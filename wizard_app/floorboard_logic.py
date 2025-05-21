#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Logic for calculating floorboard components."""

import math

try:
    from . import config
except ImportError:
    import config # For direct testing

def calculate_floorboard_layout_refined(
    target_span_to_fill_y: float, 
    board_length_x: float, 
    chosen_standard_floorboard_nominal_key: str, # e.g., "2x6"
    allow_custom_fill: bool, 
    floorboard_actual_thickness_z: float,
    max_instances_per_side: int = 10 # From CAD guide floorboard section
) -> dict:
    """Calculates floorboard layout for NX, including suppression flags.
    Assumes symmetrical placement from front and back, filling towards the center.
    Generates exp_data with individual board parameters for NX.
    Args:
        target_span_to_fill_y: The total internal span (Y-axis) to be covered by floorboards.
        board_length_x: The length of each floorboard (X-axis, typically CALC_Floor_Board_Length_Across_Skids).
        chosen_standard_floorboard_nominal_key: Key for ALL_STANDARD_FLOORBOARDS (e.g., "2x6").
        allow_custom_fill: Boolean, whether a custom width piece can be used for the final gap.
        floorboard_actual_thickness_z: Actual thickness of the floorboard lumber.
        max_instances_per_side: Max floorboard instances NX template supports from one side (e.g., FB_Std_Front_1 to N).
    """

    boards_placed_details = []
    exp_data_floor = {
        "INPUT_Floorboard_Actual_Thickness": floorboard_actual_thickness_z,
        "CALC_Floor_Board_Length_Across_Skids": board_length_x 
    }

    standard_board_actual_width_y = config.ALL_STANDARD_FLOORBOARDS.get(chosen_standard_floorboard_nominal_key, 0.0)
    if standard_board_actual_width_y <= config.FLOAT_TOLERANCE:
        # Handle error: invalid standard board choice
        return {"status": "ERROR", "message": f"Invalid standard floorboard key: {chosen_standard_floorboard_nominal_key}", "exp_data": exp_data_floor, "boards": []}

    # Initialize all possible NX instance expressions to suppress
    for i in range(1, max_instances_per_side + 1):
        exp_data_floor[f"FB_Std_Front_{i}_Suppress_Flag"] = 1
        exp_data_floor[f"FB_Std_Front_{i}_Actual_Width"] = 0
        exp_data_floor[f"FB_Std_Front_{i}_Y_Pos_Abs"] = 0 # Absolute Y position of the board's starting edge
        
        exp_data_floor[f"FB_Std_Back_{i}_Suppress_Flag"] = 1
        exp_data_floor[f"FB_Std_Back_{i}_Actual_Width"] = 0
        exp_data_floor[f"FB_Std_Back_{i}_Y_Pos_Abs"] = 0

    exp_data_floor["FB_Custom_Center_Suppress_Flag"] = 1
    exp_data_floor["FB_Custom_Center_Actual_Width"] = 0
    exp_data_floor["FB_Custom_Center_Y_Pos_Abs"] = 0
    
    current_y_front_edge = 0.0 # Start from Y=0 (min Y edge of target_span_to_fill_y)
    current_y_back_edge = target_span_to_fill_y # Max Y edge of target_span_to_fill_y
    
    std_boards_front_count = 0
    std_boards_back_count = 0
    custom_board_count = 0
    custom_board_actual_width = 0.0

    # Place standard boards from front and back inwards
    for i in range(1, max_instances_per_side + 1):
        remaining_gap = current_y_back_edge - current_y_front_edge
        if remaining_gap < standard_board_actual_width_y - config.FLOAT_TOLERANCE:
            break # Gap too small for another standard board

        # Place front board for this iteration i
        if std_boards_front_count < max_instances_per_side and remaining_gap >= standard_board_actual_width_y:
            exp_data_floor[f"FB_Std_Front_{i}_Suppress_Flag"] = 0
            exp_data_floor[f"FB_Std_Front_{i}_Actual_Width"] = standard_board_actual_width_y
            exp_data_floor[f"FB_Std_Front_{i}_Y_Pos_Abs"] = current_y_front_edge
            boards_placed_details.append({"type": "std_front", "id": i, "width": standard_board_actual_width_y, "y_pos": current_y_front_edge})
            current_y_front_edge += standard_board_actual_width_y
            std_boards_front_count += 1
            remaining_gap = current_y_back_edge - current_y_front_edge # Update remaining gap

        # Place back board for this iteration i, if space allows
        if std_boards_back_count < max_instances_per_side and remaining_gap >= standard_board_actual_width_y:
            exp_data_floor[f"FB_Std_Back_{i}_Suppress_Flag"] = 0
            exp_data_floor[f"FB_Std_Back_{i}_Actual_Width"] = standard_board_actual_width_y
            # Y_Pos_Abs for back boards is the STARTING edge of the board, from Y=0 origin.
            # So, it's current_y_back_edge - standard_board_actual_width_y
            exp_data_floor[f"FB_Std_Back_{i}_Y_Pos_Abs"] = current_y_back_edge - standard_board_actual_width_y
            boards_placed_details.append({"type": "std_back", "id": i, "width": standard_board_actual_width_y, "y_pos": current_y_back_edge - standard_board_actual_width_y})
            current_y_back_edge -= standard_board_actual_width_y
            std_boards_back_count += 1
        elif remaining_gap < standard_board_actual_width_y - config.FLOAT_TOLERANCE and remaining_gap > config.FLOAT_TOLERANCE:
            break # Gap smaller than a standard board, but still positive. Will be handled by custom fill or left as is. 

    final_gap_y = current_y_back_edge - current_y_front_edge

    if allow_custom_fill and final_gap_y > config.FLOAT_TOLERANCE: 
        # Check if custom width is within configured min/max for a single custom piece
        # For simplicity, assuming one custom piece if allowed. More complex logic could split it.
        if final_gap_y >= config.MIN_CUSTOM_NARROW_WIDTH - config.FLOAT_TOLERANCE: # only if gap is reasonably large
            custom_board_actual_width = final_gap_y
            exp_data_floor["FB_Custom_Center_Suppress_Flag"] = 0
            exp_data_floor["FB_Custom_Center_Actual_Width"] = custom_board_actual_width
            exp_data_floor["FB_Custom_Center_Y_Pos_Abs"] = current_y_front_edge # Place it after the last front board
            boards_placed_details.append({"type": "custom_center", "id": 1, "width": custom_board_actual_width, "y_pos": current_y_front_edge})
            custom_board_count = 1
            final_gap_y = 0 # Gap filled by custom board
        # Else: gap too small for preferred custom, or custom not allowed. Gap remains.

    # Sorting boards by Y position for easier review if needed
    boards_placed_details.sort(key=lambda b: b["y_pos"])

    return {
        "status": "OK",
        "message": "Floorboard layout calculated.",
        "standard_board_nominal_type": chosen_standard_floorboard_nominal_key,
        "standard_board_actual_width": standard_board_actual_width_y,
        "std_boards_front_count": std_boards_front_count,
        "std_boards_back_count": std_boards_back_count,
        "custom_board_count": custom_board_count,
        "custom_board_actual_width": custom_board_actual_width,
        "final_gap_y_remaining": final_gap_y,
        "board_length_x": board_length_x,
        "floorboard_actual_thickness_z": floorboard_actual_thickness_z,
        "boards_placed_details": boards_placed_details, # For detailed review/logging
        "exp_data": exp_data_floor
    }

if __name__ == '__main__':
    try: from . import config
    except ImportError: import config
    import json

    print("--- Floorboard Test Cases ---")

    # Test Case based on CAD guide (many instances)
    # INPUT_Floorboard_Length_X = CALC_Floor_Board_Length_Across_Skids
    # INPUT_Floorboard_Width_Y = FB_Std_Front_1_Actual_Width
    # INPUT_Floorboard_Thickness_Z = INPUT_Floorboard_Actual_Thickness
    # Position Y = FB_Std_Front_1_Y_Pos_Abs + (FB_Std_Front_1_Actual_Width / 2) -> this implies Y_Pos_Abs is edge, and NX origin is center of board
    # For this logic, Y_Pos_Abs is the starting edge (min Y) of the board, assuming NX template places board origin at this edge.
    # If NX template origin is center, then Y_Pos_Abs for exp needs to be Y_Pos_Abs_edge + width/2.
    # For now, this function returns Y_Pos_Abs as the starting edge.

    test_span_y = 50.0
    test_board_len_x = 100.0
    test_std_key = "2x8" # Actual width 7.25
    test_thickness_z = 1.5

    results1 = calculate_floorboard_layout_refined(test_span_y, test_board_len_x, test_std_key, True, test_thickness_z)
    print(f"\nTest 1 (Span={test_span_y}, Board={test_std_key}, Custom Allowed):\n{json.dumps(results1, indent=2)}")
    # Expected: 50 / 7.25 = 6.89. So 3 front (21.75), 3 back (21.75). Total 6 boards (43.5). Gap = 6.5
    # Custom fill: 6.5
    assert results1["std_boards_front_count"] == 3
    assert results1["std_boards_back_count"] == 3 
    assert results1["custom_board_count"] == 1
    assert math.isclose(results1["exp_data"]["FB_Custom_Center_Actual_Width"], 6.5)
    assert math.isclose(results1["final_gap_y_remaining"], 0.0)

    results2 = calculate_floorboard_layout_refined(test_span_y, test_board_len_x, test_std_key, False, test_thickness_z)
    print(f"\nTest 2 (Span={test_span_y}, Board={test_std_key}, Custom NOT Allowed):\n{json.dumps(results2, indent=2)}")
    assert results2["custom_board_count"] == 0
    assert math.isclose(results2["final_gap_y_remaining"], 6.5)

    test_span_y_small_gap = 15.0 # 2x8 (7.25) * 2 = 14.5. Gap = 0.5
    results3 = calculate_floorboard_layout_refined(test_span_y_small_gap, test_board_len_x, test_std_key, True, test_thickness_z)
    print(f"\nTest 3 (Span={test_span_y_small_gap}, Small Gap, Custom Allowed but < MIN_CUSTOM_NARROW_WIDTH):\n{json.dumps(results3, indent=2)}")
    assert results3["std_boards_front_count"] == 1
    assert results3["std_boards_back_count"] == 1
    assert results3["custom_board_count"] == 0 # Custom should not be placed if gap < MIN_CUSTOM_NARROW_WIDTH
    assert math.isclose(results3["final_gap_y_remaining"], 0.5)

    test_span_y_exact_fit = 14.5 # 2x8 (7.25) * 2 = 14.5. Gap = 0.0
    results4 = calculate_floorboard_layout_refined(test_span_y_exact_fit, test_board_len_x, test_std_key, True, test_thickness_z)
    print(f"\nTest 4 (Span={test_span_y_exact_fit}, Exact Fit):\n{json.dumps(results4, indent=2)}")
    assert results4["std_boards_front_count"] == 1
    assert results4["std_boards_back_count"] == 1
    assert results4["custom_board_count"] == 0
    assert math.isclose(results4["final_gap_y_remaining"], 0.0)

    test_span_y_single_board = 7.0
    results5 = calculate_floorboard_layout_refined(test_span_y_single_board, test_board_len_x, test_std_key, True, test_thickness_z)
    print(f"\nTest 5 (Span={test_span_y_single_board}, Should be custom fill only or one std if it fits):\n{json.dumps(results5, indent=2)}")
    # Current logic: Tries to place std first. Gap is 7.0, std_width 7.25. So std_front_count = 0, std_back_count = 0.
    # Then custom fill for 7.0
    assert results5["std_boards_front_count"] == 0
    assert results5["std_boards_back_count"] == 0
    assert results5["custom_board_count"] == 1
    assert math.isclose(results5["custom_board_actual_width"], 7.0) 