#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Logic for calculating skid components."""

import math

try:
    from . import config 
except ImportError:
    import config # For direct testing, if config.py is in the same directory or PYTHONPATH

def calculate_skid_layout(product_weight: float, product_width: float, product_length: float, 
                            clearance_side: float, panel_thickness: float, cleat_thickness: float, 
                            allow_3x4_skids_for_light_loads: bool = True) -> dict:
    """Calculates skid layout based on product and construction parameters.
    Returns a dictionary including specific keys for NX expression file.
    """
    
    # --- Determine Skid Type, Actual Dimensions, and Max Spacing from Rules ---
    skid_type_nominal = None
    skid_actual_width = 0.0
    skid_actual_height = 0.0
    max_skid_spacing_rule = 0.0

    # Sort rules by weight to handle cases correctly
    sorted_weight_rules = sorted(config.WEIGHT_RULES, key=lambda x: x[0])

    for rule_max_weight, type_from_rule, rule_max_spacing in sorted_weight_rules:
        if product_weight <= rule_max_weight + config.FLOAT_TOLERANCE:
            if type_from_rule == "3x4" and not allow_3x4_skids_for_light_loads:
                continue # Skip 3x4 if not allowed
            skid_type_nominal = type_from_rule
            max_skid_spacing_rule = rule_max_spacing
            break
    
    if not skid_type_nominal: # Fallback if 3x4 was skipped and no other rule matched (e.g. product too light for next rule)
        # Find first rule that isn't 3x4 or use the lightest rule if all are 3x4 and it was disallowed
        for rule_max_weight, type_from_rule, rule_max_spacing in sorted_weight_rules:
            if type_from_rule != "3x4":
                 if product_weight <= rule_max_weight + config.FLOAT_TOLERANCE:
                    skid_type_nominal = type_from_rule
                    max_skid_spacing_rule = rule_max_spacing
                    break
        if not skid_type_nominal and sorted_weight_rules: # Still no type, product is very light and 3x4 disallowed.
             # Default to the first rule in the list if any (could be 3x4 if that's the only one)
             # Or handle as an error / specific light-load case
            skid_type_nominal = sorted_weight_rules[0][1]
            max_skid_spacing_rule = sorted_weight_rules[0][2]
            # Potentially log a warning that 3x4 was disallowed and a specific rule was forced.

    if skid_type_nominal and skid_type_nominal in config.SKID_DIMENSIONS:
        skid_actual_width, skid_actual_height = config.SKID_DIMENSIONS[skid_type_nominal]
    else:
        # Handle error: skid type not found or not defined in SKID_DIMENSIONS
        # For now, use placeholder values if not found, but ideally, this should be an error or a safe default
        skid_actual_width, skid_actual_height = (3.5, 3.5) # Default to 4x4 actuals
        skid_type_nominal = "4x4" if not skid_type_nominal else skid_type_nominal
        max_skid_spacing_rule = 30.0 # Default spacing
        # Log error here

    # --- Calculate Crate Dimensions ---
    # Overall Crate Width (External) - This definition might vary based on construction style
    # Assuming product_width is the content, and clearances/walls are added externally to that.
    crate_overall_width = product_width + (2 * clearance_side) + (2 * panel_thickness) + (2 * cleat_thickness)
    
    # Usable width for skids (Internal span between innermost wall cleats/panels)
    # This depends on where skids are relative to walls. Assuming skids are inside the main wall cleats.
    usable_width_for_skids = product_width + (2 * clearance_side) # This is effectively the internal span of the crate content area
                                          # If skids support the floor directly, it could be crate_overall_width - 2*(panel_thickness + cleat_thickness)
                                          # For now, assume skids are placed under the product + clearance area only.

    # --- Skid Count and Spacing ---
    skid_count = 0
    actual_skid_center_to_center_spacing = 0.0 # CALC_Skid_Pitch in CAD guide
    first_skid_pos_x_offset = 0 # CALC_First_Skid_Pos_X in CAD guide (relative to crate center or edge)

    if usable_width_for_skids < skid_actual_width - config.FLOAT_TOLERANCE:
        skid_count = 0 # Not enough space for even one skid (error condition)
    elif usable_width_for_skids < (2 * skid_actual_width) - config.FLOAT_TOLERANCE or max_skid_spacing_rule == 0:
        skid_count = 1 if usable_width_for_skids >= skid_actual_width else 0
        if skid_count == 1:
            actual_skid_center_to_center_spacing = 0 # Only one skid
            # Position it in the center of the usable_width_for_skids
            first_skid_pos_x_offset = 0 # Relative to center of usable_width_for_skids
    else:
        # Calculate number of skids based on max_spacing_rule
        # Number of GAPS is (usable_width_for_skids - skid_actual_width) / max_skid_spacing_rule
        # Number of SKIDS is number of GAPS + 1
        num_gaps_ideal = (usable_width_for_skids - skid_actual_width) / max_skid_spacing_rule
        skid_count = math.ceil(num_gaps_ideal) + 1
        skid_count = max(2, skid_count) # Ensure at least 2 skids if we are in this else block

        if skid_count > 1:
            actual_skid_center_to_center_spacing = (usable_width_for_skids - skid_actual_width) / (skid_count - 1)
        else: # Should not happen if skid_count is max(2, ...)
            actual_skid_center_to_center_spacing = 0

    # Position of the first skid (CALC_First_Skid_Pos_X)
    # The CAD guide implies X is the direction of patterning, which is along the crate width here.
    # If 0 is the center of the crate_overall_width:
    # total_skid_span = (skid_count -1) * actual_skid_center_to_center_spacing
    # first_skid_pos_x_offset = -total_skid_span / 2.0
    # OR, if it's from an edge (e.g. min X edge of the usable_width_for_skids area):
    # Assuming 0 is center of crate_overall_width for now.
    # The `usable_width_for_skids` is centered. The skids are patterned within this.
    # The first skid's center is at -( (skid_count-1) * spacing ) / 2 + ( (skid_count-1)*spacing - (skid_count * skid_actual_width) ) /2 ... complex
    # Simpler: total span covered by skids from center of first to center of last is (skid_count-1)*actual_skid_center_to_center_spacing
    # The first skid is at one end of this span.
    
    # Position of the center of the first skid relative to the center of `usable_width_for_skids`
    if skid_count > 0 : 
        total_pattern_width_centers = (skid_count - 1) * actual_skid_center_to_center_spacing
        first_skid_pos_x_offset = -total_pattern_width_centers / 2.0
    else:
        first_skid_pos_x_offset = 0 # No skids, no offset

    # Skid Length (CALC_Skid_Actual_Length or INPUT_Skid_Actual_Length)
    # Based on config.SKID_LENGTH_ASSUMPTION
    skid_actual_length = 0
    if config.SKID_LENGTH_ASSUMPTION == "crate_overall_length":
        # Crate overall length (External)
        skid_actual_length = product_length + (2 * clearance_side) + (2 * panel_thickness) + (2 * cleat_thickness)
    elif config.SKID_LENGTH_ASSUMPTION == "product_length":
        skid_actual_length = product_length
    # Add other assumptions if necessary
    
    # --- NX Expression Data --- 
    exp_data = {
        "INPUT_Skid_Nominal_Width": skid_actual_width, # From guide: INPUT_Skid_Width linked to INPUT_Skid_Nominal_Width
        "INPUT_Skid_Nominal_Height": skid_actual_height, # From guide: INPUT_Skid_Height linked to INPUT_Skid_Nominal_Height
        "INPUT_Skid_Actual_Length": skid_actual_length, # From guide: INPUT_Skid_Length linked to INPUT_Skid_Actual_Length
        
        "CALC_Skid_Count": skid_count,
        "CALC_Skid_Pitch": actual_skid_center_to_center_spacing, # This is the 'Pitch' for linear pattern
        "CALC_First_Skid_Pos_X": first_skid_pos_x_offset, # Position of the first skid for patterning
                                                        # This needs to align with NX template's origin for skids

        # Reference values (optional, for traceability in .exp)
        "REF_Product_Weight": product_weight,
        "REF_Product_Width_for_Skid_Calc": product_width,
        "REF_Skid_Type_Nominal": skid_type_nominal,
        "REF_Max_Skid_Spacing_Rule": max_skid_spacing_rule,
        "REF_Crate_Overall_Width_for_Skid_Calc": crate_overall_width,
        "REF_Usable_Width_for_Skids": usable_width_for_skids
    }

    return {
        "skid_type_nominal": skid_type_nominal,
        "skid_actual_width": skid_actual_width,
        "skid_actual_height": skid_actual_height,
        "skid_actual_length": skid_actual_length,
        "skid_count": skid_count,
        "actual_center_to_center_spacing": actual_skid_center_to_center_spacing,
        "first_skid_position_offset_x": first_skid_pos_x_offset, # Relative to center of usable span for skids
        "crate_overall_width_calculated": crate_overall_width, 
        "exp_data": exp_data
    }

if __name__ == '__main__':
    # Test cases from cad_implementation_guide.html (Skid configurations)
    # Assuming config.py is accessible
    try: from . import config
    except ImportError: import config
    import json

    print("--- Skid Test Cases ---")
    test_params_shared = {
        "product_length": 100.0, # Length for skid length calculation
        "clearance_side": 2.0,
        "panel_thickness": 0.75,
        "cleat_thickness": 0.75,
        "allow_3x4_skids_for_light_loads": True
    }

    # Test 1: Light load, 3x4 skids
    params1 = {"product_weight": 300, "product_width": 40, **test_params_shared}
    results1 = calculate_skid_layout(**params1)
    print(f"\nTest 1 (Light Load, 3x4 Expected):\n{json.dumps(results1, indent=2)}")
    assert results1["skid_type_nominal"] == "3x4"

    # Test 2: Medium load, 4x4 skids
    params2 = {"product_weight": 1000, "product_width": 60, **test_params_shared}
    results2 = calculate_skid_layout(**params2)
    print(f"\nTest 2 (Medium Load, 4x4 Expected):\n{json.dumps(results2, indent=2)}")
    assert results2["skid_type_nominal"] == "4x4"

    # Test 3: Heavy load, 4x6 skids
    params3 = {"product_weight": 7000, "product_width": 70, **test_params_shared}
    results3 = calculate_skid_layout(**params3)
    print(f"\nTest 3 (Heavy Load, 4x6 Expected):\n{json.dumps(results3, indent=2)}")
    assert results3["skid_type_nominal"] == "4x6"
    
    # Test 4: Light load, 3x4 skids DISALLOWED
    params4 = {"product_weight": 300, "product_width": 40, **test_params_shared,
               "allow_3x4_skids_for_light_loads": False}
    results4 = calculate_skid_layout(**params4)
    print(f"\nTest 4 (Light Load, 3x4 Disallowed, 4x4 Expected):\n{json.dumps(results4, indent=2)}")
    assert results4["skid_type_nominal"] == "4x4" # Should default to next rule

    # Test 5: Very narrow product, potentially 1 skid
    params5 = {"product_weight": 300, "product_width": 5, **test_params_shared}
    results5 = calculate_skid_layout(**params5)
    print(f"\nTest 5 (Narrow Product, 1 Skid Expected):\n{json.dumps(results5, indent=2)}")
    assert results5["skid_count"] == 1

    # Test 6: Product width just enough for two skids min separation
    params6 = {"product_weight": 300, "product_width": 8, **test_params_shared, "allow_3x4_skids_for_light_loads":True }
    results6 = calculate_skid_layout(**params6)
    print(f"\nTest 6 (Product for 2 skids - 3x4 allowed):\n{json.dumps(results6, indent=2)}")
    # This assertion depends on exact skid width (2.5 for 3x4) and usable width calc.
    # If usable width = 8 + 2*2 = 12. (12 - 2.5) / (spacing_max=30) => ceil(9.5/30)=1 gap. 1+1=2 skids.
    assert results6["skid_count"] == 2 