import sys
import os
import json # For results display if needed
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, 
                             QCheckBox, QGroupBox, QScrollArea, QStatusBar, QMessageBox,
                             QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QDoubleValidator, QIntValidator, QFont, QPalette, QColor
from PyQt6.QtCore import Qt

# Make sure wizard_app is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'wizard_app'))

try:
    from wizard_app import config
    from wizard_app import skid_logic
    from wizard_app import floorboard_logic
    from wizard_app import cap_logic
    from wizard_app import wall_logic
    from wizard_app import decal_logic
    from wizard_app import exp_generator
    from wizard_app.ui_modules import CrateVisualizationManager, SkidVisualizationWidget, FloorboardVisualizationWidget, WallVisualizationWidget, CapVisualizationWidget
    from wizard_app.ui_modules.base_assembly_views import FloorboardTopView, SkidFrontView
except ImportError as e:
    print(f"Critical Import Error: {e}. Ensure wizard_app modules are accessible.")
    # In a real app, you might show a QMessageBox and exit.
    # QMessageBox.critical(None, "Import Error", f"Failed to import a necessary module: {e}")
    # sys.exit(1)
    raise

class SubassemblyTab(QWidget):
    def __init__(self, title, top_view_widget, side_view_widget, logic_text):
        super().__init__()
        layout = QVBoxLayout(self)
        # Title
        title_label = QLabel(f"<b>{title}</b>")
        layout.addWidget(title_label)
        # Views
        views_layout = QHBoxLayout()
        views_layout.addWidget(top_view_widget)
        views_layout.addWidget(side_view_widget)
        layout.addLayout(views_layout)
        # Logic dropdown
        logic_group = QGroupBox("Logic Used")
        logic_group.setCheckable(True)
        logic_group.setChecked(False)
        logic_layout = QVBoxLayout()
        logic_label = QLabel(logic_text)
        logic_label.setWordWrap(True)
        logic_layout.addWidget(logic_label)
        logic_group.setLayout(logic_layout)
        layout.addWidget(logic_group)

class AutoCrateApp(QMainWindow):
    EXP_FILENAME = "AutoCrate_Expressions.exp"
    MAX_PRODUCT_DIM_CONST = 999.0 

    parameter_definitions = [
        ("Product Weight (lbs):", 'product_weight', 600.0, "float", 1, 1.0, 20000.0, "Total weight of the product. (Example: 600 lbs)"),
        ("Product Width (in):", 'product_width', 38.0, "float", 2, 1.0, MAX_PRODUCT_DIM_CONST, f"Inside dimension across skids - Y direction (Example: 38.00\")"),
        ("Product Length (in):", 'product_length', 46.0, "float", 2, 1.0, MAX_PRODUCT_DIM_CONST, f"Inside dimension along skids - X direction (Example: 46.00\")"),
        ("Product Height (in):", 'product_actual_height', 91.5, "float", 2, 1.0, MAX_PRODUCT_DIM_CONST, f"Inside height of the product (Example: 91.50\")"),
        
        ("Side Clearance (in):", 'clearance_side', 1.0, "float", 2, 0.0, 20.0, "Clearance from product to inner wall surfaces (width and length)."),
        ("Top Clearance (in):", 'clearance_above_product', config.DEFAULT_CLEARANCE_ABOVE_PRODUCT, "float", 2, 0.0, 20.0, "Clearance above product top to cap panel underside."),
        
        ("Panel Thickness (in):", 'panel_thickness', 0.25, "float", 3, 0.25, 1.5, "Thickness for wall and cap plywood/sheathing (typically 0.25\")."),
        ("Cleat Thickness (in):", 'cleat_thickness', 0.75, "float", 3, 0.5, 3.0, "Actual thickness for ALL cleats. Ensure size is appropriate for panel area."),
        
        ("Wall Cleat Width (in):", 'wall_cleat_width', 3.5, "float", 2, 1.0, 11.25, "Actual width of wall cleats. (Example: Use 3.5\" for standard)"),
        ("Floorboard Thickness (in):", 'floor_lumbar_thickness', 1.5, "float", 3, 0.5, 3.0, "Actual thickness of floorboards (typically 1.5\")."),
        
        ("Cap Cleat Width (in):", 'cap_cleat_width', 3.5, "float", 2, 1.0, 11.25, "Actual width of cap cleats. (Example: Use 3.5\" for 2x4 nominal lumber)"),
        ("Max Cleat Spacing (C-C, in):", 'max_top_cleat_spacing', 24.0, "float", 2, 6.0, 60.0, "Maximum center-to-center spacing for cap cleats (typically 24\")."),
        
        ("Allow 3x4 Skids (Light Loads):", 'allow_3x4_skids', True, "bool", 0, None, None, "If checked, 3x4 skids can be used for lighter loads per rules."),
        ("Std Floorboard Size:", 'chosen_standard_floorboard_nominal', "2x8", "choice", 0, config.ALL_LUMBER_OPTIONS_UI, None, "Standard floorboard nominal size to prioritize (typically 2x8)."),
        ("Allow Custom Fill Floorboard:", 'allow_custom_floorboard_fill', True, "bool", 0, None, None, "Allow a custom-width floorboard to fill remaining small gaps."),
        ("Product is Fragile:", 'product_is_fragile', False, "bool", 0, None, None, "Check if product is fragile (for decal selection)."),
        ("Special Handling Required:", 'product_requires_special_handling', False, "bool", 0, None, None, "Check if special handling decals (e.g., This Way Up) are needed."),
        ("Front Panel Removable:", 'end_panel_1_removable', False, "bool", 0, None, None, "Make Front Panel (End Panel 1) removable."),
        ("Back Panel Removable:", 'end_panel_2_removable', False, "bool", 0, None, None, "Make Back Panel (End Panel 2) removable."),
        ("Left Side Panel Removable:", 'side_panel_1_removable', True, "bool", 0, None, None, "Make Left Side Panel (Side Panel 1) removable (Style B default)."),
        ("Right Side Panel Removable:", 'side_panel_2_removable', False, "bool", 0, None, None, "Make Right Side Panel (Side Panel 2) removable."),
        ("Top Panel Removable:", 'top_panel_removable', False, "bool", 0, None, None, "Make the Top Panel removable.")
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"AutoCrate Wizard V{config.VERSION}")
        self.setMinimumSize(1200, 800)
        self.exp_output_path = ""
        self.input_widgets = {} # Initialize here, before set_default_exp_output_path or initUI
        self.results_labels = {}
        self.visualization_manager = None
        self.set_default_exp_output_path()
        self.initUI()
        self.statusBar().showMessage("Ready")

    def set_default_exp_output_path(self):
        # Default to a subdirectory in the application's directory
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): # PyInstaller
            executable_dir = os.path.dirname(sys.executable)
        else: # Running as script
            executable_dir = os.path.dirname(os.path.abspath(__file__))
        
        target_dir = os.path.join(executable_dir, "nx_crate_expressions")
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
            except Exception as e:
                # Consider logging this error: print(f"Could not create target directory {target_dir}: {e}")
                target_dir = executable_dir # Fallback to app dir
        
        self.exp_output_path = os.path.normpath(os.path.join(target_dir, self.EXP_FILENAME))

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title at the top
        title_label = QLabel(f"AutoCrate Wizard V{config.VERSION}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #0055aa; padding-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Main content in a grid layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        # --- Left Panel: Input Parameters ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Organize params in two columns for more compact display
        input_grid = QGridLayout()
        input_grid.setSpacing(5)
        input_grid.setColumnStretch(0, 1)  # Group name column
        input_grid.setColumnStretch(1, 1)  # Inputs column
        
        row = 0
        
        # More compact parameter groups
        param_groups = {
            "Product Dimensions": ['product_weight', 'product_width', 'product_length', 'product_actual_height'],
            "Crate Construction": ['clearance_side', 'clearance_above_product', 'panel_thickness', 'cleat_thickness', 
                                  'wall_cleat_width', 'floor_lumbar_thickness', 'cap_cleat_width', 'max_top_cleat_spacing'],
            "Options": ['allow_3x4_skids', 'chosen_standard_floorboard_nominal', 'allow_custom_floorboard_fill', 
                       'product_is_fragile', 'product_requires_special_handling'],
            "Removable Panels": ['end_panel_1_removable', 'end_panel_2_removable', 'side_panel_1_removable', 
                                'side_panel_2_removable', 'top_panel_removable']
        }
        
        for group_title, param_keys in param_groups.items():
            group_box = QGroupBox(group_title)
            group_box.setStyleSheet("QGroupBox { font-weight: bold; }")
            group_layout = QGridLayout()
            group_layout.setSpacing(5)
            group_layout.setContentsMargins(8, 15, 8, 8)
            
            row_idx = 0
            for p_label, p_key, p_default, p_type, p_dec, p_min, p_max, p_tooltip in self.parameter_definitions:
                if p_key not in param_keys:
                    continue

                label_widget = QLabel(p_label)
                label_widget.setToolTip(p_tooltip if p_tooltip else p_label)
                
                widget_instance = None
                if p_type == "float":
                    widget_instance = QLineEdit(str(p_default))
                    validator = QDoubleValidator(p_min, p_max, p_dec)
                    validator.setNotation(QDoubleValidator.Notation.StandardNotation)
                    widget_instance.setValidator(validator)
                    widget_instance.setFixedWidth(70)
                elif p_type == "int":
                    widget_instance = QLineEdit(str(p_default))
                    validator = QIntValidator(int(p_min), int(p_max))
                    widget_instance.setValidator(validator)
                    widget_instance.setFixedWidth(70)
                elif p_type == "bool":
                    widget_instance = QCheckBox()
                    widget_instance.setChecked(p_default)
                elif p_type == "choice":
                    widget_instance = QComboBox()
                    if isinstance(p_min, list):
                        widget_instance.addItems([str(item) for item in p_min])
                    if str(p_default) in [str(item) for item in p_min if isinstance(p_min, list)]:
                         widget_instance.setCurrentText(str(p_default))
                    elif isinstance(p_min, list) and p_min:
                         widget_instance.setCurrentIndex(0)
                    widget_instance.setFixedWidth(120)
                else:
                    widget_instance = QLineEdit(str(p_default))
                    widget_instance.setFixedWidth(100)

                if widget_instance:
                    widget_instance.setToolTip(p_tooltip if p_tooltip else p_label)
                    self.input_widgets[p_key] = widget_instance
                    group_layout.addWidget(label_widget, row_idx, 0)
                    group_layout.addWidget(widget_instance, row_idx, 1)
                row_idx += 1
            
            group_box.setLayout(group_layout)
            
            # Place groups in a grid, 2 columns wide
            input_grid.addWidget(group_box, row // 2, row % 2)
            row += 1
        
        # Add the grid to the left panel
        left_layout.addLayout(input_grid)
        
        # Add output path selection in a more compact way
        output_frame = QGroupBox("Expression File")
        output_layout = QHBoxLayout()
        output_layout.setContentsMargins(8, 15, 8, 8)
        self.output_path_label = QLabel(self.exp_output_path)
        self.output_path_label.setWordWrap(True)
        browse_button = QPushButton("Browse...")
        browse_button.setFixedWidth(80)
        browse_button.clicked.connect(self.browse_exp_output_location)
        output_layout.addWidget(self.output_path_label, 1)
        output_layout.addWidget(browse_button)
        output_frame.setLayout(output_layout)
        left_layout.addWidget(output_frame)
        
        # Generate button
        generate_button = QPushButton("Generate & Update .exp File")
        generate_button.clicked.connect(self.run_calculations_and_generate_exp)
        left_layout.addWidget(generate_button)
        
        content_layout.addWidget(left_panel, 1)

        # --- Right Panel: Tabs for Results & Visualizations ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget for results and visualizations
        tabs = QTabWidget()
        
        # Results Tab - with table layout
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        results_layout.setContentsMargins(10, 10, 10, 10)
        results_layout.setSpacing(5)
        
        # Create table for results display
        self.results_table = QTableWidget(0, 2)  # 0 rows initially, 2 columns
        self.results_table.setHorizontalHeaderLabels(["Field", "Value"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setShowGrid(True)
        self.results_table.setGridStyle(Qt.PenStyle.SolidLine)

        # Define all result fields in order
        self.result_table_items = [
            ("Skid Type", "skid_type"),
            ("Skid Count", "skid_count"),
            ("Skid Spacing", "skid_spacing"),
            ("Skid Dimensions", "skid_dims"),
            ("Skid Length", "skid_length"),
            ("Floorboard Type", "floor_std_type"),
            ("Standard Floorboard Count", "floor_std_count"),
            ("Side Panels", "side_panel_dims"),
            ("End Panels", "end_panel_dims"),
            ("Top Panel", "cap_panel_dims"),
            ("Longitudinal Cleats", "cap_long_cleats"),
            ("Transverse Cleats", "cap_trans_cleats"),
            ("Crate Overall Width", "crate_overall_width"),
            ("Crate Overall Length", "crate_overall_length"),
            ("Crate Overall Height", "crate_overall_height"),
            ("Custom Floorboard Count", "floor_custom_count"),
            ("Custom Floorboard Width", "floor_custom_width"),
            ("Final Gap", "floor_gap")
        ]
        self.results_table.setRowCount(len(self.result_table_items))
        self.results_labels = {}
        for row, (label, key) in enumerate(self.result_table_items):
            label_item = QTableWidgetItem(label)
            font = label_item.font()
            font.setPointSize(10)
            label_item.setFont(font)
            label_item.setForeground(QColor("#333333"))
            label_item.setBackground(QColor("#F5F5F5"))
            label_item.setFlags(label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.results_table.setItem(row, 0, label_item)
            value_item = QTableWidgetItem("")
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.results_table.setItem(row, 1, value_item)
            self.results_labels[key] = row
        
        results_layout.addWidget(self.results_table)
        
        # Visualization Tab
        visualization_tabs = QTabWidget()
        # Create specialized visualization widgets for base assembly
        floorboard_top_view = FloorboardTopView()
        skid_front_view = SkidFrontView()
        
        # Store references to these views for later data updates
        self.floorboard_view = floorboard_top_view
        self.skid_view = skid_front_view
        
        # Create tab with the specialized views
        visualization_tabs.addTab(SubassemblyTab("Base Assembly",
            floorboard_top_view,
            skid_front_view,
            "Base assembly includes floorboards arranged across skids. Skid spacing follows the max 24 inch rule, and floorboards are selected based on standard lumber dimensions."
        ), "Base Assembly")
        visualization_tabs.addTab(SubassemblyTab("Front Panel",
            QLabel("Front View: Front Panel"),
            QLabel("Side View: Front Panel"),
            "Logic for front panel: ..."
        ), "Front Panel")
        visualization_tabs.addTab(SubassemblyTab("Left Side Panel",
            QLabel("Front View: Left Side Panel"),
            QLabel("Side View: Left Side Panel"),
            "Logic for left side panel: ..."
        ), "Left Side Panel")
        visualization_tabs.addTab(SubassemblyTab("Right Side Panel",
            QLabel("Front View: Right Side Panel"),
            QLabel("Side View: Right Side Panel"),
            "Logic for right side panel: ..."
        ), "Right Side Panel")
        visualization_tabs.addTab(SubassemblyTab("Back Panel",
            QLabel("Front View: Back Panel"),
            QLabel("Side View: Back Panel"),
            "Logic for back panel: ..."
        ), "Back Panel")
        visualization_tabs.addTab(SubassemblyTab("Top Panel",
            QLabel("Top View: Top Panel"),
            QLabel("Side View: Top Panel"),
            "Logic for top panel: ..."
        ), "Top Panel")
        visualization_tabs.addTab(SubassemblyTab("Markings",
            QLabel("Markings View 1"),
            QLabel("Markings View 2"),
            "Logic for markings: ..."
        ), "Markings")
        visualization_tabs.addTab(SubassemblyTab("Klimp Positions",
            QLabel("Klimp Positions View 1"),
            QLabel("Klimp Positions View 2"),
            "Logic for Klimp positions: ..."
        ), "Klimp Positions")
        # Replace the old visualization tab with this:
        tabs.addTab(visualization_tabs, "Crate Visualizations")
        
        right_layout.addWidget(tabs)
        content_layout.addWidget(right_panel, 2)  # Give right panel more space
        main_layout.addLayout(content_layout)
        
        # Adding status bar
        self.statusBar().showMessage("Ready")
        
        # Apply styling
        self.set_app_style()

    def set_app_style(self):
        # Minimal, professional table style
        self.setStyleSheet("""
            QMainWindow { background-color: white; }
            QLabel { font-size: 10pt; color: #000; font-weight: normal; }
            QLineEdit, QComboBox {
                padding: 5px; border: 1px solid #888; border-radius: 3px;
                font-size: 10pt; background: #fff; color: #000;
            }
            QCheckBox { font-size: 10pt; color: #000; }
            QPushButton {
                padding: 8px 12px; border-radius: 3px; font-size: 10pt;
                background: #222; color: #fff; font-weight: bold; border: none;
            }
            QPushButton:hover { background: #444; }
            QGroupBox {
                border: 1px solid #ccc; border-radius: 4px; margin-top: 1.0ex;
                font-weight: bold; color: #000; background: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 5px; background: #f8f8f8; color: #000;
            }
            QTabWidget::pane { border: 1px solid #ccc; background: #fff; border-radius: 3px; }
            QTabBar::tab {
                background: #f5f5f5; color: #222; border: 1px solid #ccc;
                border-bottom: none; border-top-left-radius: 3px; border-top-right-radius: 3px;
                padding: 6px 10px; margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #fff; color: #000; border-bottom: 1px solid #fff; font-weight: bold;
            }
            QStatusBar { font-size: 9pt; background: #f0f0f0; color: #333; }
            QScrollArea { border: none; background: transparent; }
            /* Table styling: minimal, high contrast */
            QTableWidget {
                gridline-color: #e0e0e0; background: #fff; border: 1px solid #ccc;
                border-radius: 3px; font-size: 10pt; color: #000;
            }
            QTableWidget::item { padding: 6px; border-bottom: 1px solid #e0e0e0; color: #111; }
            QHeaderView::section {
                background: #fff; color: #111; padding: 8px; font-weight: bold;
                border: none; border-bottom: 2px solid #bbb; font-size: 11pt;
            }
            QTableWidget::item:alternate { background: #fafbfc; }
        """)

    def browse_exp_output_location(self):
        current_dir = os.path.dirname(self.exp_output_path)
        file_path, _ = QFileDialog.getSaveFileName(self, "Save .exp File", current_dir, "Expression Files (*.exp);;All Files (*)")
        if file_path:
            if not file_path.lower().endswith(".exp"):
                file_path += ".exp"
            self.exp_output_path = os.path.normpath(file_path)
            self.output_path_label.setText(self.exp_output_path)
            self.statusBar().showMessage(f"Output path set to: {self.exp_output_path}", 3000)

    def collect_parameters(self):
        params = {}
        validation_passed = True
        for p_label, p_key, p_default, p_type, p_dec, p_min, p_max, p_tooltip in self.parameter_definitions:
            widget = self.input_widgets.get(p_key)
            if not widget: continue

            if isinstance(widget, QLineEdit):
                text_value = widget.text()
                if widget.validator():
                    state, _, _ = widget.validator().validate(text_value, 0)
                    if state != QDoubleValidator.State.Acceptable and state != QIntValidator.State.Acceptable:
                        QMessageBox.warning(self, "Input Error", f"Invalid value for '{p_label}': '{text_value}'")
                        widget.setFocus()
                        validation_passed = False
                        break
                try:
                    if p_type == "float": params[p_key] = float(text_value)
                    elif p_type == "int": params[p_key] = int(text_value)
                except ValueError:
                    QMessageBox.warning(self, "Input Error", f"Could not convert '{text_value}' to a number for '{p_label}'.")
                    params[p_key] = p_default 
                    widget.setFocus()
                    validation_passed = False
                    break
            elif isinstance(widget, QComboBox):
                params[p_key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                params[p_key] = widget.isChecked()
        
        if not validation_passed: return None
        return params

    def update_results_display(self, skid_res, floor_res, cap_res, wall_res, decal_res, collected_params):
        def update_cell(key, value):
            if key in self.results_labels:
                # Try-except approach for handling deleted widgets
                try:
                    # Only proceed if we have a results_table
                    if not hasattr(self, 'results_table') or self.results_table is None:
                        return
                        
                    # If we can access the widget, it probably still exists
                    row = self.results_labels[key]
                    value_item = QTableWidgetItem(value)
                    font = value_item.font()
                    font.setBold(True)
                    font.setPointSize(10)
                    value_item.setFont(font)
                    value_item.setForeground(QColor("#000000"))
                    value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.results_table.setItem(row, 1, value_item)
                except (RuntimeError, ReferenceError, AttributeError):
                    # Widget was deleted or is no longer accessible
                    return
        
        # Skid Results
        if skid_res and isinstance(skid_res.get('exp_data'), dict):
            sd = skid_res['exp_data']
            update_cell('skid_type', f"{skid_res.get('skid_type_nominal', '-')}")
            update_cell('skid_count', f"{sd.get('CALC_Skid_Count', '-')}")
            update_cell('skid_spacing', f"{sd.get('CALC_Skid_Pitch', 0.0):.3f} in")
            update_cell('skid_dims', f"{sd.get('INPUT_Skid_Nominal_Width', 0.0):.2f} x {sd.get('INPUT_Skid_Nominal_Height',0.0):.2f} in")
            update_cell('skid_length', f"{sd.get('INPUT_Skid_Actual_Length', 0.0):.2f} in")
        
        if floor_res and isinstance(floor_res.get('exp_data'), dict):
            fd = floor_res
            update_cell('floor_std_type', f"{fd.get('standard_board_nominal_type','-')}")
            fc = fd.get('std_boards_front_count',0) + fd.get('std_boards_back_count',0)
            update_cell('floor_std_count', f"{fc}")
            update_cell('floor_custom_count', f"{fd.get('custom_board_count',0)}")
            update_cell('floor_custom_width', f"{fd.get('custom_board_actual_width',0):.3f} in")
            update_cell('floor_gap', f"{fd.get('final_gap_y_remaining',0):.3f} in")

        if cap_res and isinstance(cap_res.get('exp_data'), dict) and isinstance(cap_res.get('cap_panel'), dict) \
           and isinstance(cap_res.get('longitudinal_cleats'), dict) and isinstance(cap_res.get('transverse_cleats'), dict):
            cp = cap_res['cap_panel']
            cl = cap_res['longitudinal_cleats']
            ct = cap_res['transverse_cleats']
            update_cell('cap_panel_dims', f"{cp.get('length',0):.2f} x {cp.get('width',0):.2f} in")
            update_cell('cap_long_cleats', f"{cl.get('count',0)} @ {cl.get('actual_spacing_centers',0):.3f} in C-C")
            update_cell('cap_trans_cleats', f"{ct.get('count',0)} @ {ct.get('actual_spacing_centers',0):.3f} in C-C")

        if wall_res and isinstance(wall_res.get('side_panels'), dict) and isinstance(wall_res.get('end_panels'), dict):
            wd_s = wall_res['side_panels']
            wd_e = wall_res['end_panels']
            update_cell('side_panel_dims', f"{wd_s.get('panel_width_dim',0):.2f} x {wd_s.get('panel_height_dim',0):.2f} in")
            update_cell('end_panel_dims', f"{wd_e.get('panel_width_dim',0):.2f} x {wd_e.get('panel_height_dim',0):.2f} in")
        
        # Update the visualizations
        if self.visualization_manager:
            self.visualization_manager.update_visualizations(
                skid_results=skid_res,
                floorboard_results=floor_res,
                wall_results=wall_res,
                cap_results=cap_res
            )
        
        # Update the specialized visualization views
        if hasattr(self, 'skid_view') and self.skid_view and skid_res:
            self.skid_view.set_data(skid_res)
            
        if hasattr(self, 'floorboard_view') and self.floorboard_view and floor_res:
            self.floorboard_view.set_data(floor_res)
        
        crate_overall_w = skid_res.get('crate_overall_width_calculated', 0.0) if skid_res else 0.0
        crate_overall_l = skid_res.get('skid_actual_length', 0.0) if skid_res else 0.0 # Assuming skid length is overall crate length from skid_logic
        
        crate_internal_h_for_walls = collected_params.get('product_actual_height',0) + collected_params.get('clearance_above_product',0)
        crate_overall_h = (skid_res.get('skid_actual_height',0) if skid_res else 0.0) + \
                          collected_params.get('floor_lumbar_thickness',0) + \
                          crate_internal_h_for_walls + \
                          (cap_res.get('cap_panel',{}).get('thickness',0) if cap_res else collected_params.get('panel_thickness',0))

        update_cell('crate_overall_width', f"{crate_overall_w:.2f} in")
        update_cell('crate_overall_length', f"{crate_overall_l:.2f} in")
        update_cell('crate_overall_height', f"{crate_overall_h:.2f} in")

    def show_success_dialog(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText(message)
        msg.setStyleSheet("QLabel{color:#111;font-size:11pt;} QMessageBox{background:#fff;} QPushButton{background:#007bff;color:#fff;font-weight:bold;padding:6px 18px;border-radius:3px;}")
        msg.exec()

    def run_calculations_and_generate_exp(self):
        params = self.collect_parameters()
        if not params:
            self.statusBar().showMessage("Parameter validation failed. Please correct inputs.", 5000)
            return

        try:
            self.statusBar().showMessage("Running calculations...", 2000)
            
            # Calculate shipping base components
            self.skid_results = skid_logic.calculate_skid_layout(
                product_weight=params['product_weight'], product_width=params['product_width'],
                product_length=params['product_length'], clearance_side=params['clearance_side'],
                panel_thickness=params['panel_thickness'], cleat_thickness=params['cleat_thickness'],
                allow_3x4_skids_for_light_loads=params['allow_3x4_skids']
            )
            skid_results = self.skid_results # Keep local variable for clarity in subsequent calls within this function

            target_span_y_floor = params['product_width'] + 2 * params['clearance_side']
            board_len_x_floor = skid_results.get('skid_actual_length', params['product_length'])

            floor_results = floorboard_logic.calculate_floorboard_layout_refined(
                target_span_to_fill_y=target_span_y_floor,
                board_length_x=board_len_x_floor, 
                chosen_standard_floorboard_nominal_key=params['chosen_standard_floorboard_nominal'],
                allow_custom_fill=params['allow_custom_floorboard_fill'],
                floorboard_actual_thickness_z=params['floor_lumbar_thickness']
            )

            # Calculate crate cap components
            crate_internal_h_for_walls = params['product_actual_height'] + params['clearance_above_product']
            wall_results = wall_logic.calculate_wall_layout(
                crate_internal_width=target_span_y_floor,
                crate_internal_length=board_len_x_floor,
                crate_internal_height=crate_internal_h_for_walls,
                panel_thickness=params['panel_thickness'],
                cleat_thickness=params['cleat_thickness'],
                cleat_width=params['wall_cleat_width'],
                wall_construction_type="style_b",
                end_panel_1_removable=params['end_panel_1_removable'],
                end_panel_2_removable=params['end_panel_2_removable'],
                side_panel_1_removable=params['side_panel_1_removable'],
                side_panel_2_removable=params['side_panel_2_removable']
            )
            
            cap_results = cap_logic.calculate_cap_layout(
                crate_overall_width_y=skid_results.get('crate_overall_width_calculated', 0),
                crate_overall_length_x=skid_results.get('skid_actual_length', 0),
                cap_panel_sheathing_thickness=params['panel_thickness'],
                cap_cleat_actual_thickness=params['cleat_thickness'],
                cap_cleat_actual_width=params['cap_cleat_width'],
                max_top_cleat_spacing=params['max_top_cleat_spacing'],
                top_panel_removable=params['top_panel_removable']
            )

            # Calculate decals
            side_panel_h = wall_results.get('side_panels', {}).get('panel_height_dim', 0)
            side_panel_w = wall_results.get('side_panels', {}).get('panel_width_dim', 0)
            end_panel_h = wall_results.get('end_panels', {}).get('panel_height_dim', 0)
            end_panel_w = wall_results.get('end_panels', {}).get('panel_width_dim', 0)
            overall_crate_h_for_decals = (skid_results.get('skid_actual_height',0)) + \
                                     params['floor_lumbar_thickness'] + \
                                     crate_internal_h_for_walls + \
                                     (cap_results.get('cap_panel',{}).get('thickness', params['panel_thickness']))

            decal_results = decal_logic.calculate_decal_placements(
                product_is_fragile=params['product_is_fragile'],
                product_requires_special_handling=params['product_requires_special_handling'],
                panel_height_side=side_panel_h, panel_width_side=side_panel_w,
                panel_height_end=end_panel_h, panel_width_end=end_panel_w,
                overall_crate_height=overall_crate_h_for_decals
            )
            
            # Update visualization widgets with new data
            # DEBUG: Print info about skid_results
            print("DEBUG SKID_RESULTS:")
            print(f"Type: {type(self.skid_results)}")
            print(f"Has 'exp_data'?: {'exp_data' in self.skid_results if isinstance(self.skid_results, dict) else 'Not a dict'}")
            if isinstance(self.skid_results, dict) and 'exp_data' in self.skid_results:
                print(f"exp_data keys: {self.skid_results['exp_data'].keys()}")
                if 'CALC_Skid_Count' in self.skid_results['exp_data']:
                    print(f"CALC_Skid_Count: {self.skid_results['exp_data']['CALC_Skid_Count']}")
            
            if hasattr(self, 'skid_view') and self.skid_view and self.skid_results:
                self.skid_view.set_data(self.skid_results)
            if hasattr(self, 'floorboard_view') and self.floorboard_view and floor_results:
                # This is where we pass skid_data to the FloorboardTopView
                print(f"Before set_data, self.skid_results is {self.skid_results is not None}")
                self.floorboard_view.set_data(floor_results, skid_data=self.skid_results)

            # Update displays (table)
            self.update_results_display(self.skid_results, floor_results, cap_results, wall_results, decal_results, params)

            # Generate expression file
            exp_content = exp_generator.generate_nx_exp_file_content(
                product_params=params, skid_results=self.skid_results, floorboard_results=floor_results,
                wall_results=wall_results, cap_results=cap_results, decal_results=decal_results,
                app_version=config.VERSION
            )

            output_dir = os.path.dirname(self.exp_output_path)
            if not os.path.exists(output_dir): os.makedirs(output_dir)
            
            with open(self.exp_output_path, 'w') as f: f.write(exp_content)
            
            self.statusBar().showMessage(f"Successfully generated {os.path.basename(self.exp_output_path)}", 5000)
            self.show_success_dialog(f"Successfully generated AutoCrate_Expressions.exp to:\n{self.exp_output_path}")

        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}", 5000)
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}\nCheck console for more details.")
            print(f"Error details: {e}", file=sys.stderr) # Print to stderr for console visibility
            import traceback
            traceback.print_exc()

def main():
    app = QApplication(sys.argv)
    ex = AutoCrateApp()
    ex.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    # It can be helpful to set up basic logging when running directly for debugging
    # import logging
    # logging.basicConfig(level=logging.INFO, 
    #                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # log = logging.getLogger(__name__) # If you want to use a logger instance
    main() 