# wizard_app/app.py
# VERSION: Meeting Mode - Full Skid & Floorboard .exp for N-Instance Strategy (All Corrected)

import sys
import os, logging, math, json, datetime

try:
    import streamlit as st
    import pandas as pd
except ImportError as e:
    print(f"Error importing required libraries: {e}. Ensure 'streamlit' and 'pandas' are installed.")
    sys.exit(1)

# --- Path Setup ---
if __name__ == "__main__" and __package__ is None:
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_script_dir)
    if parent_dir not in sys.path: sys.path.insert(0, parent_dir)
    __package__ = os.path.basename(current_script_dir)

# --- Page Config & Logging ---
APP_VERSION_FALLBACK = "0.8.20_MeetingFloorboardFinal" 
log = logging.getLogger(__package__ if __package__ else "wizard_app")
if not log.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log.info(f"Logger '{log.name}' configured with basicConfig.")

# --- Attempt to Import Project Modules ---
config = None
skid_logic = None
floorboard_logic = None
APP_VERSION = APP_VERSION_FALLBACK
try:
    from . import config 
    from . import skid_logic
    from . import floorboard_logic 
    APP_VERSION = getattr(config, 'VERSION', APP_VERSION_FALLBACK)
    log.info(f"Imported config, skid_logic, floorboard_logic (relative) - Version: {APP_VERSION}")
except ImportError as e:
    log.warning(f"Could not import all core logic modules via relative import: {e}. Trying direct imports.")
    try:
        if 'config' not in globals() or config is None: 
            import config as cfg_direct
            config = cfg_direct
            log.info("Imported config directly.")
        if 'skid_logic' not in globals() or skid_logic is None: 
            import skid_logic as sl_direct
            skid_logic = sl_direct
            log.info("Imported skid_logic directly.")
        if 'floorboard_logic' not in globals() or floorboard_logic is None: 
            import floorboard_logic as fl_direct
            floorboard_logic = fl_direct
            log.info("Imported floorboard_logic directly.")
        APP_VERSION = getattr(config, 'VERSION', APP_VERSION_FALLBACK) # Get version after attempting config import
        log.info(f"Successfully imported core logic modules directly. Version: {APP_VERSION}")
    except ImportError:
        st.error("CRITICAL ERROR: Core logic modules (config, skid_logic, floorboard_logic) not found even with direct import. App cannot run.")
        log.error("Failed to import core logic modules directly. App will not function correctly.")
        st.stop() 

st.set_page_config(layout="wide", page_title=f"AutoCrate Wizard v{APP_VERSION}", page_icon="⚙️")

# --- Function to generate .exp file content ---
def generate_nx_exp_file_content(product_params, skid_results_for_exp, floorboard_exp_data):
    """
    Generates the content for an NX .exp file including Skids and Floorboards
    for N-Instance Suppression strategy.
    """
    p_weight = product_params.get('product_weight', 2500.0)
    p_width = product_params.get('product_width', 90.0)
    p_length = product_params.get('product_length', 90.0)
    p_actual_height = product_params.get('product_actual_height', 48.0)
    p_clearance_side = product_params.get('clearance_side', 2.0)
    p_clearance_above = product_params.get('clearance_above_product', 1.5)
    p_panel_thickness = product_params.get('panel_thickness', 0.25)
    p_wall_cleat_thickness = product_params.get('wall_cleat_thickness', 0.75)
    chosen_std_fb_nominal_from_params = product_params.get('chosen_standard_floorboard_nominal', "N/A")

    generation_time = product_params.get('generation_timestamp', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    exp_content = []
    exp_content.append("// NX Expressions for AutoCrate Wizard - Skids & Floorboards (N-Instance Strategy)")
    exp_content.append(f"// Parameters based on UI state at: {generation_time}")
    
    exp_content.append("\n// =============================")
    exp_content.append("// 1. USER CONTROLS (Values from UI)")
    exp_content.append("// =============================")
    exp_content.append(f"[lbm]product_weight = {p_weight:.1f}  // Product Weight")
    exp_content.append(f"[Inch]product_width = {p_width:.2f}     // Product Width - across skids")
    exp_content.append(f"[Inch]product_length = {p_length:.2f}    // Product Length - along skids")
    exp_content.append(f"[Inch]product_actual_height = {p_actual_height:.2f} // Product Actual Height (for content)")
    exp_content.append(f"[Inch]clearance_side = {p_clearance_side:.2f}     // Clearance per Side (product to inner wall face)")
    exp_content.append(f"[Inch]clearance_above_product = {p_clearance_above:.2f} // Clearance above product")
    exp_content.append(f"[Inch]panel_thickness = {p_panel_thickness:.3f}   // Panel Sheathing Thickness")
    exp_content.append(f"[Inch]wall_cleat_thickness = {p_wall_cleat_thickness:.3f}   // Wall Cleat Actual Thickness (used for front/back wall offset)")
    exp_content.append(f"[Inch]wall_cleat_width = {product_params.get('wall_cleat_width', 3.5):.2f} // Wall Cleat Actual Width")
    exp_content.append(f"[Inch]floor_lumbar_thickness = {product_params.get('floor_lumbar_thickness', 1.5):.3f} // Floorboard Actual Thickness")
    exp_content.append(f"// CHOSEN_Std_Floorboard_Nominal_UI: \"{chosen_std_fb_nominal_from_params}\" (Selected in UI - For Info Only)") 
    exp_content.append(f"[Inch]cap_cleat_thickness = {product_params.get('cap_cleat_thickness', 0.75):.3f} // Cap Cleat Actual Thickness")
    exp_content.append(f"[Inch]cap_cleat_width = {product_params.get('cap_cleat_width', 3.5):.2f}     // Cap Cleat Actual Width")
    exp_content.append(f"[Inch]max_cap_cleat_spacing_rule = {product_params.get('max_top_cleat_spacing', 24.0):.2f} // Max rule for cap cleats")

    exp_content.append("\n// --- Constants (Informational) ---")
    exp_content.append("[Inch]min_skid_height_const = 3.5")
    exp_content.append("[Inch]float_tolerance_const = 0.001")

    exp_content.append("\n// ===========================================")
    exp_content.append("// 2. CALCULATED CRATE AND USABLE DIMENSIONS (NX Expressions)")
    exp_content.append("// ===========================================")
    exp_content.append("[Inch]crate_width_OD = product_width + 2 * (clearance_side + panel_thickness + wall_cleat_thickness)")
    exp_content.append("[Inch]crate_length_OD = product_length + 2 * (clearance_side + panel_thickness + wall_cleat_thickness)")
    exp_content.append("[Inch]skid_usable_width_ID = crate_width_OD - 2 * (panel_thickness + wall_cleat_thickness)")

    exp_content.append("\n// =============================")
    exp_content.append("// 3. SKID LAYOUT (Values from Python skid_logic, for NX Pattern)")
    exp_content.append("// =============================")
    exp_content.append(f"[Inch]INPUT_Skid_Nominal_Width = {skid_results_for_exp.get('skid_width', 3.5):.3f}")
    exp_content.append(f"[Inch]INPUT_Skid_Nominal_Height = {skid_results_for_exp.get('skid_height', 3.5):.3f}")
    exp_content.append(f"[Inch]RULE_Max_Skid_Spacing_Ref = {skid_results_for_exp.get('max_spacing', 30.0):.2f} // Max spacing rule applied by Python logic")
    
    exp_content.append(f"CALC_Skid_Count = {skid_results_for_exp.get('skid_count', 0)}")
    exp_content.append(f"[Inch]CALC_Skid_Pitch = {skid_results_for_exp.get('spacing_actual', 0.0):.4f}")
    
    first_skid_pos_x_py_calc = 0.0
    skid_count_val = skid_results_for_exp.get('skid_count', 0)
    skid_spacing_val = skid_results_for_exp.get('spacing_actual', 0.0)
    if skid_count_val == 1:
        first_skid_pos_x_py_calc = 0.0
    elif skid_count_val > 1:
        total_centerline_span_py = skid_spacing_val * (skid_count_val - 1)
        first_skid_pos_x_py_calc = -total_centerline_span_py / 2.0
        
    exp_content.append(f"[Inch]CALC_First_Skid_Pos_X = {first_skid_pos_x_py_calc:.4f}")
    
    _overall_skid_span_py = 0.0
    skid_width_val = skid_results_for_exp.get('skid_width', 0.0)
    if skid_count_val == 0 : # Handles error case from skid_logic where count is 0
        _overall_skid_span_py = 0.0
    elif skid_count_val == 1:
        _overall_skid_span_py = skid_width_val
    elif skid_count_val > 1:
        _overall_skid_span_py = (skid_count_val - 1) * skid_spacing_val + skid_width_val
        
    exp_content.append(f"[Inch]CALC_Overall_Skid_Span = {_overall_skid_span_py:.3f}")
    exp_content.append("[Inch]INPUT_Skid_Actual_Length = crate_length_OD") 

    exp_content.append("\n// ===========================================")
    exp_content.append("// 4. FLOORBOARD PARAMETERS (for N-Instance Suppression Strategy)")
    exp_content.append("// ===========================================")
    exp_content.append(f"[Inch]CALC_Floor_Start_Y_Offset_Abs = {floorboard_exp_data.get('y_offset_for_floorboards', 0.0):.3f} // Abs Y for first front board's leading edge")
    exp_content.append(f"[Inch]CALC_Floor_Target_Layout_Span = {floorboard_exp_data.get('target_span_to_fill', 0.0):.3f} // Total Y-span floorboards must cover")
    exp_content.append("[Inch]CALC_Floor_Board_Length_Across_Skids = CALC_Overall_Skid_Span // X-Length of each floorboard piece")
    exp_content.append("[Inch]INPUT_Floorboard_Actual_Thickness = floor_lumbar_thickness")
    exp_content.append(f"[Inch]CHOSEN_Std_Floorboard_Actual_Width_Val = {floorboard_exp_data.get('standard_board_actual_width', 0.0):.3f}")

    # Summary values from Python floorboard logic (for reference in .exp file)
    exp_content.append(f"// INFO_Std_Floorboard_Count_Python = {product_params.get('calculated_standard_floorboard_count',0)}")
    exp_content.append(f"// INFO_Custom_Floorboard_Count_Python = {product_params.get('calculated_custom_floorboard_count',0)}")
    exp_content.append(f"// INFO_Custom_Floorboard_Width_Python = {product_params.get('calculated_custom_floorboard_width',0.0):.3f} [Inch]")
    exp_content.append(f"// INFO_Final_Floor_Gap_Python = {product_params.get('calculated_final_floor_gap',0.0):.4f} [Inch]")


    MAX_FB_SLOTS_PER_SIDE = 10 
    
    exp_content.append("\n// --- Front Standard Floorboards (Max " + str(MAX_FB_SLOTS_PER_SIDE) + " slots) ---")
    front_boards_list = floorboard_exp_data.get('front_boards', [])
    for i in range(1, MAX_FB_SLOTS_PER_SIDE + 1):
        fb_data = front_boards_list[i-1] if i-1 < len(front_boards_list) else {}
        suppress = 0 if fb_data else 1
        width = fb_data.get('width', 0.0) if not suppress else 0.0
        y_pos_abs = fb_data.get('y_pos_abs_leading_edge', 0.0) if not suppress else 0.0
        exp_content.append(f"FB_Std_Front_{i}_Suppress_Flag = {suppress}")
        exp_content.append(f"[Inch]FB_Std_Front_{i}_Actual_Width = {width:.3f}")
        exp_content.append(f"[Inch]FB_Std_Front_{i}_Y_Pos_Abs = {y_pos_abs:.3f} // Leading Edge Y")

    exp_content.append("\n// --- Back Standard Floorboards (Max " + str(MAX_FB_SLOTS_PER_SIDE) + " slots) ---")
    back_boards_list = floorboard_exp_data.get('back_boards', [])
    for i in range(1, MAX_FB_SLOTS_PER_SIDE + 1):
        fb_data = back_boards_list[i-1] if i-1 < len(back_boards_list) else {}
        suppress = 0 if fb_data else 1
        width = fb_data.get('width', 0.0) if not suppress else 0.0
        y_pos_abs = fb_data.get('y_pos_abs_leading_edge', 0.0) if not suppress else 0.0
        exp_content.append(f"FB_Std_Back_{i}_Suppress_Flag = {suppress}")
        exp_content.append(f"[Inch]FB_Std_Back_{i}_Actual_Width = {width:.3f}")
        exp_content.append(f"[Inch]FB_Std_Back_{i}_Y_Pos_Abs = {y_pos_abs:.3f} // Leading Edge Y")

    exp_content.append("\n// --- Custom Middle Floorboard (1 slot) ---")
    custom_data = floorboard_exp_data.get('custom_board', {})
    custom_width_val = custom_data.get('width', 0.0)
    # Check config.FLOAT_TOLERANCE if config is loaded
    float_tol = getattr(config, 'FLOAT_TOLERANCE', 1e-6) if config else 1e-6
    suppress_custom = 0 if custom_data and custom_width_val > float_tol else 1
    
    width_custom = custom_width_val if not suppress_custom else 0.0
    y_pos_abs_custom = custom_data.get('y_pos_abs_leading_edge', 0.0) if not suppress_custom else 0.0
    exp_content.append(f"FB_Custom_Suppress_Flag = {suppress_custom}")
    exp_content.append(f"[Inch]FB_Custom_Actual_Width = {width_custom:.3f}")
    exp_content.append(f"[Inch]FB_Custom_Y_Pos_Abs = {y_pos_abs_custom:.3f} // Leading Edge Y")
    exp_content.append(f"[Inch]CALC_Floor_Final_Gap_Debug = {floorboard_exp_data.get('final_gap', 0.0):.4f} // For verification (Python calc)")

    exp_content.append("\n// End of AutoCrate Wizard Expressions")
    return "\n".join(exp_content)

# --- Initialize session state for UI parameters ---
default_params_for_ui = {
    'product_weight': 1800.0, 'product_width': 75.0, 'product_length': 110.0,
    'product_actual_height': 55.0, 'clearance_side': 2.5, 'clearance_above_product': 2.0,
    'panel_thickness': 0.75, 'wall_cleat_thickness': 0.75, 'wall_cleat_width': 3.5,
    'floor_lumbar_thickness': 1.5, 
    'chosen_standard_floorboard_nominal': "2x8", 
    'allow_custom_floorboard_fill': True,
    'cap_cleat_thickness': 0.75, 'cap_cleat_width': 3.5, 'max_top_cleat_spacing': 24.0
}
for key, value in default_params_for_ui.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Streamlit UI ---
st.title(f"⚙️ AutoCrate Wizard v{APP_VERSION} (Skid & Floorboard .exp)")
st.caption("Enter parameters, then click 'Update .exp File'.")

st.subheader("Product & Crate Parameters")
c1, c2, c3 = st.columns(3)
with c1:
    st.session_state.product_weight = st.number_input("Product Weight (lbs)", min_value=1.0, max_value=20000.0, value=float(st.session_state.product_weight), step=10.0, format="%.1f")
    st.session_state.product_width = st.number_input("Product Width (in)", min_value=1.0, max_value=200.0, value=float(st.session_state.product_width), step=0.5, format="%.2f")
    st.session_state.product_length = st.number_input("Product Length (in)", min_value=1.0, max_value=200.0, value=float(st.session_state.product_length), step=0.5, format="%.2f")
    st.session_state.product_actual_height = st.number_input("Product Actual Height (in)", min_value=1.0, max_value=150.0, value=float(st.session_state.product_actual_height), step=0.5, format="%.2f")
with c2:
    st.session_state.clearance_side = st.number_input("Clearance Side (in)", min_value=0.0, value=float(st.session_state.clearance_side), step=0.1, format="%.2f")
    st.session_state.clearance_above_product = st.number_input("Clearance Above Product (in)", min_value=0.0, value=float(st.session_state.clearance_above_product), step=0.1, format="%.2f")
    st.session_state.panel_thickness = st.number_input("Panel Sheathing Thickness (in)", min_value=0.01, value=float(st.session_state.panel_thickness), step=0.01, format="%.3f")
    st.session_state.floor_lumbar_thickness = st.number_input("Floorboard Actual Thickness (in)", min_value=0.1, value=float(st.session_state.floor_lumbar_thickness), step=0.01, format="%.3f")
with c3:
    st.session_state.wall_cleat_thickness = st.number_input("Wall Cleat Thickness (in)", min_value=0.1, value=float(st.session_state.wall_cleat_thickness), step=0.01, format="%.3f")
    st.session_state.wall_cleat_width = st.number_input("Wall Cleat Width (in)", min_value=0.1, value=float(st.session_state.wall_cleat_width), step=0.1, format="%.2f")
    st.session_state.cap_cleat_thickness = st.number_input("Cap Cleat Thickness (in)", min_value=0.1, value=float(st.session_state.cap_cleat_thickness), step=0.01, format="%.3f")
    st.session_state.cap_cleat_width = st.number_input("Cap Cleat Width (in)", min_value=0.1, value=float(st.session_state.cap_cleat_width), step=0.1, format="%.2f")
    st.session_state.max_top_cleat_spacing = st.number_input("Max Cap Cleat Spacing (in)", min_value=1.0, value=float(st.session_state.max_top_cleat_spacing), step=1.0, format="%.2f")

st.subheader("Floorboard Parameters")
standard_floorboard_options = ["2x6", "2x8", "2x10", "2x12"] 
if config and hasattr(config, 'ALL_STANDARD_FLOORBOARDS'):
    standard_floorboard_options = sorted(list(config.ALL_STANDARD_FLOORBOARDS.keys()))

st.session_state.chosen_standard_floorboard_nominal = st.selectbox(
    "Choose Standard Floorboard Size:",
    options=standard_floorboard_options,
    index=standard_floorboard_options.index(st.session_state.chosen_standard_floorboard_nominal) if st.session_state.chosen_standard_floorboard_nominal in standard_floorboard_options else 0
)
st.session_state.allow_custom_floorboard_fill = st.checkbox("Allow Custom Center Fill Piece for Floorboards", value=st.session_state.allow_custom_floorboard_fill)

st.markdown("---")

# --- Actions ---
try:
    APP_DIR = os.path.dirname(os.path.abspath(__file__)) 
    PROJECT_ROOT = os.path.dirname(APP_DIR) 
    TARGET_SUBFOLDER = "nx_part_templates" 
    TARGET_DIR = os.path.join(PROJECT_ROOT, TARGET_SUBFOLDER)
    
    EXP_FILENAME = "AutoCrate_Expressions.exp" 
    FIXED_EXP_FILEPATH = os.path.join(TARGET_DIR, EXP_FILENAME)
    
    st.info(f"ℹ️ The .exp file will be updated at: {FIXED_EXP_FILEPATH}")
except Exception as e:
    log.error(f"Error calculating relative path for .exp file: {e}. Defaulting to current directory.")
    FIXED_EXP_FILEPATH = "AutoCrate_Expressions.exp" 
    st.warning(f"Could not determine project relative path. .exp file will be saved to: {os.path.abspath(FIXED_EXP_FILEPATH)}")

# Collect current parameters from UI for processing
current_ui_parameters = {key: st.session_state.get(key) for key in default_params_for_ui.keys()}
current_ui_parameters['generation_timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Run Skid Logic ---
skid_results_for_processing = {}
if skid_logic: 
    skid_results_for_processing = skid_logic.calculate_skid_layout(
        product_weight=current_ui_parameters['product_weight'],
        product_width=current_ui_parameters['product_width'],
        clearance_side=current_ui_parameters['clearance_side'],
        panel_thickness=current_ui_parameters['panel_thickness'],
        cleat_thickness=current_ui_parameters['wall_cleat_thickness'] 
    )
    if not (skid_results_for_processing and skid_results_for_processing.get('status') == 'OK'):
        st.error(f"Skid calculation failed: {skid_results_for_processing.get('message', 'Unknown error')}. Exp file might be incomplete.")
        log.error(f"Skid calc failed: {skid_results_for_processing}")
        skid_results_for_processing = {'status': 'ERROR', 'skid_width': 3.5, 'skid_height': 3.5, 'max_spacing': 30.0, 'skid_count': 0, 'spacing_actual': 0.0, 'overall_skid_span': 0.0} 
else:
    st.error("Skid logic module not loaded. Cannot proceed with full calculations for .exp file.")
    skid_results_for_processing = {'status': 'ERROR', 'skid_width': 3.5, 'skid_height': 3.5, 'max_spacing': 30.0, 'skid_count': 0, 'spacing_actual': 0.0, 'overall_skid_span': 0.0} 

# --- Process Floorboard Logic ---
floorboard_data_for_exp_generation = {
    'front_boards': [], 'back_boards': [], 'custom_board': {},
    'y_offset_for_floorboards': 0.0, 'target_span_to_fill': 0.0,
    'standard_board_actual_width': 0.0, 'final_gap': 0.0
}
floor_results_from_logic = None 

if floorboard_logic and skid_results_for_processing.get('status') == 'OK' and config :
    y_offset_abs = current_ui_parameters['wall_cleat_thickness'] + current_ui_parameters['panel_thickness']
    span_to_fill = current_ui_parameters['product_length'] + (2 * current_ui_parameters['clearance_side'])
    
    skid_count_val = skid_results_for_processing.get('skid_count', 0)
    skid_spacing_val = skid_results_for_processing.get('spacing_actual', 0.0)
    skid_width_val = skid_results_for_processing.get('skid_width', 0.0)
    board_len_x_val = 0.0
    if skid_count_val == 0: board_len_x_val = 0.0
    elif skid_count_val == 1: board_len_x_val = skid_width_val
    else: board_len_x_val = (skid_count_val - 1) * skid_spacing_val + skid_width_val
    
    floor_results_from_logic = floorboard_logic.calculate_floorboard_layout_refined(
        target_span_to_fill_y=span_to_fill,
        board_length_x=board_len_x_val, 
        chosen_standard_nominal=current_ui_parameters['chosen_standard_floorboard_nominal'],
        allow_custom_fill=current_ui_parameters['allow_custom_floorboard_fill'],
        floorboard_actual_thickness_z=current_ui_parameters['floor_lumbar_thickness']
    )

    if floor_results_from_logic and floor_results_from_logic.get("status") in ["OK", "WARNING"]:
        log.info("Floorboard logic refined call successful for .exp data preparation.")
        summary_from_logic = floor_results_from_logic.get("summary", {})
        floorboard_data_for_exp_generation['y_offset_for_floorboards'] = y_offset_abs
        floorboard_data_for_exp_generation['target_span_to_fill'] = span_to_fill
        floorboard_data_for_exp_generation['standard_board_actual_width'] = summary_from_logic.get('chosen_standard_actual_width_y', 0.0)
        floorboard_data_for_exp_generation['final_gap'] = summary_from_logic.get('final_gap_y', 0.0)
        
        current_ui_parameters['chosen_standard_floorboard_actual_width'] = summary_from_logic.get('chosen_standard_actual_width_y', 0.0)
        current_ui_parameters['calculated_standard_floorboard_count'] = summary_from_logic.get('total_standard_boards_count', 0)
        current_ui_parameters['calculated_custom_floorboard_width'] = summary_from_logic.get('custom_board_actual_width_y',0.0)
        current_ui_parameters['calculated_custom_floorboard_count'] = summary_from_logic.get('custom_board_count', 0)
        current_ui_parameters['calculated_final_floor_gap'] = summary_from_logic.get('final_gap_y', 0.0)

        all_boards_detail_list = floor_results_from_logic.get("boards_layout_details", [])
        front_boards_list = []
        back_boards_list = []
        custom_board_dict = {}
        
        # Segregate boards for N-instance slots
        # Assumes boards_layout_details is sorted by y_pos_relative_start_edge
        std_boards_collected = []
        for board in all_boards_detail_list:
            abs_lead_edge_y = y_offset_abs + board.get('y_pos_relative_start_edge', 0.0)
            board_data_for_list = {'width': board.get('actual_width_y',0.0), 'y_pos_abs_leading_edge': abs_lead_edge_y}
            if board.get('type') == 'custom':
                custom_board_dict = board_data_for_list
            elif board.get('type') == 'standard':
                std_boards_collected.append(board_data_for_list)
        
        num_std_total = len(std_boards_collected)
        num_front = math.ceil(num_std_total / 2.0)
        
        front_boards_list = std_boards_collected[:int(num_front)]
        back_boards_list = std_boards_collected[int(num_front):]
        # Back boards y_pos_abs_leading_edge should be correct as they were added from the "back" by logic

        floorboard_data_for_exp_generation['front_boards'] = front_boards_list
        floorboard_data_for_exp_generation['back_boards'] = back_boards_list 
        floorboard_data_for_exp_generation['custom_board'] = custom_board_dict
    else:
        log.warning("Floorboard logic did not run successfully. .exp file may have default/zero floorboard slot parameters.")
        st.warning("Floorboard calculation failed or module returned no data. Floorboard expressions in .exp might be incorrect.")
else:
    st.warning("Core logic modules (floorboard_logic, skid_logic, config) not fully loaded. Floorboard data for .exp will be minimal.")


# --- Action Buttons ---
col_actions1_main, col_actions2_main, col_actions3_main = st.columns([1,1.5,1.5])

with col_actions1_main:
    if st.button("💾 Save UI Params", key="save_params_button_main_final_v3", help="Saves current UI parameters to a JSON file."):
        try:
            json_filename = f"parameters_ui_snapshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            exp_dir_check = os.path.dirname(FIXED_EXP_FILEPATH) 
            if exp_dir_check and not os.path.exists(exp_dir_check): os.makedirs(exp_dir_check)
            json_filepath = os.path.join(exp_dir_check, json_filename)
            
            with open(json_filepath, 'w') as f_json: json.dump(current_ui_parameters, f_json, indent=4)
            st.success(f"Parameters saved to {json_filepath}")
        except Exception as e: st.error(f"Error saving parameters to JSON: {e}")

with col_actions2_main:
    if st.button("🚀 Update .exp File (Skids & Floorboards)", key="update_exp_button_main_final_v3", use_container_width=True):
        if not all(current_ui_parameters.get(key) is not None for key in ['product_weight', 'product_width', 'product_length']):
            st.error("Error: Product weight, width, and length must be provided.")
        elif not skid_results_for_processing or skid_results_for_processing.get('status') != 'OK':
            st.error("Skid calculation failed. Cannot generate .exp file with accurate skid data.")
        else:
            exp_file_content_str = generate_nx_exp_file_content(current_ui_parameters, skid_results_for_processing, floorboard_data_for_exp_generation)
            try:
                exp_dir_check = os.path.dirname(FIXED_EXP_FILEPATH)
                if exp_dir_check and not os.path.exists(exp_dir_check): os.makedirs(exp_dir_check)
                with open(FIXED_EXP_FILEPATH, 'w') as f: f.write(exp_file_content_str)
                st.success(f".exp file updated at: {FIXED_EXP_FILEPATH}")
            except Exception as e: st.error(f"Error updating .exp file: {e}")

with col_actions3_main:
    if st.button("📊 Download Detailed Floorboard CSV", key="download_floorboard_csv_v3", use_container_width=True):
        if floor_results_from_logic and floor_results_from_logic.get("status") in ["OK", "WARNING"] and skid_results_for_processing.get('status') == 'OK':
            csv_rows = []
            all_boards_for_csv = floor_results_from_logic.get("boards_layout_details", [])
            y_offset_abs_csv = floorboard_data_for_exp_generation.get('y_offset_for_floorboards',0.0)
            
            skid_h_csv = skid_results_for_processing.get('skid_height', 3.5)
            floor_thickness_csv = current_ui_parameters.get('floor_lumbar_thickness', 1.5)

            for idx, board_data in enumerate(all_boards_for_csv):
                abs_leading_edge_y = y_offset_abs_csv + board_data.get('y_pos_relative_start_edge', 0.0)
                pos_y_center = abs_leading_edge_y + (board_data.get('actual_width_y', 0.0) / 2.0)

                csv_rows.append({
                    "ComponentName": f"Floorboard_{board_data.get('nominal_size', 'Custom').replace('x','_')}_{idx+1}",
                    "TemplateFile": "FLOORBOARD_LUMBER_TEMPLATE.prt",
                    "PosX_Center": 0.0,
                    "PosY_Center": round(pos_y_center, 3),
                    "PosZ_Bottom": round(skid_h_csv, 3),
                    "INPUT_Floorboard_Length_X": round(board_data.get('length_x', 0.0), 3),
                    "INPUT_Floorboard_Width_Y": round(board_data.get('actual_width_y', 0.0), 3),
                    "INPUT_Floorboard_Thickness_Z": round(board_data.get('thickness_z', 0.0), 3)
                })
            
            if csv_rows:
                df = pd.DataFrame(csv_rows)
                csv_data_out = df.to_csv(index=False).encode('utf-8')
                st.download_button( 
                    label="📥 Click to Download CSV",
                    data=csv_data_out,
                    file_name=f"floorboard_details_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime='text/csv',
                    key=f"final_floorboard_csv_dl_btn_{datetime.datetime.now().timestamp()}" 
                )
            else: st.warning("No detailed floorboard data to generate CSV.")
        else: st.warning("Floorboard or Skid calculations not run successfully or no data. Cannot generate CSV.")

st.markdown("---")
st.caption(f"AutoCrate Wizard v{APP_VERSION}")
log.info(f"Streamlit app v{APP_VERSION} (Floorboard N-Instance Strategy Corrected) exec finished.")