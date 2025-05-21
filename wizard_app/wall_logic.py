#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Logic for calculating wall (side and end panel) components."""

try:
    from . import config
    from . import panel_logic
except ImportError:
    import config # For direct testing
    import panel_logic # For direct testing

def calculate_wall_layout(crate_internal_width: float, crate_internal_length: float, crate_internal_height: float,
                            panel_thickness: float, cleat_thickness: float, cleat_width: float,
                            wall_construction_type: str = "style_b",
                            end_panel_1_removable: bool = False,
                            end_panel_2_removable: bool = False,
                            side_panel_1_removable: bool = True,  # Default for Style B is side panel 1 removable
                            side_panel_2_removable: bool = False) -> dict:
    """Calculates wall panel and cleat layouts.
    
    Args:
        crate_internal_width: Internal width of the crate (Y-axis).
        crate_internal_length: Internal length of the crate (X-axis).
        crate_internal_height: Internal height of the crate (Z-axis), from top of floorboard to bottom of cap panel.
        panel_thickness: Thickness of the wall sheathing panels.
        cleat_thickness: Actual thickness of the cleat material.
        cleat_width: Actual width of the cleat material.
        wall_construction_type: String to select different wall construction styles ("style_b" is default for Style B crates).
        end_panel_1_removable: Whether end panel 1 (-X) is removable.
        end_panel_2_removable: Whether end panel 2 (+X) is removable.
        side_panel_1_removable: Whether side panel 1 (-Y) is removable.
        side_panel_2_removable: Whether side panel 2 (+Y) is removable.

    Returns:
        dict: {
            "side_panels": { "count": 2, "width": crate_internal_length, "height": crate_internal_height, "thickness": panel_thickness,
                             "cleats": { "vertical": [], "horizontal": [], "intermediate_vertical": [] } },
            "end_panels": { "count": 2, "width": crate_internal_width, "height": crate_internal_height, "thickness": panel_thickness,
                           "cleats": { "vertical": [], "horizontal": [], "intermediate_vertical": [] } },
            "removable_panels": { "count": n, "positions": [] },
            "exp_data": {} # Parameters for NX expression file
        }
    """
    
    # Using panel_logic to determine panel case and configuration for side panels 
    side_panel_config = panel_logic.generate_panel_config(
        width=crate_internal_length,  # Side panel width is crate length
        height=crate_internal_height,
        panel_thickness=panel_thickness,
        cleat_thickness=cleat_thickness,
        cleat_width=cleat_width
    )
    
    # Using panel_logic to determine panel case and configuration for end panels
    end_panel_config = panel_logic.generate_panel_config(
        width=crate_internal_width,   # End panel width is crate width
        height=crate_internal_height,
        panel_thickness=panel_thickness,
        cleat_thickness=cleat_thickness,
        cleat_width=cleat_width
    )
    
    # Check for error status in panel configurations
    if side_panel_config.get("status") == "ERROR" or end_panel_config.get("status") == "ERROR":
        error_message = side_panel_config.get("message", "") or end_panel_config.get("message", "")
        return {
            "status": "ERROR",
            "message": f"Panel configuration error: {error_message}",
            "side_panels": {},
            "end_panels": {},
            "removable_panels": {"count": 0, "positions": []},
            "exp_data": {}
        }
    
    # Create side panel spec using the panel_logic configuration
    side_panel_spec = {
        "count": 2,
        "panel_width_dim": crate_internal_length,  # Dimension along crate length
        "panel_height_dim": crate_internal_height,
        "thickness": panel_thickness,
        "case_id": side_panel_config.get("case_info", {}).get("case_id", ""),
        "cleats": {
            "vertical_edge_count": 2,  # Typically 2, one at each end of the panel
            "vertical_edge_length": crate_internal_height,
            "horizontal_edge_count": 2,  # Typically 2, top and bottom
            "horizontal_edge_length": crate_internal_length - (2 * cleat_thickness),  # Fit between vertical cleats
            "intermediate_vertical_cleats": [],  # Will be populated from panel_logic
            "intermediate_horizontal_cleats": []  # Will be populated from panel_logic
        },
        "panel_1_removable": side_panel_1_removable,
        "panel_2_removable": side_panel_2_removable,
        "splices": side_panel_config.get("splices", [])
    }

    # Create end panel spec using the panel_logic configuration
    end_panel_spec = {
        "count": 2,
        "panel_width_dim": crate_internal_width,  # Dimension along crate width
        "panel_height_dim": crate_internal_height,
        "thickness": panel_thickness,
        "case_id": end_panel_config.get("case_info", {}).get("case_id", ""),
        "cleats": {
            "vertical_edge_count": 2,
            "vertical_edge_length": crate_internal_height,
            "horizontal_edge_count": 2,
            "horizontal_edge_length": crate_internal_width - (2 * cleat_thickness),
            "intermediate_vertical_cleats": [],  # Will be populated from panel_logic
            "intermediate_horizontal_cleats": []  # Will be populated from panel_logic
        },
        "panel_1_removable": end_panel_1_removable,
        "panel_2_removable": end_panel_2_removable,
        "splices": end_panel_config.get("splices", [])
    }
    
    # Use panel_logic to calculate cleats instead of the helper function
    # Convert panel_logic cleat positions to our format
    def convert_cleat_positions(positions, dimension, is_vertical=True):
        """Convert cleat positions from panel_logic format to our cleat objects"""
        cleats = []
        for pos in positions:
            # Skip edge positions (0.0 and max dimension) as they're handled by edge cleats
            if pos > 0.01 and pos < (dimension - 0.01):  # Small epsilon to handle floating point
                length = crate_internal_height if is_vertical else dimension - (2 * cleat_thickness)
                cleats.append({
                    "position": pos,
                    "length": length
                })
        return cleats
    
    # Get intermediate cleats for side panels from panel_logic
    side_vert_cleats = convert_cleat_positions(
        side_panel_config.get("side_panels", {}).get("vertical_cleats", []),
        crate_internal_height,
        is_vertical=True
    )
    side_horiz_cleats = convert_cleat_positions(
        side_panel_config.get("side_panels", {}).get("horizontal_cleats", []),
        crate_internal_length,
        is_vertical=False
    )
    side_panel_spec["cleats"]["intermediate_vertical_cleats"] = side_vert_cleats
    side_panel_spec["cleats"]["intermediate_horizontal_cleats"] = side_horiz_cleats
    
    # Get intermediate cleats for end panels from panel_logic
    end_vert_cleats = convert_cleat_positions(
        end_panel_config.get("end_panels", {}).get("vertical_cleats", []),
        crate_internal_height,
        is_vertical=True
    )
    end_horiz_cleats = convert_cleat_positions(
        end_panel_config.get("end_panels", {}).get("horizontal_cleats", []),
        crate_internal_width,
        is_vertical=False
    )
    end_panel_spec["cleats"]["intermediate_vertical_cleats"] = end_vert_cleats
    end_panel_spec["cleats"]["intermediate_horizontal_cleats"] = end_horiz_cleats
    
    # Count removable panels for Style B compliance (must have at least one)
    removable_panels = []
    if side_panel_1_removable:
        removable_panels.append("side_1")
    if side_panel_2_removable:
        removable_panels.append("side_2")
    if end_panel_1_removable:
        removable_panels.append("end_1")
    if end_panel_2_removable:
        removable_panels.append("end_2")
    
    # Determine if panels need drop-end style for Style B crates
    drop_end_style = (wall_construction_type == "style_b")
    
    # Placeholder for NX Expressions related to walls
    # These will need to be carefully named to match the CAD template
    exp_data_walls = {
        "INPUT_Side_Panel_Plywood_Thickness": panel_thickness,
        "INPUT_End_Panel_Plywood_Thickness": panel_thickness,
        "INPUT_Wall_Cleat_Actual_Thickness": cleat_thickness,
        "INPUT_Wall_Cleat_Actual_Width": cleat_width,
        
        "CALC_Side_Panel_Plywood_Length": side_panel_spec["panel_width_dim"],
        "CALC_Side_Panel_Plywood_Height": side_panel_spec["panel_height_dim"],
        "CALC_End_Panel_Plywood_Width": end_panel_spec["panel_width_dim"],
        "CALC_End_Panel_Plywood_Height": end_panel_spec["panel_height_dim"],
        
        # Case ID and splice information
        "CALC_Side_Panel_Case_ID": side_panel_spec["case_id"],
        "CALC_End_Panel_Case_ID": end_panel_spec["case_id"],
        "CALC_Side_Panel_Has_Splice": 1 if side_panel_spec["splices"] else 0,
        "CALC_End_Panel_Has_Splice": 1 if end_panel_spec["splices"] else 0,
        
        # Standard panel dimensions
        "CALC_Std_Panel_Width": panel_logic.STD_PANEL_WIDTH,
        "CALC_Std_Panel_Height": panel_logic.STD_PANEL_HEIGHT,
        
        # Detail A dimensions
        "CALC_Detail_A_Dim_1": panel_logic.DETAIL_A_DIM_1,
        "CALC_Detail_A_Dim_2": panel_logic.DETAIL_A_DIM_2,
        
        # Removable panel flags for CAD templates
        "CALC_Side_Panel_1_Removable": 1 if side_panel_1_removable else 0,
        "CALC_Side_Panel_2_Removable": 1 if side_panel_2_removable else 0,
        "CALC_End_Panel_1_Removable": 1 if end_panel_1_removable else 0,
        "CALC_End_Panel_2_Removable": 1 if end_panel_2_removable else 0,
        
        # Style specific flags
        "CALC_Use_Drop_End_Style": 1 if drop_end_style else 0,
        
        # Intermediate cleat counts
        "CALC_Side_Panel_Intermediate_Vert_Cleat_Count": len(side_vert_cleats),
        "CALC_Side_Panel_Intermediate_Horiz_Cleat_Count": len(side_horiz_cleats),
        "CALC_End_Panel_Intermediate_Vert_Cleat_Count": len(end_vert_cleats),
        "CALC_End_Panel_Intermediate_Horiz_Cleat_Count": len(end_horiz_cleats),
        
        # Add expressions for cleat lengths
        "CALC_Side_Panel_Vert_Cleat_Length": side_panel_spec["cleats"]["vertical_edge_length"],
        "CALC_Side_Panel_Horiz_Cleat_Length": side_panel_spec["cleats"]["horizontal_edge_length"],
        "CALC_End_Panel_Vert_Cleat_Length": end_panel_spec["cleats"]["vertical_edge_length"],
        "CALC_End_Panel_Horiz_Cleat_Length": end_panel_spec["cleats"]["horizontal_edge_length"],
        
        # Cleat spacing rules
        "CALC_Max_Cleat_Spacing": panel_logic.MAX_CLEAT_SPACING,
        "CALC_Min_Splice_Overlap": panel_logic.MIN_SPLICE_OVERLAP,
        "CALC_Cleat_Spacing_Gap": panel_logic.CLEAT_SPACING_GAP,
        "CALC_Cleat_Splice_Clearance": panel_logic.CLEAT_SPLICE_CLEARANCE,
    }
    
    # Add positions for intermediate cleats if needed
    for i, cleat in enumerate(side_vert_cleats):
        exp_data_walls[f"CALC_Side_Panel_Int_Vert_Cleat_{i+1}_Pos"] = cleat["position"]
    
    for i, cleat in enumerate(side_horiz_cleats):
        exp_data_walls[f"CALC_Side_Panel_Int_Horiz_Cleat_{i+1}_Pos"] = cleat["position"]
        
    for i, cleat in enumerate(end_vert_cleats):
        exp_data_walls[f"CALC_End_Panel_Int_Vert_Cleat_{i+1}_Pos"] = cleat["position"]
    
    for i, cleat in enumerate(end_horiz_cleats):
        exp_data_walls[f"CALC_End_Panel_Int_Horiz_Cleat_{i+1}_Pos"] = cleat["position"]

    return {
        "side_panels": side_panel_spec,
        "end_panels": end_panel_spec,
        "removable_panels": {
            "count": len(removable_panels),
            "positions": removable_panels,
            "drop_end_style": drop_end_style
        },
        "exp_data": exp_data_walls
    }

if __name__ == '__main__':
    # Test case for Style B crate with side panel 1 removable
    wall_results = calculate_wall_layout(
        crate_internal_width=48.0,
        crate_internal_length=96.0,
        crate_internal_height=40.0,
        panel_thickness=0.75,
        cleat_thickness=0.75,
        cleat_width=3.5,
        wall_construction_type="style_b",
        side_panel_1_removable=True
    )
    import json
    print(json.dumps(wall_results, indent=2)) 