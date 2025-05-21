#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Logic for calculating cap components."""

import math

try:
    from . import config
except ImportError:
    import config # For direct testing

def _calculate_cleat_pattern(span_to_cover: float, cleat_width_for_spacing: float, 
                             max_spacing_center_to_center: float, cleat_length: float,
                             cleat_thickness_val: float, cleat_width_val: float) -> dict:
    """Helper to calculate cleat count, spacing, and positions for one direction."""
    if span_to_cover < cleat_width_for_spacing - config.FLOAT_TOLERANCE:
        return {"count": 0, "actual_spacing_centers": 0, "positions_from_center": [], "length": cleat_length, "thickness": cleat_thickness_val, "width": cleat_width_val}
    
    if span_to_cover < (2 * cleat_width_for_spacing) - config.FLOAT_TOLERANCE or max_spacing_center_to_center <= config.FLOAT_TOLERANCE:
        # If span is too small for 2 cleats with any positive spacing, or if max_spacing is invalid, place 1 cleat if span allows
        # Or, if the CAD template expects at least two end cleats, this logic needs adjustment.
        # The CAD guide for Cap shows "pattern features for cleats", implying multiple.
        # For now, let's assume if span can fit one cleat, it gets one. If it can fit two, it gets two (ends).
        if span_to_cover >= cleat_width_for_spacing:
            count = 1
            actual_spacing_centers = 0
            positions = [0.0] # Centered
            # If 2 are always required for ends if span_to_cover allows them:
            if span_to_cover >= (2 * cleat_width_for_spacing) - config.FLOAT_TOLERANCE:
                 count = 2
                 actual_spacing_centers = span_to_cover - cleat_width_for_spacing # Center to center for 2 end cleats
                 positions = [-actual_spacing_centers/2.0, actual_spacing_centers/2.0]
            return {"count": count, "actual_spacing_centers": actual_spacing_centers, "positions_from_center": positions, "length": cleat_length, "thickness": cleat_thickness_val, "width": cleat_width_val}
        else:
            return {"count": 0, "actual_spacing_centers": 0, "positions_from_center": [], "length": cleat_length, "thickness": cleat_thickness_val, "width": cleat_width_val}
            
    # General case: span_to_cover allows for at least 2 cleats with potential for intermediates.
    # The span for placing cleat centers is (span_to_cover - cleat_width_for_spacing) for end-to-end cleats.
    centerline_span_for_pattern = span_to_cover - cleat_width_for_spacing 
    num_gaps_ideal = centerline_span_for_pattern / max_spacing_center_to_center
    cleat_count = math.ceil(num_gaps_ideal) + 1
    cleat_count = max(2, cleat_count) # Ensure at least 2 (end cleats)

    actual_spacing_centers = centerline_span_for_pattern / (cleat_count - 1) if cleat_count > 1 else 0
    
    positions = []
    start_pos = -centerline_span_for_pattern / 2.0
    for i in range(cleat_count):
        positions.append(round(start_pos + i * actual_spacing_centers, 4))
        
    return {"count": cleat_count, "actual_spacing_centers": actual_spacing_centers, "positions_from_center": positions, "length": cleat_length, "thickness": cleat_thickness_val, "width": cleat_width_val}

def calculate_cap_layout(crate_overall_width_y: float, crate_overall_length_x: float, 
                         cap_panel_sheathing_thickness: float, 
                         cap_cleat_actual_thickness: float,
                         cap_cleat_actual_width: float,
                         max_top_cleat_spacing: float,
                         top_panel_removable: bool = False,
                         construction_style: str = "style_b") -> dict:
    """Calculates cap layout based on crate and construction parameters.
       Returns exp_data suitable for NX expression file.
       
    Args:
        crate_overall_width_y: Overall width of the crate (Y dimension).
        crate_overall_length_x: Overall length of the crate (X dimension).
        cap_panel_sheathing_thickness: Thickness of the cap panel plywood.
        cap_cleat_actual_thickness: Actual thickness of the cap cleats.
        cap_cleat_actual_width: Actual width of the cap cleats.
        max_top_cleat_spacing: Maximum allowed spacing between cleats, center to center.
        top_panel_removable: Whether the top panel is removable.
        construction_style: Style of crate construction ("style_b" default for Style B crates).
    """
    
    # Cap Panel Dimensions
    cap_panel_width_y = crate_overall_width_y
    cap_panel_length_x = crate_overall_length_x
    
    # For Style B crates (according to the specification)
    # Calculate panel area to determine if lag frames or klimps are needed
    panel_area_sqft = (cap_panel_width_y * cap_panel_length_x) / 144.0  # Convert sq inches to sq feet
    
    # According to Style B document, if panel area > 64 sq ft, use lag screws
    # Otherwise, use klimps (or a combination)
    use_lag_screws = panel_area_sqft > 64.0
    use_klimps = not use_lag_screws or panel_area_sqft <= 64.0  # Can use klimps alone or with lag screws
    
    # For Style B crates, if top panel width <= 30", lag frames or panel stops are not required
    small_top_panel_exemption = False
    if construction_style == "style_b" and top_panel_removable:
        if cap_panel_width_y <= 30.0 or cap_panel_length_x <= 30.0:
            small_top_panel_exemption = True
    
    # Determine fastener count and spacing based on Style B document (18"-24" on center)
    # For now, use average spacing of 21"
    fastener_spacing = 21.0
    
    # Longitudinal Cleats (run along crate_overall_length_x, spaced across crate_overall_width_y)
    long_cleats = _calculate_cleat_pattern(
        span_to_cover=crate_overall_width_y, 
        cleat_width_for_spacing=cap_cleat_actual_width, 
        max_spacing_center_to_center=max_top_cleat_spacing, 
        cleat_length=crate_overall_length_x,
        cleat_thickness_val=cap_cleat_actual_thickness,
        cleat_width_val=cap_cleat_actual_width
    )

    # Transverse Cleats (run along crate_overall_width_y, spaced across crate_overall_length_x)
    trans_cleats = _calculate_cleat_pattern(
        span_to_cover=crate_overall_length_x, 
        cleat_width_for_spacing=cap_cleat_actual_width, 
        max_spacing_center_to_center=max_top_cleat_spacing,
        cleat_length=crate_overall_width_y,
        cleat_thickness_val=cap_cleat_actual_thickness,
        cleat_width_val=cap_cleat_actual_width
    )
    
    # Calculate fastener requirements for removable top panel if applicable
    fastener_data = {
        "required": top_panel_removable,
        "exemption_applies": small_top_panel_exemption,
        "klimps_required": use_klimps and top_panel_removable,
        "lag_screws_required": use_lag_screws and top_panel_removable,
        "perimeter": 2 * (cap_panel_width_y + cap_panel_length_x),
        "fastener_spacing": fastener_spacing
    }
    
    # Calculate klimp count if needed (perimeter / spacing, rounded up)
    if fastener_data["klimps_required"]:
        fastener_data["klimp_count"] = math.ceil(fastener_data["perimeter"] / fastener_spacing)
    else:
        fastener_data["klimp_count"] = 0
        
    # Calculate lag screw count if needed
    if fastener_data["lag_screws_required"]:
        fastener_data["lag_screw_count"] = math.ceil(fastener_data["perimeter"] / fastener_spacing)
    else:
        fastener_data["lag_screw_count"] = 0
    
    # NX Expression Data
    exp_data_cap = {
        "INPUT_Cap_Panel_Plywood_Thickness": cap_panel_sheathing_thickness,
        "CALC_Cap_Panel_Actual_Length_X": cap_panel_length_x,
        "CALC_Cap_Panel_Actual_Width_Y": cap_panel_width_y,
        
        "INPUT_Cap_Cleat_Actual_Thickness": cap_cleat_actual_thickness,
        "INPUT_Cap_Cleat_Actual_Width": cap_cleat_actual_width,
        
        "CALC_Cap_Top_Panel_Removable": 1 if top_panel_removable else 0,
        "CALC_Cap_Small_Top_Exemption": 1 if small_top_panel_exemption else 0,
        "CALC_Cap_Panel_Area_SqFt": panel_area_sqft,
        "CALC_Cap_Use_Klimps": 1 if fastener_data["klimps_required"] else 0,
        "CALC_Cap_Use_Lag_Screws": 1 if fastener_data["lag_screws_required"] else 0,
        "CALC_Cap_Klimp_Count": fastener_data["klimp_count"],
        "CALC_Cap_Lag_Screw_Count": fastener_data["lag_screw_count"],
        "CALC_Cap_Fastener_Spacing": fastener_data["fastener_spacing"],
        
        # Longitudinal Cleats (Patterned along Y, length in X)
        "CALC_Cap_Long_Cleat_Actual_Length_X": long_cleats["length"],
        "CALC_Cap_Long_Cleat_Count_Y": long_cleats["count"],
        "CALC_Cap_Long_Cleat_Pitch_Y": long_cleats["actual_spacing_centers"],
        # Position of the first long cleat (center Y) relative to cap panel center Y
        "CALC_Cap_Long_Cleat_First_Pos_Y": long_cleats["positions_from_center"][0] if long_cleats["count"] > 0 else 0,
        "CALC_Cap_Long_Cleat_Suppress_Flag": 1 if long_cleats["count"] == 0 else 0, # Suppress pattern if no cleats

        # Transverse Cleats (Patterned along X, length in Y)
        "CALC_Cap_Trans_Cleat_Actual_Length_Y": trans_cleats["length"],
        "CALC_Cap_Trans_Cleat_Count_X": trans_cleats["count"],
        "CALC_Cap_Trans_Cleat_Pitch_X": trans_cleats["actual_spacing_centers"],
        # Position of the first trans cleat (center X) relative to cap panel center X
        "CALC_Cap_Trans_Cleat_First_Pos_X": trans_cleats["positions_from_center"][0] if trans_cleats["count"] > 0 else 0,
        "CALC_Cap_Trans_Cleat_Suppress_Flag": 1 if trans_cleats["count"] == 0 else 0, # Suppress pattern if no cleats
    }

    return {
        "cap_panel": {
            "width": cap_panel_width_y, 
            "length": cap_panel_length_x, 
            "thickness": cap_panel_sheathing_thickness,
            "removable": top_panel_removable
        },
        "longitudinal_cleats": long_cleats,
        "transverse_cleats": trans_cleats,
        "fasteners": fastener_data,
        "exp_data": exp_data_cap
    }

if __name__ == '__main__':
    try: from . import config
    except ImportError: import config
    import json

    print("--- Cap Logic Test Cases ---")
    
    # Standard Style B cap test
    cap_results1 = calculate_cap_layout(
        crate_overall_width_y=50.0,
        crate_overall_length_x=100.0,
        cap_panel_sheathing_thickness=0.75,
        cap_cleat_actual_thickness=0.75,
        cap_cleat_actual_width=3.5,
        max_top_cleat_spacing=24.0,
        top_panel_removable=False,
        construction_style="style_b"
    )
    print(f"\nCap Results 1 (Standard Style B):\n{json.dumps(cap_results1, indent=2)}")
    assert cap_results1["longitudinal_cleats"]["count"] == 3
    assert cap_results1["transverse_cleats"]["count"] == 5

    # Test with removable top panel
    cap_results2 = calculate_cap_layout(
        crate_overall_width_y=50.0,
        crate_overall_length_x=100.0,
        cap_panel_sheathing_thickness=0.75,
        cap_cleat_actual_thickness=0.75,
        cap_cleat_actual_width=3.5,
        max_top_cleat_spacing=24.0,
        top_panel_removable=True,
        construction_style="style_b"
    )
    print(f"\nCap Results 2 (Style B with Removable Top):\n{json.dumps(cap_results2, indent=2)}")
    assert cap_results2["fasteners"]["required"] == True
    assert cap_results2["fasteners"]["lag_screws_required"] == True  # Area > 64 sq ft
    
    # Test with small removable top panel (exemption case)
    cap_results3 = calculate_cap_layout(
        crate_overall_width_y=28.0,  # <= 30", should qualify for exemption
        crate_overall_length_x=60.0,
        cap_panel_sheathing_thickness=0.25,  # Minimum per Style B doc
        cap_cleat_actual_thickness=0.75,
        cap_cleat_actual_width=3.5,
        max_top_cleat_spacing=24.0,
        top_panel_removable=True,
        construction_style="style_b"
    )
    print(f"\nCap Results 3 (Style B with Small Removable Top - Exemption):\n{json.dumps(cap_results3, indent=2)}")
    assert cap_results3["fasteners"]["exemption_applies"] == True
    
    # Test based on BOM document (0205-13058)
    cap_results4 = calculate_cap_layout(
        crate_overall_width_y=40.0,  # From BOM doc
        crate_overall_length_x=48.0,  # From BOM doc
        cap_panel_sheathing_thickness=0.25,  # From BOM doc (.25 IN PLYWOOD)
        cap_cleat_actual_thickness=0.75,
        cap_cleat_actual_width=3.5,
        max_top_cleat_spacing=24.0,
        top_panel_removable=False,  # Per BOM doc - using Klimps but not for removable top
        construction_style="style_b"
    )
    print(f"\nCap Results 4 (Based on BOM doc 0205-13058):\n{json.dumps(cap_results4, indent=2)}") 