# wizard_app/floorboard_logic.py
# VERSION: Refined for N-Instance Suppression Strategy (Single Standard Type, Zero Gap Target)

import logging
import math
from typing import Dict, List, Any, Tuple

try:
    from . import config # For ALL_STANDARD_FLOORBOARDS, FLOAT_TOLERANCE
except ImportError:
    import config # Fallback for testing or direct execution

log = logging.getLogger(__name__)

def calculate_floorboard_layout_refined(
    target_span_to_fill_y: float,
    board_length_x: float, # This is CALC_Overall_Skid_Span
    chosen_standard_nominal: str,
    allow_custom_fill: bool,
    floorboard_actual_thickness_z: float 
) -> Dict[str, Any]:
    """
    Calculates floorboard layout using one chosen standard lumber type and one optional
    custom fill piece to achieve minimal/zero gap, placing boards symmetrically.

    Args:
        target_span_to_fill_y: The total span along the Y-axis that floorboards need to cover.
        board_length_x: The length of each floorboard piece (dimension across skids, along X-axis).
        chosen_standard_nominal: The single nominal size of standard lumber to use (e.g., "2x8").
        allow_custom_fill: Boolean, whether a custom width piece can be used to fill the remainder.
        floorboard_actual_thickness_z: The thickness of the floorboard lumber.

    Returns:
        A dictionary containing the layout details and summary.
    """
    result = {
        "status": "INIT",
        "message": "Floorboard calculation not started.",
        "boards_layout_details": [], # List of dicts for each board
        "summary": {
            "chosen_standard_nominal": chosen_standard_nominal,
            "chosen_standard_actual_width_y": 0.0,
            "total_standard_boards_count": 0,
            "custom_board_actual_width_y": 0.0,
            "custom_board_count": 0,
            "final_gap_y": target_span_to_fill_y, # Initially, the whole span is a gap
            "target_span_input_y": target_span_to_fill_y,
            "calculated_span_covered_y": 0.0 # Sum of actual board widths placed
        }
    }

    # --- Input Validation and Setup ---
    # Ensure config is loaded for ALL_STANDARD_FLOORBOARDS and FLOAT_TOLERANCE
    if not config or not hasattr(config, 'ALL_STANDARD_FLOORBOARDS') or not hasattr(config, 'FLOAT_TOLERANCE'):
        result["status"] = "ERROR"
        result["message"] = "Configuration (config.py with ALL_STANDARD_FLOORBOARDS and FLOAT_TOLERANCE) not loaded."
        log.error(result["message"])
        return result

    if target_span_to_fill_y <= config.FLOAT_TOLERANCE:
        result["status"] = "ERROR"; result["message"] = "Target span for floorboards must be positive."
        log.error(result["message"]); return result
    if board_length_x <= config.FLOAT_TOLERANCE:
        result["status"] = "ERROR"; result["message"] = "Board length (across skids) must be positive."
        log.error(result["message"]); return result
    if not chosen_standard_nominal or chosen_standard_nominal not in config.ALL_STANDARD_FLOORBOARDS:
        result["status"] = "ERROR"; result["message"] = f"Invalid or missing standard floorboard nominal size: {chosen_standard_nominal}."
        log.error(result["message"]); return result

    standard_board_actual_width_y = config.ALL_STANDARD_FLOORBOARDS.get(chosen_standard_nominal, 0.0)
    if standard_board_actual_width_y <= config.FLOAT_TOLERANCE:
        result["status"] = "ERROR"; result["message"] = f"Actual width for {chosen_standard_nominal} is zero or invalid."
        log.error(result["message"]); return result
    
    result["summary"]["chosen_standard_actual_width_y"] = standard_board_actual_width_y

    log.info(
        f"Refined Floorboard Calc: TargetSpanY={target_span_to_fill_y:.3f}\", "
        f"BoardLenX={board_length_x:.3f}\", StdNominal={chosen_standard_nominal} ({standard_board_actual_width_y:.3f}\"W), "
        f"CustomAllowed={allow_custom_fill}, ThicknessZ={floorboard_actual_thickness_z:.3f}\""
    )

    boards_placed_details = []
    current_pos_front_edge_relative = 0.0 
    current_pos_back_edge_relative = target_span_to_fill_y
    total_std_boards_count = 0

    # 1. Place symmetrical pairs of STANDARD boards
    while True:
        remaining_center_span_for_pairs = current_pos_back_edge_relative - current_pos_front_edge_relative
        if remaining_center_span_for_pairs < (2 * standard_board_actual_width_y) - config.FLOAT_TOLERANCE:
            break

        boards_placed_details.append({
            "type": "standard", "nominal_size": chosen_standard_nominal,
            "actual_width_y": standard_board_actual_width_y, "length_x": board_length_x,
            "thickness_z": floorboard_actual_thickness_z,
            "y_pos_relative_start_edge": round(current_pos_front_edge_relative, 4)
        })
        current_pos_front_edge_relative += standard_board_actual_width_y
        total_std_boards_count += 1

        boards_placed_details.append({
            "type": "standard", "nominal_size": chosen_standard_nominal,
            "actual_width_y": standard_board_actual_width_y, "length_x": board_length_x,
            "thickness_z": floorboard_actual_thickness_z,
            "y_pos_relative_start_edge": round(current_pos_back_edge_relative - standard_board_actual_width_y, 4)
        })
        current_pos_back_edge_relative -= standard_board_actual_width_y
        total_std_boards_count += 1
        
        if total_std_boards_count > 200: 
            result["status"] = "ERROR"; result["message"] = "Exceeded standard board count limit (200)."
            log.error(result["message"]); return result
            
    log.debug(f"Placed {total_std_boards_count} standard boards. Front edge at {current_pos_front_edge_relative:.3f}, Back edge at {current_pos_back_edge_relative:.3f}")

    remaining_gap_y = current_pos_back_edge_relative - current_pos_front_edge_relative
    custom_board_actual_width_y = 0.0
    custom_board_count = 0

    if remaining_gap_y < -config.FLOAT_TOLERANCE:
        result["status"] = "ERROR"; result["message"] = f"Internal error: Negative remaining gap ({remaining_gap_y:.4f})."
        log.error(result["message"]); return result

    if allow_custom_fill and remaining_gap_y > config.FLOAT_TOLERANCE:
        custom_board_actual_width_y = remaining_gap_y 
        custom_board_count = 1
        boards_placed_details.append({
            "type": "custom", "nominal_size": "Custom",
            "actual_width_y": round(custom_board_actual_width_y, 4), "length_x": board_length_x,
            "thickness_z": floorboard_actual_thickness_z,
            "y_pos_relative_start_edge": round(current_pos_front_edge_relative, 4)
        })
        remaining_gap_y = 0.0 
        log.info(f"Custom fill piece added. Width: {custom_board_actual_width_y:.3f}\"")
    elif remaining_gap_y > config.FLOAT_TOLERANCE:
        log.warning(f"Remaining gap of {remaining_gap_y:.3f}\" exists, custom fill not allowed or not triggered.")

    boards_placed_details.sort(key=lambda b: b["y_pos_relative_start_edge"])
    result["boards_layout_details"] = boards_placed_details
    
    result["summary"]["total_standard_boards_count"] = total_std_boards_count
    result["summary"]["custom_board_actual_width_y"] = round(custom_board_actual_width_y, 4)
    result["summary"]["custom_board_count"] = custom_board_count
    result["summary"]["final_gap_y"] = round(remaining_gap_y, 4)
    
    calculated_span_covered_by_boards_only = sum(b["actual_width_y"] for b in boards_placed_details)
    result["summary"]["calculated_span_covered_y"] = round(calculated_span_covered_by_boards_only, 4)

    if not math.isclose(target_span_to_fill_y, calculated_span_covered_by_boards_only + result["summary"]["final_gap_y"], abs_tol=config.FLOAT_TOLERANCE * 10):
        result["status"] = "ERROR"
        result["message"] = (f"Critical Error: Span verification failed. Target: {target_span_to_fill_y:.4f} != "
                             f"Boards_Width_Sum ({calculated_span_covered_by_boards_only:.4f}) + Final_Gap ({result['summary']['final_gap_y']:.4f})")
        log.error(result["message"]); return result

    result["status"] = "OK"
    if result["summary"]["final_gap_y"] > config.FLOAT_TOLERANCE:
        result["status"] = "WARNING" 
        result["message"] = f"Floorboard layout calculated. Note: Final gap of {result['summary']['final_gap_y']:.4f}\" exists."
    else:
        result["message"] = "Floorboard layout calculated successfully with minimal/zero gap."
    
    log.info(f"Floorboard Calculation Complete. Status: {result['status']}. Boards: {len(boards_placed_details)}. Final Gap: {result['summary']['final_gap_y']:.4f}")
    return result

if __name__ == '__main__':
    if not hasattr(config, 'ALL_STANDARD_FLOORBOARDS'): 
        config.ALL_STANDARD_FLOORBOARDS = {"2x6": 5.5, "2x8": 7.25, "2x10": 9.25, "2x12": 11.25}
    if not hasattr(config, 'FLOAT_TOLERANCE'):
        config.FLOAT_TOLERANCE = 1e-6

    logging.basicConfig(level=logging.DEBUG)

    test_target_span_y = 60.0 
    test_board_len_x = 70.0   
    test_std_nominal = "2x8" 
    test_allow_custom = True
    test_thickness_z = 1.5

    layout1 = calculate_floorboard_layout_refined(
        test_target_span_y, test_board_len_x, test_std_nominal, test_allow_custom, test_thickness_z
    )
    print("\n--- Test Case 1 (Custom Fill Expected) ---")
    print(f"Status: {layout1['status']}, Message: {layout1['message']}")
    print(f"Summary: {json.dumps(layout1['summary'], indent=2)}")
    print("Board Details:")
    for board in layout1['boards_layout_details']:
        print(f"  - Type: {board['type']}, Nominal: {board['nominal_size']}, "
              f"Width(Y): {board['actual_width_y']:.3f}, Len(X): {board['length_x']:.3f}, Thick(Z): {board['thickness_z']:.3f}, "
              f"Rel Y Pos Edge: {board['y_pos_relative_start_edge']:.3f}")
    # Expected for 60 span, 2x8 (7.25W): 4 pairs (8 boards) = 58.0. Gap = 2.0. Custom = 2.0. Total 9 boards.

    test_target_span_y_2 = config.ALL_STANDARD_FLOORBOARDS["2x6"] * 4 
    layout2 = calculate_floorboard_layout_refined(
        test_target_span_y_2, test_board_len_x, "2x6", True, test_thickness_z
    )
    print("\n--- Test Case 2 (Exact Fit with Standard) ---")
    # Expected: 4 standard 2x6 boards, 0 custom, 0 gap.
    print(f"Summary: {json.dumps(layout2['summary'], indent=2)}")
    for board in layout2['boards_layout_details']:
        print(f"  - Type: {board['type']}, Nominal: {board['nominal_size']}, Width(Y): {board['actual_width_y']:.3f}, Rel Y Pos Edge: {board['y_pos_relative_start_edge']:.3f}")

    test_target_span_y_3 = 60.0
    layout3 = calculate_floorboard_layout_refined(
        test_target_span_y_3, test_board_len_x, "2x12", False, test_thickness_z 
    )
    print("\n--- Test Case 3 (No Custom, Gap Remains) ---")
    # Expected for 60 span, 2x12 (11.25W): 2 pairs (4 boards) = 45.0. Gap = 15.0.
    print(f"Summary: {json.dumps(layout3['summary'], indent=2)}")
    for board in layout3['boards_layout_details']:
        print(f"  - Type: {board['type']}, Nominal: {board['nominal_size']}, Width(Y): {board['actual_width_y']:.3f}, Rel Y Pos Edge: {board['y_pos_relative_start_edge']:.3f}")