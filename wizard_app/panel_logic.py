#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Panel configuration logic for AutoCrate based on standardized rules.
Implements the case-based logic for panel sizes and splice configurations.
"""

try:
    from . import config
except ImportError:
    import config # For direct testing

# --- Constants for Standard Panel Design Rules ---
MAX_WIDTH = 96.0  # Maximum allowable width (front face) in inches
MAX_HEIGHT = 116.0  # Maximum allowable height in inches
MAX_LENGTH = 125.0  # Maximum allowable length in inches

# Standard panel sizes
STD_PANEL_WIDTH = 48.0  # Standard panel width
STD_PANEL_HEIGHT = 96.0  # Standard panel height

# Splice rules
MIN_SPLICE_OVERLAP = 1.5  # Minimum splice overlap in inches
CLEAT_SPLICE_CLEARANCE = 1.5  # Required clearance from any cleat edge for a splice
MAX_CLEAT_SPACING = 24.0  # Maximum spacing between cleats (on center)
CLEAT_SPACING_GAP = 0.75  # Required gap between cleats

# Detail A standard dimensions
DETAIL_A_DIM_1 = 0.25  # Standard dimension 1 for DETAIL A in splice construction
DETAIL_A_DIM_2 = 0.75  # Standard dimension 2 for DETAIL A in splice construction

def determine_panel_case(width, height):
    """
    Determines which case applies based on input width and height.
    
    Args:
        width: Width of the autocrate front face (inches)
        height: Height of the autocrate front face (inches)
        
    Returns:
        dict: Case details including case_id and construction approach
    """
    # Validate against maximum dimensions
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        return {
            "case_id": "OVERSIZE",
            "status": "ERROR",
            "message": f"Dimensions exceed maximum allowable: Width={width} (max {MAX_WIDTH}), Height={height} (max {MAX_HEIGHT})"
        }
    
    # Handle cases where Height ≤ 96 inches (Cases 1-7)
    if height <= STD_PANEL_HEIGHT:
        if width <= STD_PANEL_WIDTH:
            return {
                "case_id": "Case 1",
                "status": "OK",
                "front_face_strategy": "Single Panel",
                "main_panel_width": width,
                "main_panel_height": height,
                "splice_required": False
            }
        elif width <= 49.5:
            return {
                "case_id": "Case 2",
                "status": "OK",
                "front_face_strategy": "48\" Panel + Splice",
                "main_panel_width": STD_PANEL_WIDTH,
                "main_panel_height": height,
                "splice_required": True,
                "splice_width": width - STD_PANEL_WIDTH,
                "min_splice_overlap": MIN_SPLICE_OVERLAP
            }
        elif width <= 50.0:
            return {
                "case_id": "Case 3",
                "status": "OK",
                "front_face_strategy": "48\" Panel + Splice",
                "main_panel_width": STD_PANEL_WIDTH, 
                "main_panel_height": height,
                "splice_required": True,
                "splice_width": 2.0,  # Fixed at 2 inches for this case
                "min_splice_overlap": MIN_SPLICE_OVERLAP
            }
        elif width <= 53.75:
            return {
                "case_id": "Case 4",
                "status": "OK", 
                "front_face_strategy": "48\" Panel + Splice",
                "main_panel_width": STD_PANEL_WIDTH,
                "main_panel_height": height,
                "splice_required": True,
                "splice_width": 5.75,  # Fixed at 5.75 inches for this case
                "min_splice_overlap": MIN_SPLICE_OVERLAP
            }
        elif width <= 54.25:
            return {
                "case_id": "Case 5",
                "status": "OK",
                "front_face_strategy": "48\" Panel + Splice",
                "main_panel_width": STD_PANEL_WIDTH,
                "main_panel_height": height,
                "splice_required": True,
                "splice_width": 6.25,  # Fixed at 6.25 inches for this case
                "min_splice_overlap": MIN_SPLICE_OVERLAP
            }
        elif width <= 74.0:
            return {
                "case_id": "Case 6",
                "status": "OK",
                "front_face_strategy": "Complex Splice Configuration",
                "main_panel_width": STD_PANEL_WIDTH,
                "main_panel_height": height,
                "second_panel_width": 26.0,  # From rear panel composition
                "splice_required": True,
                "min_splice_overlap": MIN_SPLICE_OVERLAP,
                "front_view_dimensions": {
                    "dim_1": 24.0,
                    "dim_2": 22.5,
                    "dim_3": 1.5,
                    "dim_4": 19.0,
                    "dim_5": 1.5,
                    "dim_6": 20.5
                }
            }
        elif width <= 96.0:
            return {
                "case_id": "Case 7",
                "status": "OK", 
                "front_face_strategy": "Two 48\" Panels + Central Splice",
                "main_panel_width": STD_PANEL_WIDTH,
                "main_panel_height": height,
                "second_panel_width": STD_PANEL_WIDTH,
                "splice_required": True,
                "min_splice_overlap": MIN_SPLICE_OVERLAP,
                "front_view_dimensions": {
                    "dim_1": 24.0,
                    "dim_2": 22.5, 
                    "dim_3": 22.0,
                    "dim_4": 24.0
                }
            }
    
    # Handle cases where Width ≤ 48 inches and Height > 96 inches (Cases 1-1 to 1-5)
    elif width <= STD_PANEL_WIDTH and height > STD_PANEL_HEIGHT:
        if height <= 97.5:
            return {
                "case_id": "Case 1-1",
                "status": "OK",
                "front_face_strategy": "96\" High Panel + Top Splice",
                "main_panel_width": width,
                "main_panel_height": STD_PANEL_HEIGHT,
                "splice_required": True,
                "splice_type": "vertical",
                "splice_panel_height": height - STD_PANEL_HEIGHT,
                "min_splice_overlap": MIN_SPLICE_OVERLAP
            }
        elif height <= 98.0:
            return {
                "case_id": "Case 1-2",
                "status": "OK",
                "front_face_strategy": "96\" High Panel + Top Splice",
                "main_panel_width": width, 
                "main_panel_height": STD_PANEL_HEIGHT,
                "splice_required": True,
                "splice_type": "vertical",
                "splice_panel_height": 2.0,  # Fixed at 2 inches for this case
                "min_splice_overlap": MIN_SPLICE_OVERLAP
            }
        elif height <= 101.75:
            return {
                "case_id": "Case 1-3",
                "status": "OK",
                "front_face_strategy": "96\" High Panel + Top Splice",
                "main_panel_width": width,
                "main_panel_height": STD_PANEL_HEIGHT,
                "splice_required": True, 
                "splice_type": "vertical",
                "splice_panel_height": 5.75,  # Fixed at 5.75 inches for this case
                "min_splice_overlap": MIN_SPLICE_OVERLAP
            }
        elif height <= 102.25:
            return {
                "case_id": "Case 1-4",
                "status": "OK",
                "front_face_strategy": "96\" High Panel + Top Splice",
                "main_panel_width": width,
                "main_panel_height": STD_PANEL_HEIGHT,
                "splice_required": True,
                "splice_type": "vertical",
                "splice_panel_height": 6.25,  # Fixed at 6.25 inches for this case
                "min_splice_overlap": MIN_SPLICE_OVERLAP
            }
        elif height <= 116.0:
            return {
                "case_id": "Case 1-5",
                "status": "OK",
                "front_face_strategy": "96\" High Panel + Top Splice",
                "main_panel_width": width,
                "main_panel_height": STD_PANEL_HEIGHT,
                "splice_required": True,
                "splice_type": "vertical",
                "splice_panel_height": height - STD_PANEL_HEIGHT,
                "min_splice_overlap": MIN_SPLICE_OVERLAP
            }
    
    # If none of the defined cases match but dimensions are within limits
    return {
        "case_id": "UNDEFINED",
        "status": "WARNING",
        "message": f"No specific case defined for Width={width}, Height={height}, but dimensions are within limits"
    }

def calculate_cleat_positions(dimension, max_spacing=MAX_CLEAT_SPACING, edge_cleats=True):
    """
    Calculates positions of cleats along a dimension, ensuring max spacing is not exceeded.
    
    Args:
        dimension: Total dimension to place cleats along (inches)
        max_spacing: Maximum allowable spacing between cleats (inches)
        edge_cleats: Whether to include cleats at the edges
        
    Returns:
        list: Positions of cleats from one end (0.0) to the other (dimension)
    """
    positions = []
    
    # Add edge cleats if requested
    if edge_cleats:
        positions.append(0.0)  # Start edge
        positions.append(dimension)  # End edge
    
    # If dimension is small enough, just return edge cleats
    if dimension <= max_spacing:
        return positions
    
    # Calculate number of intermediate cleats needed
    num_spaces = int(dimension / max_spacing)
    if dimension % max_spacing == 0:
        num_spaces -= 1  # Exact division means one fewer space
    
    num_intermediate_cleats = num_spaces - 1 if edge_cleats else num_spaces + 1
    
    # Even spacing between all cleats
    if num_intermediate_cleats > 0:
        spacing = dimension / (num_intermediate_cleats + 1 if edge_cleats else num_intermediate_cleats - 1)
        for i in range(1, num_intermediate_cleats + 1):
            positions.append(i * spacing)
    
    # Sort positions
    positions = sorted(positions)
    
    return positions

def generate_panel_config(width, height, panel_thickness, cleat_thickness, cleat_width):
    """
    Generates complete panel configuration including panels and cleats.
    
    Args:
        width: Width of the autocrate front face (inches)
        height: Height of the autocrate front face (inches)
        panel_thickness: Thickness of wall panel material (inches)
        cleat_thickness: Thickness of cleat material (inches)
        cleat_width: Width of cleat material (inches)
        
    Returns:
        dict: Complete panel configuration with cleats and splices
    """
    # Determine which case applies
    case_info = determine_panel_case(width, height)
    
    # If error case, return immediately
    if case_info["status"] == "ERROR":
        return case_info
    
    # Initialize panel config with case info
    panel_config = {
        "case_info": case_info,
        "panel_thickness": panel_thickness,
        "cleat_thickness": cleat_thickness,
        "cleat_width": cleat_width,
        "side_panels": {},
        "end_panels": {},
        "cleats": [],
        "splices": []
    }
    
    # Calculate side panel dimensions
    side_panel_width = width
    side_panel_height = height
    
    # Calculate end panel dimensions
    end_panel_width = width
    end_panel_height = height
    
    # Calculate cleat positions for side panels
    side_vertical_cleats = calculate_cleat_positions(side_panel_height, MAX_CLEAT_SPACING)
    side_horizontal_cleats = calculate_cleat_positions(side_panel_width, MAX_CLEAT_SPACING)
    
    # Calculate cleat positions for end panels
    end_vertical_cleats = calculate_cleat_positions(end_panel_height, MAX_CLEAT_SPACING)
    end_horizontal_cleats = calculate_cleat_positions(end_panel_width, MAX_CLEAT_SPACING)
    
    # Setup panel info based on case
    if case_info["splice_required"]:
        # Handle different splice cases
        if "splice_type" in case_info and case_info["splice_type"] == "vertical":
            # Vertical splice (height extension)
            panel_config["splices"].append({
                "type": "vertical",
                "position": STD_PANEL_HEIGHT - CLEAT_SPLICE_CLEARANCE,
                "detail_a_dim_1": DETAIL_A_DIM_1,
                "detail_a_dim_2": DETAIL_A_DIM_2,
                "min_overlap": MIN_SPLICE_OVERLAP
            })
        else:
            # Horizontal splice (width extension)
            splice_position = STD_PANEL_WIDTH - CLEAT_SPLICE_CLEARANCE
            panel_config["splices"].append({
                "type": "horizontal",
                "position": splice_position,
                "detail_a_dim_1": DETAIL_A_DIM_1,
                "detail_a_dim_2": DETAIL_A_DIM_2,
                "min_overlap": MIN_SPLICE_OVERLAP
            })
            
            # Add special handling for multi-panel cases (like Case 7)
            if case_info["case_id"] == "Case 7":
                # Central splice for two 48" panels
                panel_config["splices"].append({
                    "type": "central", 
                    "position": STD_PANEL_WIDTH,
                    "detail_a_dim_1": DETAIL_A_DIM_1,
                    "detail_a_dim_2": DETAIL_A_DIM_2,
                    "min_overlap": MIN_SPLICE_OVERLAP
                })
    
    # Add panel info
    panel_config["side_panels"] = {
        "width": side_panel_width,
        "height": side_panel_height,
        "thickness": panel_thickness,
        "vertical_cleats": side_vertical_cleats,
        "horizontal_cleats": side_horizontal_cleats
    }
    
    panel_config["end_panels"] = {
        "width": end_panel_width, 
        "height": end_panel_height,
        "thickness": panel_thickness,
        "vertical_cleats": end_vertical_cleats,
        "horizontal_cleats": end_horizontal_cleats
    }
    
    # Generate NX expression data
    panel_config["exp_data"] = {
        "INPUT_Max_Cleat_Spacing": MAX_CLEAT_SPACING,
        "INPUT_Min_Splice_Overlap": MIN_SPLICE_OVERLAP,
        "INPUT_Cleat_Splice_Clearance": CLEAT_SPLICE_CLEARANCE,
        "CALC_Panel_Case_ID": case_info["case_id"],
        "CALC_Splice_Required": 1 if case_info["splice_required"] else 0,
        "CALC_Std_Panel_Width": STD_PANEL_WIDTH,
        "CALC_Std_Panel_Height": STD_PANEL_HEIGHT,
        "DETAIL_A_Dim_1": DETAIL_A_DIM_1,
        "DETAIL_A_Dim_2": DETAIL_A_DIM_2
    }
    
    return panel_config

if __name__ == '__main__':
    # Test cases
    test_dimensions = [
        (45, 90),    # Case 1
        (49, 90),    # Case 2
        (50, 90),    # Case 3
        (53, 90),    # Case 4
        (54, 90),    # Case 5
        (70, 90),    # Case 6
        (95, 90),    # Case 7
        (45, 97),    # Case 1-1
        (45, 98),    # Case 1-2
        (45, 101),   # Case 1-3
        (45, 102),   # Case 1-4
        (45, 115)    # Case 1-5
    ]
    
    import json
    for width, height in test_dimensions:
        case_info = determine_panel_case(width, height)
        print(f"Width={width}, Height={height} => {case_info['case_id']}")
        # Uncomment to see full case details
        # print(json.dumps(case_info, indent=2))
