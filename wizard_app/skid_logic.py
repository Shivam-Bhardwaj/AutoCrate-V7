# wizard_app/skid_logic.py
# Version: Updated to include allow_3x4_skids_for_light_loads parameter
"""
Core logic for calculating skid layout for industrial shipping crates
based on specified shipping standards.
Imports constants from config.py
"""

import math
import logging
from typing import Dict, List, Union, Any # Added Any

# Import from config
# This needs to work whether run directly or as part of a package
try:
    from . import config # Relative import for when skid_logic is part of wizard_app package
except ImportError:
    try:
        import config # Direct import for testing or if wizard_app is in PYTHONPATH
    except ImportError:
        log = logging.getLogger(__name__)
        log.critical("CRITICAL: config.py not found. Skid logic cannot function.")
        # Define minimal fallbacks if config is absolutely missing, though this is not ideal
        class ConfigFallback:
            FLOAT_TOLERANCE = 1e-6
            WEIGHT_RULES = [(500, "3x4", 30.0), (4500, "4x4", 30.0), (20000, "4x6", 24.0)] # Simplified
            SKID_DIMENSIONS = {"3x4": (2.5, 3.5), "4x4": (3.5, 3.5), "4x6": (5.5, 3.5)}
            MIN_SKID_HEIGHT = 3.5
        config = ConfigFallback()


# Configure logging
log = logging.getLogger(__name__) 

def calculate_skid_layout(
    product_weight: float,
    product_width: float,
    clearance_side: float,
    panel_thickness: float,
    cleat_thickness: float, # This is the framing cleat thickness for side/end walls
    allow_3x4_skids_for_light_loads: bool = True # NEW PARAMETER
) -> Dict[str, Any]:
    """
    Calculates skid layout based on product weight and dimensions per shipping standards.

    Args:
        product_weight: Weight of the product in lbs.
        product_width: Width of the product in inches.
        clearance_side: Clearance space on each side of the product in inches.
        panel_thickness: Thickness of the crate side panels in inches.
        cleat_thickness: Thickness of the crate side/end wall framing cleats in inches.
        allow_3x4_skids_for_light_loads: If True, allows 3x4 skids for applicable light loads.
                                         If False, 3x4 skids will be skipped even if weight rules allow.

    Returns:
        A dictionary containing skid layout parameters or an error status.
    """
    result = {
        "skid_type": None, "skid_width": None, "skid_height": None,
        "skid_count": 0, "spacing_actual": 0.0, "max_spacing": None,
        "crate_width": 0.0, "usable_width": 0.0, "skid_positions": [],
        "status": "INIT", "message": "Calculation not started."
    }

    # --- Input Validation ---
    if not isinstance(product_weight, (int, float)) or product_weight < 0:
        result["status"] = "ERROR"; result["message"] = "Product weight must be a non-negative number."
        log.error(result["message"]); return result
    if not isinstance(product_width, (int, float)) or product_width <= config.FLOAT_TOLERANCE:
        result["status"] = "ERROR"; result["message"] = "Product width must be a positive number."
        log.error(result["message"]); return result
    # ... (add more robust type checks for other inputs if necessary) ...

    log.info(f"Calculating skid layout: Weight={product_weight:.2f} lbs, ProdW={product_width:.2f}\", Allow3x4={allow_3x4_skids_for_light_loads}")

    # --- Handle Overweight Case ---
    if not config.WEIGHT_RULES: # Safety check if config didn't load properly
        result["status"] = "ERROR"; result["message"] = "Weight rules not loaded from config."
        log.error(result["message"]); return result
        
    if product_weight > config.WEIGHT_RULES[-1][0] + config.FLOAT_TOLERANCE: 
        result["status"] = "OVER"
        result["message"] = f"Weight ({product_weight:.0f} lbs) exceeds {config.WEIGHT_RULES[-1][0]:.0f} lbs limit."
        log.warning(result["message"]); return result

    # --- Determine Skid Type, Width, Height, and Max Spacing ---
    skid_type_nominal = None
    max_spacing = None
    skid_width = 0.0
    skid_height = 0.0

    # Iterate through weight rules to find the first applicable one
    for rule_max_weight, type_from_rule, rule_max_spacing in config.WEIGHT_RULES:
        if product_weight <= rule_max_weight + config.FLOAT_TOLERANCE:
            if type_from_rule == "3x4" and not allow_3x4_skids_for_light_loads:
                log.info(f"Product weight ({product_weight} lbs) qualifies for 3x4 skids, but option is disabled. Seeking next rule.")
                continue # Skip this "3x4" rule and check the next one
            
            skid_type_nominal = type_from_rule
            max_spacing = rule_max_spacing
            log.info(f"Selected rule: Weight <= {rule_max_weight}, Type = {skid_type_nominal}, Max Spacing = {max_spacing}")
            break # Found the first applicable rule

    if skid_type_nominal is None:
        # This could happen if all applicable rules were 3x4 and they were disallowed.
        # Fallback: Re-iterate without the 3x4 constraint to find the next best (likely 4x4).
        log.warning(f"Initial rule selection yielded no skid type (possibly due to 3x4 restriction). Attempting fallback.")
        for rule_max_weight, type_from_rule, rule_max_spacing in config.WEIGHT_RULES:
            if product_weight <= rule_max_weight + config.FLOAT_TOLERANCE:
                if type_from_rule == "3x4": # Explicitly skip 3x4 in this fallback pass if it was the issue
                    continue
                skid_type_nominal = type_from_rule
                max_spacing = rule_max_spacing
                log.info(f"Fallback rule selected: Weight <= {rule_max_weight}, Type = {skid_type_nominal}, Max Spacing = {max_spacing}")
                break
        if skid_type_nominal is None: # Still no type found
            result["status"] = "ERROR"; result["message"] = f"Could not determine skid type for weight {product_weight:.0f} lbs with current rules and 3x4 allowance."
            log.error(result["message"]); return result


    if not config.SKID_DIMENSIONS: # Safety check
        result["status"] = "ERROR"; result["message"] = "Skid dimensions not loaded from config."
        log.error(result["message"]); return result

    try:
        skid_width, skid_height = config.SKID_DIMENSIONS[skid_type_nominal]
    except KeyError:
        result["status"] = "ERROR"; result["message"] = f"Dimensions for skid type '{skid_type_nominal}' not found in config."
        log.error(result["message"]); return result

    result.update({"skid_type": skid_type_nominal, "skid_width": skid_width,
                   "skid_height": skid_height, "max_spacing": max_spacing})
    log.info(f"Selected Skid: {skid_type_nominal}, W={skid_width}\", H={skid_height}\", Max Spacing={max_spacing}\"")

    if skid_height < config.MIN_SKID_HEIGHT - config.FLOAT_TOLERANCE:
         result["status"] = "ERROR"; result["message"] = f"Skid height ({skid_height}\") < min required ({config.MIN_SKID_HEIGHT}\")."
         log.error(result["message"]); return result

    # --- Calculate Crate and Usable Width ---
    crate_width_calculated = product_width + 2 * (clearance_side + panel_thickness + cleat_thickness)
    usable_width_for_skids = crate_width_calculated - 2 * (panel_thickness + cleat_thickness)

    result.update({"crate_width": crate_width_calculated, "usable_width": usable_width_for_skids})
    log.info(f"Crate Width: {crate_width_calculated:.2f}\", Usable Width (for skids): {usable_width_for_skids:.2f}\"")

    # --- Determine Skid Count and Spacing ---
    if usable_width_for_skids < skid_width - config.FLOAT_TOLERANCE:
        result["status"] = "ERROR"
        result["message"] = f"Usable width for skids ({usable_width_for_skids:.2f}\") is too narrow for skid width ({skid_width:.2f}\")."
        log.error(result["message"]); return result

    skid_count = 0
    spacing_actual = 0.0

    if usable_width_for_skids < (skid_width * 2) - config.FLOAT_TOLERANCE:
        skid_count = 1
        spacing_actual = 0.0
        log.info("Usable width allows only one skid.")
    else:
        centerline_span = usable_width_for_skids - skid_width
        log.debug(f"Centerline span available for skids: {centerline_span:.2f}\"")

        if centerline_span < config.FLOAT_TOLERANCE: 
            skid_count = 2
            spacing_actual = centerline_span 
            log.info(f"Centerline span ({centerline_span:.2f}) very small, placing 2 skids with spacing {spacing_actual:.2f}\"")
        else:
            if max_spacing <= config.FLOAT_TOLERANCE: # Should not happen if a valid rule was chosen
                log.error(f"Max spacing rule is {max_spacing}, which is invalid for calculation. Defaulting to 2 skids if possible.")
                skid_count = 2 # Fallback
            else:
                num_skids_calculated = math.ceil( (centerline_span / max_spacing) + 1 )
                skid_count = max(2, int(num_skids_calculated))
                log.debug(f"Calculated initial skid count: {skid_count} (from theoretical min {num_skids_calculated})")

            if skid_count <=1 : 
                result["status"] = "ERROR"; result["message"] = "Internal error: skid_count became <= 1 unexpectedly."
                log.error(result["message"]); return result

            spacing_actual = centerline_span / (skid_count - 1)

    result.update({"skid_count": skid_count, "spacing_actual": spacing_actual if skid_count > 1 else 0.0})
    log.info(f"Final Skid Count: {skid_count}, Actual Spacing: {result['spacing_actual']:.3f}\"")

    # --- Calculate Skid Positions (relative to center of usable_width_for_skids) ---
    skid_positions = []
    if skid_count == 1:
        skid_positions = [0.0] 
    elif skid_count > 1:
        total_centerline_span_actual = spacing_actual * (skid_count - 1)
        start_x = -total_centerline_span_actual / 2.0
        log.debug(f"Calculated actual centerline span for positions: {total_centerline_span_actual:.4f}\"")
        log.debug(f"First skid center (start_x): {start_x:.4f}\"")
        for i in range(skid_count):
            position = start_x + i * spacing_actual
            skid_positions.append(round(position, 4))

    result["skid_positions"] = skid_positions
    log.info(f"Skid Positions (Centerlines rel to usable width center): {['%.3f' % p for p in skid_positions]}")

    if skid_count > 0 and result["status"] not in ["ERROR", "OVER"]:
        result["status"] = "OK"; result["message"] = "Skid layout calculated successfully."
        log.info(result["message"])
    elif result["status"] == "INIT": 
        result["status"] = "ERROR"; result["message"] = "Calculation finished without a final status."
        log.error(result["message"])
    return result

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG) # Ensure logs are visible for testing
    
    # Test Case 1: Light load, 3x4 allowed
    params1 = {
        "product_weight": 300, "product_width": 40, "clearance_side": 2,
        "panel_thickness": 0.75, "cleat_thickness": 0.75,
        "allow_3x4_skids_for_light_loads": True
    }
    print(f"\n--- Test Case 1: Light load, 3x4 ALLOWED ---")
    results1 = calculate_skid_layout(**params1)
    print(json.dumps(results1, indent=2))
    assert results1["skid_type"] == "3x4"

    # Test Case 2: Light load, 3x4 NOT allowed
    params2 = {
        "product_weight": 300, "product_width": 40, "clearance_side": 2,
        "panel_thickness": 0.75, "cleat_thickness": 0.75,
        "allow_3x4_skids_for_light_loads": False
    }
    print(f"\n--- Test Case 2: Light load, 3x4 DISALLOWED ---")
    results2 = calculate_skid_layout(**params2)
    print(json.dumps(results2, indent=2))
    assert results2["skid_type"] == "4x4" # Should default to next rule

    # Test Case 3: Heavier load where 3x4 wouldn't apply anyway
    params3 = {
        "product_weight": 1000, "product_width": 60, "clearance_side": 2,
        "panel_thickness": 0.75, "cleat_thickness": 0.75,
        "allow_3x4_skids_for_light_loads": False # This flag shouldn't matter here
    }
    print(f"\n--- Test Case 3: Heavier load ---")
    results3 = calculate_skid_layout(**params3)
    print(json.dumps(results3, indent=2))
    assert results3["skid_type"] == "4x4"
