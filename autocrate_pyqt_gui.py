# autocrate_pyqt_gui.py
# Version: 0.8.34_PyQt_InputConsolidation
# Main application for AutoCrate using PyQt6 for the GUI

import sys
import os
import json
import datetime
import logging
import math 

# --- Setup Logging ---
log = logging.getLogger(__name__)
if not log.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Add Project Root to Python Path ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_PATH = current_script_dir 
if PROJECT_ROOT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_PATH)
log.info(f"Project root added to sys.path: {PROJECT_ROOT_PATH}")

# --- Import Core Logic Modules ---
try:
    from wizard_app import config
    from wizard_app import skid_logic
    from wizard_app import floorboard_logic
    log.info("Successfully imported config, skid_logic, floorboard_logic using 'from wizard_app import ...'.")
except ImportError as e:
    log.error(f"CRITICAL ERROR: Could not import core logic modules from 'wizard_app': {e}")
    config = None
    skid_logic = None
    floorboard_logic = None
except Exception as e_gen:
    log.error(f"An unexpected error occurred during core logic module imports: {e_gen}", exc_info=True)
    config = None
    skid_logic = None
    floorboard_logic = None

# --- Import PyQt6 ---
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QMessageBox,
        QScrollArea, QGroupBox, QFrame, QFileDialog, QStatusBar
    )
    from PyQt6.QtCore import Qt, QLocale
    from PyQt6.QtGui import QDoubleValidator, QIntValidator, QFont, QPalette, QColor
except ImportError:
    log.error("CRITICAL ERROR: PyQt6 is not installed. Please install it using 'pip install PyQt6'")
    sys.exit("PyQt6 not found. Please install it: pip install PyQt6")


# --- .exp File Generation Logic ---
def generate_nx_exp_file_content_for_pyqt(product_params, skid_results_for_exp, floorboard_exp_data):
    p_weight = product_params.get('product_weight', 2500.0)
    p_width = product_params.get('product_width', 90.0)
    p_length = product_params.get('product_length', 90.0)
    p_actual_height = product_params.get('product_actual_height', 48.0)
    p_clearance_side = product_params.get('clearance_side', 2.0)
    p_clearance_above = product_params.get('clearance_above_product', 1.5)
    p_panel_thickness = product_params.get('panel_thickness', 0.25) # Default updated
    # Use the single cleat_thickness for both wall and cap in .exp file
    p_cleat_thickness_unified = product_params.get('cleat_thickness', 0.75) 
    chosen_std_fb_nominal_from_params = product_params.get('chosen_standard_floorboard_nominal', "N/A")
    allow_3x4_skids_info = product_params.get('allow_3x4_skids', True) 
    
    float_tol = 1e-6 
    if config and hasattr(config, 'FLOAT_TOLERANCE'): 
        float_tol = config.FLOAT_TOLERANCE

    generation_time = product_params.get('generation_timestamp', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    exp_content = []
    exp_content.append("// NX Expressions for AutoCrate Wizard - Skids & Floorboards (N-Instance Strategy)")
    exp_content.append(f"// Parameters from PyQt GUI at: {generation_time}")
    exp_content.append(f"// Allow 3x4 Skids for Light Loads Option: {'Enabled' if allow_3x4_skids_info else 'Disabled'}")
    
    exp_content.append("\n// =============================")
    exp_content.append("// 1. USER CONTROLS (Values from UI)")
    exp_content.append("// =============================")
    exp_content.append(f"[lbm]product_weight = {p_weight:.1f}  // Product Weight")
    exp_content.append(f"[Inch]product_width = {p_width:.2f}     // Product Width - across skids (Max 120)")
    exp_content.append(f"[Inch]product_length = {p_length:.2f}    // Product Length - along skids (Max 120)")
    exp_content.append(f"[Inch]product_actual_height = {p_actual_height:.2f} // Product Actual Height (for content) (Max 120)")
    exp_content.append(f"[Inch]clearance_side = {p_clearance_side:.2f}     // Clearance per Side (product to inner wall face)")
    exp_content.append(f"[Inch]clearance_above_product = {p_clearance_above:.2f} // Clearance above product")
    exp_content.append(f"[Inch]panel_thickness = {p_panel_thickness:.3f}   // Panel Sheathing Thickness (Default 0.25)")
    exp_content.append(f"[Inch]cleat_thickness = {p_cleat_thickness_unified:.3f}   // General Cleat Actual Thickness") # Consolidated
    exp_content.append(f"[Inch]wall_cleat_width = {product_params.get('wall_cleat_width', 3.5):.2f} // Wall Cleat Actual Width")
    exp_content.append(f"[Inch]floor_lumbar_thickness = {product_params.get('floor_lumbar_thickness', 1.5):.3f} // Floorboard Actual Thickness")
    exp_content.append(f"// CHOSEN_Std_Floorboard_Nominal_UI: \"{chosen_std_fb_nominal_from_params}\" (Selected in UI - For Info Only)") 
    exp_content.append(f"[Inch]cap_cleat_width = {product_params.get('cap_cleat_width', 3.5):.2f}     // Cap Cleat Actual Width")
    exp_content.append(f"[Inch]max_cap_cleat_spacing_rule = {product_params.get('max_top_cleat_spacing', 24.0):.2f} // Max rule for cap cleats")

    exp_content.append("\n// --- Constants (Informational) ---")
    exp_content.append("[Inch]min_skid_height_const = 3.5")
    exp_content.append(f"[Inch]float_tolerance_const = {float_tol:.6f}")

    exp_content.append("\n// ===========================================")
    exp_content.append("// 2. CALCULATED CRATE AND USABLE DIMENSIONS (NX Expressions)")
    exp_content.append("// ===========================================")
    # Use the single 'cleat_thickness' for these calculations
    exp_content.append("[Inch]crate_width_OD = product_width + 2 * (clearance_side + panel_thickness + cleat_thickness)")
    exp_content.append("[Inch]crate_length_OD = product_length + 2 * (clearance_side + panel_thickness + cleat_thickness)")
    exp_content.append("[Inch]skid_usable_width_ID = crate_width_OD - 2 * (panel_thickness + cleat_thickness)")

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
    if skid_count_val == 1: first_skid_pos_x_py_calc = 0.0
    elif skid_count_val > 1:
        total_centerline_span_py = skid_spacing_val * (skid_count_val - 1)
        first_skid_pos_x_py_calc = -total_centerline_span_py / 2.0
    exp_content.append(f"[Inch]CALC_First_Skid_Pos_X = {first_skid_pos_x_py_calc:.4f}")
    
    _overall_skid_span_py = 0.0
    skid_width_val = skid_results_for_exp.get('skid_width', 0.0)
    if skid_count_val == 0: _overall_skid_span_py = 0.0
    elif skid_count_val == 1: _overall_skid_span_py = skid_width_val
    elif skid_count_val > 1: _overall_skid_span_py = (skid_count_val - 1) * skid_spacing_val + skid_width_val
    exp_content.append(f"[Inch]CALC_Overall_Skid_Span = {_overall_skid_span_py:.3f}")
    exp_content.append("[Inch]INPUT_Skid_Actual_Length = crate_length_OD") 

    exp_content.append("\n// ===========================================")
    exp_content.append("// 4. FLOORBOARD PARAMETERS (for N-Instance Suppression Strategy)")
    exp_content.append("// ===========================================")
    # CALC_Floor_Start_Y_Offset_Abs will use the single 'cleat_thickness' from user controls
    exp_content.append("[Inch]CALC_Floor_Start_Y_Offset_Abs = cleat_thickness + panel_thickness") 
    exp_content.append(f"[Inch]CALC_Floor_Target_Layout_Span = {floorboard_exp_data.get('target_span_to_fill', 0.0):.3f}")
    exp_content.append("[Inch]CALC_Floor_Board_Length_Across_Skids = CALC_Overall_Skid_Span")
    exp_content.append("[Inch]INPUT_Floorboard_Actual_Thickness = floor_lumbar_thickness")
    exp_content.append(f"[Inch]CHOSEN_Std_Floorboard_Actual_Width_Val = {floorboard_exp_data.get('standard_board_actual_width', 0.0):.3f}")
    exp_content.append(f"// INFO_Python_Std_Floorboard_Count = {product_params.get('calculated_standard_floorboard_count',0)}")
    exp_content.append(f"// INFO_Python_Custom_Floorboard_Count = {product_params.get('calculated_custom_floorboard_count',0)}")
    exp_content.append(f"// INFO_Python_Custom_Floorboard_Width = {product_params.get('calculated_custom_floorboard_width',0.0):.3f} [Inch]")
    exp_content.append(f"// INFO_Python_Final_Floor_Gap = {product_params.get('calculated_final_floor_gap',0.0):.4f} [Inch]")

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
    suppress_custom = 0 if custom_data and custom_width_val > float_tol else 1
    width_custom = custom_width_val if not suppress_custom else 0.0
    y_pos_abs_custom = custom_data.get('y_pos_abs_leading_edge', 0.0) if not suppress_custom else 0.0
    exp_content.append(f"FB_Custom_Suppress_Flag = {suppress_custom}")
    exp_content.append(f"[Inch]FB_Custom_Actual_Width = {width_custom:.3f}")
    exp_content.append(f"[Inch]FB_Custom_Y_Pos_Abs = {y_pos_abs_custom:.3f} // Leading Edge Y")
    exp_content.append(f"[Inch]CALC_Floor_Final_Gap_Debug = {floorboard_exp_data.get('final_gap', 0.0):.4f} // For verification (Python calc)")

    exp_content.append("\n// End of AutoCrate Wizard Expressions")
    return "\n".join(exp_content)

# --- Application Stylesheet (same as 0.8.29) ---
APP_STYLESHEET = """
    QMainWindow, QWidget { 
        background-color: #F0F4F8; 
        font-family: Segoe UI, Arial, sans-serif; 
        color: #1A252F; 
    }
    QGroupBox {
        font-weight: bold; font-size: 10pt; border: 1px solid #B0BEC5; 
        border-radius: 4px; margin-top: 1ex; padding: 1.2ex 8px 8px 8px; 
    }
    QGroupBox::title {
        subcontrol-origin: margin; subcontrol-position: top left; 
        padding: 2px 6px; left: 9px; background-color: #E1E8ED; 
        border: 1px solid #B0BEC5; border-bottom: 1px solid #E1E8ED; 
        border-top-left-radius: 3px; border-top-right-radius: 3px;
        color: #263238; 
    }
    QLabel {
        font-size: 9pt; padding-top: 5px; padding-bottom: 5px;
        color: #263238; font-weight: 500; 
    }
    QLineEdit, QComboBox {
        padding: 5px; border: 1px solid #90A4AE; border-radius: 3px;
        font-size: 9pt; background-color: #FFFFFF; color: #1A252F;            
        selection-background-color: #64B5F6; selection-color: #FFFFFF;           
        min-height: 1.9em; 
    }
    QComboBox::drop-down { border-left: 1px solid #B0BEC5; width: 18px; }
    QCheckBox {
        font-size: 9pt; spacing: 6px; color: #263238;
        padding-top: 5px; padding-bottom: 5px;
    }
    QPushButton {
        font-size: 10pt; font-weight: 500; padding: 8px 16px; 
        border: 1px solid #78909C; border-radius: 3px;
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FAFAFA, stop:1 #E0E0E0);
        color: #263238; min-width: 100px; 
    }
    QPushButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E8E8E8);
        border-color: #546E7A; 
    }
    QPushButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D0D0D0, stop:1 #C8C8C8);
    }
    QPushButton#GenerateExpButton { 
        font-weight: bold; font-size: 10pt; 
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5cb85c, stop:1 #4cae4c); 
        color: white; border-color: #3d8b3d; min-width: 120px; 
    }
    QPushButton#GenerateExpButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #67c467, stop:1 #52b852);
    }
    QPushButton#GenerateExpButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #45a045, stop:1 #409140);
    }
    QStatusBar { font-size: 9pt; color: #37474F; }
"""

class AutoCrateApp(QMainWindow):
    EXP_FILENAME = "AutoCrate_Expressions.exp" 
    # Define product_params_list at class level for access in initUI and collect_parameters
    # (Label Text, dict key, default, type, precision, min_val, max_val, tooltip)
    MAX_PRODUCT_DIM_CONST = 120.0 # Define as a constant
    
    parameter_definitions = [
        ("Prod. Weight (lbs):", 'product_weight', 1800.0, "float", 1, 1.0, 20000.0, "Total weight of the product."),
        ("Prod. Width (in):", 'product_width', 75.0, "float", 2, 1.0, MAX_PRODUCT_DIM_CONST, f"Product dimension across skids (Max {MAX_PRODUCT_DIM_CONST:.1f})."),
        ("Prod. Length (in):", 'product_length', 110.0, "float", 2, 1.0, MAX_PRODUCT_DIM_CONST, f"Product dimension along skids (Max {MAX_PRODUCT_DIM_CONST:.1f})."),
        ("Prod. Height (in):", 'product_actual_height', 55.0, "float", 2, 1.0, MAX_PRODUCT_DIM_CONST, f"Actual height of the product (Max {MAX_PRODUCT_DIM_CONST:.1f})."),
        ("Clearance Side (in):", 'clearance_side', 2.5, "float", 2, 0.0, 20.0, "Clearance (W & L) to inner wall."),
        ("Clearance Above (in):", 'clearance_above_product', 2.0, "float", 2, 0.0, 20.0, "Clearance above product top."),
        ("Panel Thickness (in):", 'panel_thickness', 0.25, "float", 3, 0.01, 2.0, "Sheathing thickness (Default 0.25)."), # Default Changed
        ("Cleat Thickness (in):", 'cleat_thickness', 0.75, "float", 3, 0.01, 3.0, "Actual thickness for ALL cleats (wall, cap)."), # Consolidated
        ("Wall Cleat Width (in):", 'wall_cleat_width', 3.5, "float", 2, 0.1, 12.0, "Actual width of wall cleats."),
        # ("Floorboard Thk (in):", 'floor_lumbar_thickness', 1.5, "float", 3, 0.1, 3.0, "Actual thickness of floorboards."), # This is still used by floorboard logic
        ("Cap Cleat Width (in):", 'cap_cleat_width', 3.5, "float", 2, 0.1, 12.0, "Actual width of cap cleats."),
        ("Max Cap Cleat Space (in):", 'max_top_cleat_spacing', 24.0, "float", 2, 1.0, 60.0, "Max C-C spacing for cap cleats.")
    ]
    # Add Floorboard Thk separately as it's not in the main loop for product_params_group
    floorboard_thk_def = ("Floorboard Thk (in):", 'floor_lumbar_thickness', 1.5, "float", 3, 0.1, 3.0, "Actual thickness of floorboards.")


    def __init__(self):
        super().__init__()
        self.app_version = "0.8.34" # Updated version
        if config and hasattr(config, 'VERSION'): 
            self.app_version = config.VERSION
        
        self.setWindowTitle(f"AutoCrate Wizard V8 (PyQt {self.app_version}) - Exp Generator")
        self.setMinimumSize(780, 650) 
        self.setStyleSheet(APP_STYLESHEET) 

        QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

        self.input_widgets = {}
        self.exp_output_path_edit = QLineEdit() 
        self.initUI()
        self.set_default_exp_output_path()

    def set_default_exp_output_path(self):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            executable_dir = os.path.dirname(sys.executable)
            default_path = os.path.join(executable_dir, self.EXP_FILENAME)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            target_dir = os.path.join(script_dir, "nx_part_templates")
            if not os.path.exists(target_dir):
                try: os.makedirs(target_dir); log.info(f"Created directory: {target_dir}")
                except Exception as e:
                    log.error(f"Could not create target directory {target_dir}: {e}")
                    target_dir = script_dir 
            default_path = os.path.join(target_dir, self.EXP_FILENAME)
        self.exp_output_path_edit.setText(os.path.normpath(default_path))
        log.info(f"Default .exp file output path set to: {default_path}")

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        overall_layout = QVBoxLayout(self.central_widget)
        overall_layout.setContentsMargins(12, 12, 12, 12); overall_layout.setSpacing(12) 

        intro_label = QLabel(
            f"<h2><b>AutoCrate Wizard</b> <span style='font-size:10pt; font-weight:normal;'>v{self.app_version}</span></h2>"
            "<p style='font-size:9pt; color:#4a5568; margin-bottom:10px;'>Generates an NX Expression File (.exp) for parametrically "
            "driving industrial shipping crate designs (skids & floorboards). "
            "Enter parameters below to define your product and construction preferences.</p>"
        )
        intro_label.setWordWrap(True); overall_layout.addWidget(intro_label)

        main_content_widget = QWidget(); main_content_layout = QHBoxLayout(main_content_widget)
        main_content_layout.setSpacing(15); main_content_layout.setContentsMargins(0,0,0,0)

        left_column_widget = QWidget(); left_column_layout = QVBoxLayout(left_column_widget)
        left_column_layout.setSpacing(10); left_column_layout.setContentsMargins(0,0,0,0)

        product_params_group = QGroupBox("Product & General Crate Parameters")
        product_params_layout = QGridLayout(); product_params_layout.setSpacing(7); 
        product_params_layout.setContentsMargins(10,18,10,10) 
        
        row = 0; col = 0
        for label_text, key, default, val_type, precision, min_val, max_val, tooltip_text in self.parameter_definitions:
            label = QLabel(label_text); label.setToolTip(tooltip_text)
            edit = QLineEdit(str(default)); edit.setToolTip(tooltip_text)
            if val_type == "float":
                validator = QDoubleValidator(min_val, max_val, precision); 
                validator.setNotation(QDoubleValidator.Notation.StandardNotation); 
                edit.setValidator(validator)
            elif val_type == "int": 
                edit.setValidator(QIntValidator(int(min_val), int(max_val)))
            product_params_layout.addWidget(label, row, col * 2, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter) 
            product_params_layout.addWidget(edit, row, (col * 2) + 1)
            self.input_widgets[key] = edit
            col += 1
            if col >= 2: col = 0; row += 1
        
        # Add Floorboard Thickness to this group as well
        label_text, key, default, val_type, precision, min_val, max_val, tooltip_text = self.floorboard_thk_def
        label = QLabel(label_text); label.setToolTip(tooltip_text)
        edit = QLineEdit(str(default)); edit.setToolTip(tooltip_text)
        validator = QDoubleValidator(min_val, max_val, precision); validator.setNotation(QDoubleValidator.Notation.StandardNotation); edit.setValidator(validator)
        product_params_layout.addWidget(label, row, col * 2, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        product_params_layout.addWidget(edit, row, (col*2)+1)
        self.input_widgets[key] = edit


        product_params_group.setLayout(product_params_layout)
        left_column_layout.addWidget(product_params_group)
        
        skid_options_group = QGroupBox("Skid Options")
        skid_options_layout = QVBoxLayout(); skid_options_layout.setContentsMargins(10,15,10,10)
        self.input_widgets['allow_3x4_skids'] = QCheckBox("Allow 3x4 Skids for Light Loads (if applicable by weight rules)")
        self.input_widgets['allow_3x4_skids'].setToolTip("If checked, 3x4 skids may be used for loads under configured threshold.")
        self.input_widgets['allow_3x4_skids'].setChecked(True) 
        skid_options_layout.addWidget(self.input_widgets['allow_3x4_skids'], alignment=Qt.AlignmentFlag.AlignCenter)
        skid_options_group.setLayout(skid_options_layout)
        left_column_layout.addWidget(skid_options_group)
        left_column_layout.addStretch(1) 

        right_column_widget = QWidget(); right_column_layout = QVBoxLayout(right_column_widget)
        right_column_layout.setSpacing(10); right_column_layout.setContentsMargins(0,0,0,0)

        floorboard_params_group = QGroupBox("Floorboard Specifics"); floorboard_params_layout = QGridLayout() 
        floorboard_params_layout.setSpacing(8); floorboard_params_layout.setContentsMargins(10,18,10,10)
        label_std_fb = QLabel("Std. Floorboard Size:"); label_std_fb.setToolTip("Choose one standard lumber size.")
        self.input_widgets['chosen_standard_floorboard_nominal'] = QComboBox(); self.input_widgets['chosen_standard_floorboard_nominal'].setToolTip("Choose one standard lumber size.")
        std_fb_options = ["2x6", "2x8", "2x10", "2x12"]
        if config and hasattr(config, 'ALL_STANDARD_FLOORBOARDS'): std_fb_options = sorted(list(config.ALL_STANDARD_FLOORBOARDS.keys()))
        self.input_widgets['chosen_standard_floorboard_nominal'].addItems(std_fb_options)
        default_fb_nominal = "2x8"
        if default_fb_nominal in std_fb_options: self.input_widgets['chosen_standard_floorboard_nominal'].setCurrentText(default_fb_nominal)
        floorboard_params_layout.addWidget(label_std_fb, 0, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        floorboard_params_layout.addWidget(self.input_widgets['chosen_standard_floorboard_nominal'], 0, 1)
        self.input_widgets['allow_custom_floorboard_fill'] = QCheckBox("Allow Custom Center Fill"); self.input_widgets['allow_custom_floorboard_fill'].setToolTip("Use custom board to minimize center gap.")
        self.input_widgets['allow_custom_floorboard_fill'].setChecked(True)
        floorboard_params_layout.addWidget(self.input_widgets['allow_custom_floorboard_fill'], 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter) 
        floorboard_params_group.setLayout(floorboard_params_layout)
        right_column_layout.addWidget(floorboard_params_group)

        output_path_group = QGroupBox(".exp File Output"); output_path_layout = QGridLayout()
        output_path_layout.setContentsMargins(10,8,10,8); output_path_layout.setSpacing(8)
        output_path_layout.addWidget(QLabel("Save .exp to:"), 0, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.exp_output_path_edit.setReadOnly(True); output_path_layout.addWidget(self.exp_output_path_edit, 0, 1, 1, 2) 
        browse_button = QPushButton("Change..."); browse_button.clicked.connect(self.browse_exp_output_location)
        output_path_layout.addWidget(browse_button, 0, 3)
        output_path_group.setLayout(output_path_layout)
        right_column_layout.addWidget(output_path_group)
        
        right_column_layout.addStretch(1) 

        main_content_layout.addWidget(left_column_widget, 2) 
        main_content_layout.addWidget(right_column_widget, 1) 
        overall_layout.addWidget(main_content_widget) 

        self.generate_button = QPushButton("🚀 Generate & Update .exp File")
        self.generate_button.setObjectName("GenerateExpButton"); self.generate_button.setFixedHeight(40) 
        self.generate_button.clicked.connect(self.run_calculations_and_generate_exp)
        button_container_layout = QHBoxLayout(); button_container_layout.addStretch(); button_container_layout.addWidget(self.generate_button); button_container_layout.addStretch()
        overall_layout.addLayout(button_container_layout) 
        overall_layout.addStretch(0) 

        self.setStatusBar(QStatusBar()); self.statusBar().showMessage("Ready.")

    def browse_exp_output_location(self):
        current_path = self.exp_output_path_edit.text()
        current_dir = os.path.dirname(current_path) if current_path and os.path.isdir(os.path.dirname(current_path)) else os.getcwd()
        
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save .exp File", current_dir)
        if directory: 
            new_path = os.path.join(directory, self.EXP_FILENAME)
            self.exp_output_path_edit.setText(os.path.normpath(new_path))
            log.info(f".exp file output location changed to: {new_path}")
            self.statusBar().showMessage(f"Output path set to: {new_path}", 3000)

    def collect_parameters(self):
        params = {}
        validation_passed = True
        # Use the class-level definition for checking defaults if needed
        for label_text, key, default, val_type, precision, min_val, max_val, tooltip_text in self.parameter_definitions:
            widget = self.input_widgets.get(key)
            if not widget: continue # Should not happen if initUI is correct

            if isinstance(widget, QLineEdit):
                text_value = widget.text()
                if widget.validator() is not None:
                    state, _, _ = widget.validator().validate(text_value, 0)
                    if state != QDoubleValidator.State.Acceptable and state != QIntValidator.State.Acceptable :
                        log.warning(f"Invalid input for {key}: '{text_value}'. Validator state: {state}")
                        QMessageBox.warning(self, "Input Error", 
                                            f"Invalid value entered for '{label_text}'.\n'{text_value}' is not acceptable. Please enter a number within the range [{min_val} - {max_val}].")
                        widget.setFocus() 
                        validation_passed = False
                        break 
                try: 
                    if isinstance(widget.validator(), QDoubleValidator): params[key] = float(text_value)
                    elif isinstance(widget.validator(), QIntValidator): params[key] = int(text_value)
                    else: params[key] = text_value 
                except ValueError: 
                    params[key] = default # Fallback to default if conversion fails after validation (should be rare)
                    log.warning(f"Could not convert QLineEdit value for {key} to number. Using default: {default}")
                    widget.setText(str(default)) # Reset field to default
            # Handle other widget types if they were in parameter_definitions
        
        # Collect parameters not in the main list (checkboxes, comboboxes)
        if validation_passed: # Only collect these if basic validation passed
            for key, widget in self.input_widgets.items():
                if key not in params: # Avoid re-processing QLineEdits
                    if isinstance(widget, QComboBox): params[key] = widget.currentText()
                    elif isinstance(widget, QCheckBox): params[key] = widget.isChecked()
        
        if not validation_passed:
            return None 

        params['generation_timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.info(f"Collected parameters from UI: {params}")
        return params

    def run_calculations_and_generate_exp(self):
        self.statusBar().showMessage("Processing... Please wait.")
        QApplication.processEvents() 

        current_ui_parameters = self.collect_parameters()
        if current_ui_parameters is None: 
            self.statusBar().showMessage("Input validation failed. Please correct errors.", 5000)
            return

        if not all([config, skid_logic, floorboard_logic]):
            QMessageBox.critical(self, "Error", "Core logic modules (config, skid, floorboard) not loaded.")
            self.statusBar().showMessage("Error: Core logic modules missing."); return
        
        self.last_skid_results = {} 
        self.last_floor_results_from_logic = None
        self.last_floorboard_data_for_exp = {}

        try:
            self.last_skid_results = skid_logic.calculate_skid_layout(
                product_weight=current_ui_parameters['product_weight'],
                product_width=current_ui_parameters['product_width'],
                clearance_side=current_ui_parameters['clearance_side'],
                panel_thickness=current_ui_parameters['panel_thickness'],
                cleat_thickness=current_ui_parameters['cleat_thickness'], # Use consolidated cleat_thickness
                allow_3x4_skids_for_light_loads=current_ui_parameters.get('allow_3x4_skids', True)
            )
            if not (self.last_skid_results and self.last_skid_results.get('status') == 'OK'):
                msg = f"Skid calculation failed: {self.last_skid_results.get('message', 'Unknown error')}"
                QMessageBox.warning(self, "Skid Calculation Warning", msg); log.error(msg)
                self.last_skid_results = {'status': 'ERROR', 'skid_width': 3.5, 'skid_height': 3.5, 
                                'max_spacing': 30.0, 'skid_count': 0, 'spacing_actual': 0.0}
        except TypeError as te:
             QMessageBox.critical(self, "Skid Logic Error", f"Skid function signature mismatch. Update skid_logic.py? Error: {te}")
             log.error(f"Skid logic TypeError: {te}", exc_info=True); return
        except Exception as e:
            QMessageBox.critical(self, "Skid Logic Error", f"Skid calculation error: {e}")
            log.error(f"Skid logic error: {e}", exc_info=True)
            self.last_skid_results = {'status': 'ERROR', 'skid_width': 3.5, 'skid_height': 3.5, 
                            'max_spacing': 30.0, 'skid_count': 0, 'spacing_actual': 0.0}

        self.last_floorboard_data_for_exp = {
            'front_boards': [], 'back_boards': [], 'custom_board': {},
            'y_offset_for_floorboards': 0.0, 'target_span_to_fill': 0.0,
            'standard_board_actual_width': 0.0, 'final_gap': 0.0
        }
        floor_results_summary_for_exp_header = {}

        if self.last_skid_results.get('status') == 'OK':
            try:
                # Use consolidated cleat_thickness for y_offset_abs
                y_offset_abs = current_ui_parameters['cleat_thickness'] + current_ui_parameters['panel_thickness']
                span_to_fill = current_ui_parameters['product_length'] + (2 * current_ui_parameters['clearance_side'])
                
                skid_count_val = self.last_skid_results.get('skid_count', 0)
                skid_spacing_val = self.last_skid_results.get('spacing_actual', 0.0)
                skid_width_val = self.last_skid_results.get('skid_width', 0.0)
                board_len_x_val = 0.0
                if skid_count_val == 0: board_len_x_val = 0.0
                elif skid_count_val == 1: board_len_x_val = skid_width_val
                else: board_len_x_val = (skid_count_val - 1) * skid_spacing_val + skid_width_val
                
                self.last_floor_results_from_logic = floorboard_logic.calculate_floorboard_layout_refined(
                    target_span_to_fill_y=span_to_fill,
                    board_length_x=board_len_x_val, 
                    chosen_standard_nominal=current_ui_parameters['chosen_standard_floorboard_nominal'],
                    allow_custom_fill=current_ui_parameters['allow_custom_floorboard_fill'],
                    floorboard_actual_thickness_z=current_ui_parameters['floor_lumbar_thickness']
                )

                if self.last_floor_results_from_logic and self.last_floor_results_from_logic.get("status") in ["OK", "WARNING"]:
                    summary = self.last_floor_results_from_logic.get("summary", {})
                    self.last_floorboard_data_for_exp['y_offset_for_floorboards'] = y_offset_abs
                    self.last_floorboard_data_for_exp['target_span_to_fill'] = span_to_fill
                    self.last_floorboard_data_for_exp['standard_board_actual_width'] = summary.get('chosen_standard_actual_width_y', 0.0)
                    self.last_floorboard_data_for_exp['final_gap'] = summary.get('final_gap_y', 0.0)
                    
                    floor_results_summary_for_exp_header = {
                        'chosen_standard_floorboard_actual_width': summary.get('chosen_standard_actual_width_y', 0.0),
                        'calculated_standard_floorboard_count': summary.get('total_standard_boards_count', 0),
                        'calculated_custom_floorboard_width': summary.get('custom_board_actual_width_y',0.0),
                        'calculated_custom_floorboard_count': summary.get('custom_board_count', 0),
                        'calculated_final_floor_gap': summary.get('final_gap_y', 0.0)
                    }
                    
                    all_boards = self.last_floor_results_from_logic.get("boards_layout_details", [])
                    front_list, back_list, custom_dict = [], [], {}
                    std_processed_count = 0
                    total_std = summary.get('total_standard_boards_count', 0)
                    all_boards.sort(key=lambda b: b.get('y_pos_relative_start_edge', 0.0))

                    for board in all_boards:
                        abs_y = y_offset_abs + board.get('y_pos_relative_start_edge', 0.0)
                        b_data = {'width': board.get('actual_width_y',0.0), 'y_pos_abs_leading_edge': abs_y}
                        if board.get('type') == 'custom': custom_dict = b_data
                        elif board.get('type') == 'standard':
                            if std_processed_count < total_std / 2.0: front_list.append(b_data)
                            else: back_list.append(b_data)
                            std_processed_count += 1
                    self.last_floorboard_data_for_exp['front_boards'] = front_list
                    self.last_floorboard_data_for_exp['back_boards'] = back_list
                    self.last_floorboard_data_for_exp['custom_board'] = custom_dict
                else:
                    QMessageBox.warning(self, "Floorboard Logic Warning", 
                                        f"Floorboard calculation did not return OK/WARNING: {self.last_floor_results_from_logic.get('message', 'Unknown error') if self.last_floor_results_from_logic else 'No result'}")
            except Exception as e:
                QMessageBox.critical(self, "Floorboard Logic Error", f"An error occurred during floorboard calculation: {e}")
                log.error(f"Floorboard logic error: {e}", exc_info=True)
        
        current_ui_parameters.update(floor_results_summary_for_exp_header)
        # Pass the single 'cleat_thickness' to be used for wall_cleat_thickness in .exp generation
        current_ui_parameters['wall_cleat_thickness_for_exp'] = current_ui_parameters.get('cleat_thickness')
        current_ui_parameters['cap_cleat_thickness_for_exp'] = current_ui_parameters.get('cleat_thickness')


        exp_file_content_str = generate_nx_exp_file_content_for_pyqt(current_ui_parameters, self.last_skid_results, self.last_floorboard_data_for_exp)
        
        save_path = self.exp_output_path_edit.text()
        if not save_path: self.set_default_exp_output_path(); save_path = self.exp_output_path_edit.text()

        try:
            exp_dir = os.path.dirname(save_path)
            if exp_dir and not os.path.exists(exp_dir): os.makedirs(exp_dir); log.info(f"Created directory for .exp file: {exp_dir}")
            with open(save_path, 'w') as f: f.write(exp_file_content_str)
            success_msg = f".exp file updated successfully at: {save_path}"
            QMessageBox.information(self, "Success", success_msg)
            self.statusBar().showMessage(success_msg, 5000); log.info(success_msg)
        except PermissionError:
            err_msg = f"Permission denied: Could not write to '{save_path}'."
            QMessageBox.critical(self, "File Error", err_msg + " Check path/permissions.")
            self.statusBar().showMessage(err_msg); log.error(err_msg)
        except Exception as e:
            err_msg = f"Error updating .exp file at '{save_path}': {e}"
            QMessageBox.critical(self, "File Error", err_msg)
            self.statusBar().showMessage(err_msg); log.error(err_msg, exc_info=True)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    palette = QPalette() 
    palette.setColor(QPalette.ColorRole.Window, QColor(240,244,248)) 
    palette.setColor(QPalette.ColorRole.WindowText, QColor(26,37,47)) 
    palette.setColor(QPalette.ColorRole.Base, QColor(255,255,255))      
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(225,232,237)) 
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255,255,220))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0,0,0))
    palette.setColor(QPalette.ColorRole.Text, QColor(26,37,47))       
    palette.setColor(QPalette.ColorRole.Button, QColor(225,232,237))     
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(38,50,56)) 
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255,23,68)) 
    palette.setColor(QPalette.ColorRole.Link, QColor(0,123,255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(100,181,246))  
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255,255,255)) 
    app.setPalette(palette)
    
    default_font = QFont("Segoe UI", 9) 
    app.setFont(default_font)
    
    ex = AutoCrateApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
