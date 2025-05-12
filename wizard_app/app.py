# wizard_app/app.py
# VERSION: Meeting Mode - Skid .exp to Fixed Relative Path - WITH CORRECTIONS

import sys
import os
import logging
import math 
import streamlit as st
import pandas as pd 
import json
import datetime

# --- Path Setup ---
if __name__ == "__main__" and __package__ is None:
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_script_dir)
    if parent_dir not in sys.path: sys.path.insert(0, parent_dir)
    __package__ = os.path.basename(current_script_dir)

# --- Page Config & Logging ---
APP_VERSION_FALLBACK = "0.8.16_MeetingFixes" 
log = logging.getLogger(__package__ if __package__ else "wizard_app")
if not log.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log.info(f"Logger '{log.name}' configured with basicConfig.")

# --- Attempt to Import Project Config ---
APP_INITIALIZATION_SUCCESS = True
config = None
APP_VERSION = APP_VERSION_FALLBACK
try:
    from . import config 
    APP_VERSION = getattr(config, 'VERSION', APP_VERSION_FALLBACK)
    log.info(f"Imported config (relative) - Version: {APP_VERSION}")
except ImportError:
    log.warning("Could not import config.py. Some default values might be used.")

st.set_page_config(layout="wide", page_title=f"AutoCrate Wizard v{APP_VERSION} (Skid .exp Fixed Path)", page_icon="⚙️")

# --- Function to generate .exp file content (focused on skids) ---
def generate_nx_exp_file_content_for_skids(product_params):
    """
    Generates the content for an NX .exp file, focusing on Skid Layout,
    based on product parameters.
    """
    p_weight = product_params.get('product_weight', 2500.0)
    p_width = product_params.get('product_width', 90.0)
    p_length = product_params.get('product_length', 90.0)
    p_actual_height = product_params.get('product_actual_height', 48.0)
    p_clearance_side = product_params.get('clearance_side', 2.0)
    p_clearance_above = product_params.get('clearance_above_product', 1.5)
    p_panel_thickness = product_params.get('panel_thickness', 0.25)
    
    p_wall_cleat_thickness = product_params.get('wall_cleat_thickness', 0.75)
    p_wall_cleat_width = product_params.get('wall_cleat_width', 3.5)
    
    p_floor_lumbar_thickness = product_params.get('floor_lumbar_thickness', 1.5)
    p_example_floorboard_width = product_params.get('example_floorboard_width', 7.25)

    p_cap_cleat_thickness = product_params.get('cap_cleat_thickness', 0.75)
    p_cap_cleat_width = product_params.get('cap_cleat_width', 3.5)
    p_max_top_cleat_spacing = product_params.get('max_top_cleat_spacing', 24.0)

    generation_time = product_params.get('generation_timestamp', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    exp_content = []
    exp_content.append("// NX Expressions for AutoCrate Wizard - Skid Focus")
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
    exp_content.append(f"[Inch]wall_cleat_thickness = {p_wall_cleat_thickness:.3f}   // Wall Cleat Actual Thickness")
    exp_content.append(f"[Inch]wall_cleat_width = {p_wall_cleat_width:.2f} // Wall Cleat Actual Width")
    exp_content.append(f"[Inch]floor_lumbar_thickness = {p_floor_lumbar_thickness:.3f} // Floorboard Actual Thickness")
    exp_content.append(f"[Inch]example_floorboard_width = {p_example_floorboard_width:.3f} // Example fixed floorboard width")
    exp_content.append(f"[Inch]cap_cleat_thickness = {p_cap_cleat_thickness:.3f} // Cap Cleat Actual Thickness")
    exp_content.append(f"[Inch]cap_cleat_width = {p_cap_cleat_width:.2f}     // Cap Cleat Actual Width")
    exp_content.append(f"[Inch]max_cap_cleat_spacing_rule = {p_max_top_cleat_spacing:.2f} // Max rule for cap cleats")

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
    exp_content.append("// 3. SKID LAYOUT (NX Expressions - Focused for current goal)")
    exp_content.append("// =============================")
    exp_content.append("[Inch]INPUT_Skid_Nominal_Width = if(product_weight <= 500[lbm]) then (2.5[Inch]) else if(product_weight <= 4500[lbm]) then (3.5[Inch]) else (5.5[Inch])")
    exp_content.append("[Inch]RULE_Max_Skid_Spacing = if(product_weight <= 500[lbm]) then (30.0[Inch]) else if(product_weight <= 4500[lbm]) then (30.0[Inch]) else if(product_weight <= 6000[lbm]) then (41.0[Inch]) else if(product_weight <= 12000[lbm]) then (28.0[Inch]) else if(product_weight <= 20000[lbm]) then (24.0[Inch]) else (0[Inch])")
    exp_content.append("[Inch]INPUT_Skid_Nominal_Height = 3.5")
    exp_content.append("is_overweight_flag = if(product_weight > 20000[lbm]) then (1) else (0)")
    exp_content.append("is_skid_width_error_flag = if(skid_usable_width_ID < INPUT_Skid_Nominal_Width - float_tolerance_const) then (1) else (0)")
    exp_content.append("[Inch]skid_centerline_span_calc = skid_usable_width_ID - INPUT_Skid_Nominal_Width")
    exp_content.append("theoretical_min_skid_count_calc = if(RULE_Max_Skid_Spacing > float_tolerance_const) then (ceil(skid_centerline_span_calc / RULE_Max_Skid_Spacing) + 1) else (999)")
    # CORRECTED CALC_Skid_Count line:
    exp_content.append("CALC_Skid_Count = if(is_overweight_flag == 1) then (0) else (if(is_skid_width_error_flag == 1) then (0) else (if(skid_usable_width_ID < (INPUT_Skid_Nominal_Width * 2) - float_tolerance_const) then (1) else (max(2, theoretical_min_skid_count_calc))))")
    exp_content.append("[Inch]CALC_Skid_Pitch = if(CALC_Skid_Count > 1) then (skid_centerline_span_calc / (CALC_Skid_Count - 1)) else (0.0[Inch])")
    exp_content.append("[Inch]CALC_First_Skid_Pos_X = if(CALC_Skid_Count == 1) then (0.0[Inch]) else (-(CALC_Skid_Pitch * (CALC_Skid_Count - 1)) / 2.0)")
    exp_content.append("[Inch]CALC_Overall_Skid_Span = if(CALC_Skid_Count == 0) then (0[Inch]) else (if(CALC_Skid_Count == 1) then (INPUT_Skid_Nominal_Width) else ((CALC_Skid_Count - 1) * CALC_Skid_Pitch + INPUT_Skid_Nominal_Width))")
    exp_content.append("[Inch]INPUT_Skid_Actual_Length = crate_length_OD") 

    exp_content.append("\n// --- Expressions for individual skid positions (Example for up to 10 skids) ---")
    for i in range(1, 11): 
        exp_content.append(f"[Inch]POS_Skid_{i}_X = if(CALC_Skid_Count >= {i}) then (CALC_First_Skid_Pos_X + ({i-1} * CALC_Skid_Pitch)) else (0[Inch]) // Position for Skid {i} (0 if not used)")
    
    exp_content.append("\n// End of AutoCrate Wizard Expressions (Skid Focus)")
    return "\n".join(exp_content)

# --- Initialize session state for direct input values if not present ---
default_params_for_ui = {
    'product_weight': 1800.0, 'product_width': 75.0, 'product_length': 110.0,
    'product_actual_height': 55.0, 'clearance_side': 2.5, 'clearance_above_product': 2.0,
    'panel_thickness': 0.75, 'wall_cleat_thickness': 0.75, 'wall_cleat_width': 3.5,
    'floor_lumbar_thickness': 1.5, 'example_floorboard_width': 7.25,
    'cap_cleat_thickness': 0.75, 'cap_cleat_width': 3.5, 'max_top_cleat_spacing': 24.0
}
for key, value in default_params_for_ui.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Streamlit UI ---
st.title(f"⚙️ AutoCrate Wizard v{APP_VERSION} (Skid .exp Fixed Path)")
st.caption("Enter parameters below and click 'Update Skid .exp File'.")

st.subheader("Product & Crate Parameters")
c1, c2, c3 = st.columns(3)
with c1:
    st.session_state.product_weight = st.number_input("Product Weight (lbs)", min_value=1.0, max_value=20000.0, value=st.session_state.product_weight, step=10.0, format="%.1f")
    st.session_state.product_width = st.number_input("Product Width (in)", min_value=1.0, max_value=200.0, value=st.session_state.product_width, step=0.5, format="%.2f")
    st.session_state.product_length = st.number_input("Product Length (in)", min_value=1.0, max_value=200.0, value=st.session_state.product_length, step=0.5, format="%.2f")
    st.session_state.product_actual_height = st.number_input("Product Actual Height (in)", min_value=1.0, max_value=150.0, value=st.session_state.product_actual_height, step=0.5, format="%.2f")
with c2:
    st.session_state.clearance_side = st.number_input("Clearance Side (in)", min_value=0.0, value=st.session_state.clearance_side, step=0.1, format="%.2f")
    st.session_state.clearance_above_product = st.number_input("Clearance Above Product (in)", min_value=0.0, value=st.session_state.clearance_above_product, step=0.1, format="%.2f")
    st.session_state.panel_thickness = st.number_input("Panel Sheathing Thickness (in)", min_value=0.01, value=st.session_state.panel_thickness, step=0.01, format="%.3f")
    st.session_state.floor_lumbar_thickness = st.number_input("Floorboard Actual Thickness (in)", min_value=0.1, value=st.session_state.floor_lumbar_thickness, step=0.01, format="%.3f")
    st.session_state.example_floorboard_width = st.number_input("Example Floorboard Width (in)", min_value=1.0, value=st.session_state.example_floorboard_width, step=0.01, format="%.3f")
with c3:
    st.session_state.wall_cleat_thickness = st.number_input("Wall Cleat Thickness (in)", min_value=0.1, value=st.session_state.wall_cleat_thickness, step=0.01, format="%.3f")
    st.session_state.wall_cleat_width = st.number_input("Wall Cleat Width (in)", min_value=0.1, value=st.session_state.wall_cleat_width, step=0.1, format="%.2f")
    st.session_state.cap_cleat_thickness = st.number_input("Cap Cleat Thickness (in)", min_value=0.1, value=st.session_state.cap_cleat_thickness, step=0.01, format="%.3f")
    st.session_state.cap_cleat_width = st.number_input("Cap Cleat Width (in)", min_value=0.1, value=st.session_state.cap_cleat_width, step=0.1, format="%.2f")
    # CORRECTED line for max_top_cleat_spacing input:
    st.session_state.max_top_cleat_spacing = st.number_input("Max Cap Cleat Spacing (in)", min_value=1.0, value=st.session_state.max_top_cleat_spacing, step=1.0, format="%.2f")

st.markdown("---")

# --- Actions ---
try:
    APP_DIR = os.path.dirname(os.path.abspath(__file__)) 
    PROJECT_ROOT = os.path.dirname(APP_DIR) 
    TARGET_SUBFOLDER = "nx_part_templates" 
    TARGET_DIR = os.path.join(PROJECT_ROOT, TARGET_SUBFOLDER)
    
    EXP_FILENAME = "AutoCrate_Skids_Expressions.exp" 
    FIXED_EXP_FILEPATH = os.path.join(TARGET_DIR, EXP_FILENAME)
    
    st.info(f"ℹ️ The .exp file will be updated at: {FIXED_EXP_FILEPATH}")

except Exception as e:
    log.error(f"Error calculating relative path for .exp file: {e}. Defaulting to current directory.")
    FIXED_EXP_FILEPATH = "AutoCrate_Skids_Expressions.exp" 
    st.warning(f"Could not determine project relative path. .exp file will be saved to: {os.path.abspath(FIXED_EXP_FILEPATH)}")


col_actions1, col_actions2 = st.columns(2)
current_parameters_for_processing = {key: st.session_state.get(key) for key in default_params_for_ui.keys()}
current_parameters_for_processing['generation_timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with col_actions1:
    if st.button("💾 Save Current Parameters to JSON (Optional)", key="save_params_button_final_corrected"):
        try:
            json_filename = f"parameters_ui_snapshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            json_filepath = os.path.join(os.path.dirname(FIXED_EXP_FILEPATH), json_filename) # Save JSON in same target dir

            if not os.path.exists(os.path.dirname(json_filepath)): # Ensure dir exists
                 os.makedirs(os.path.dirname(json_filepath))

            with open(json_filepath, 'w') as f_json:
                json.dump(current_parameters_for_processing, f_json, indent=4)
            st.success(f"Parameters saved to {json_filepath}")
            log.info(f"Parameters saved to {json_filepath}")
        except Exception as e:
            st.error(f"Error saving parameters to JSON: {e}")
            log.error(f"Error saving parameters to JSON: {e}", exc_info=True)

with col_actions2:
    if st.button("🚀 Update Skid .exp File", key="update_exp_button_final_corrected", use_container_width=True):
        if not all(current_parameters_for_processing.get(key) is not None for key in ['product_weight', 'product_width', 'product_length']):
            st.error("Error: Product weight, width, and length must be provided.")
        else:
            exp_file_content_str = generate_nx_exp_file_content_for_skids(current_parameters_for_processing)
            try:
                exp_dir_check = os.path.dirname(FIXED_EXP_FILEPATH)
                if exp_dir_check and not os.path.exists(exp_dir_check):
                    os.makedirs(exp_dir_check)
                    log.info(f"Created directory for .exp file during button click: {exp_dir_check}")

                with open(FIXED_EXP_FILEPATH, 'w') as f:
                    f.write(exp_file_content_str)
                st.success(f"Skid .exp file updated successfully at: {FIXED_EXP_FILEPATH}")
                log.info(f".exp file updated at '{FIXED_EXP_FILEPATH}'.")
            except PermissionError:
                st.error(f"Permission denied: Could not write to '{FIXED_EXP_FILEPATH}'. Please check path and permissions.")
                log.error(f"Permission denied writing to '{FIXED_EXP_FILEPATH}'.")
            except Exception as e:
                st.error(f"Error updating .exp file: {e}")
                log.error(f"Error updating .exp file at '{FIXED_EXP_FILEPATH}': {e}", exc_info=True)

st.markdown("---")
st.caption(f"AutoCrate Wizard v{APP_VERSION}")
log.info(f"Streamlit app v{APP_VERSION} (Meeting Mode - Fixed Path, Corrected) exec finished.")