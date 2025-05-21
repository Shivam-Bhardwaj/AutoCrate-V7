"""
Debug version of autocrate_pyqt_gui.py with extensive logging
"""

import sys
import os
import json
import logging
import traceback
from datetime import datetime

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"autocrate_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("AutoCrate")
logger.info(f"Starting debug session, logging to {log_file}")

try:
    # Import required modules
    logger.info("Importing modules...")
    from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog, QMessageBox
    from PyQt6.QtGui import QAction, QColor
    from PyQt6.QtCore import Qt, QSize
    
    # Import custom modules
    from wizard_app.ui_modules.base_assembly_views import FloorboardTopView, SkidFrontView
    from wizard_app.ui_modules.generated_ui import Ui_MainWindow
    
    # Import logical components
    from wizard_app import config
    from wizard_app import skid_logic
    from wizard_app import floorboard_logic
    from wizard_app import wall_logic
    from wizard_app import cap_logic
    from wizard_app import decal_logic
    from wizard_app import exp_generator
    
    logger.info("All modules imported successfully")
except Exception as e:
    logger.critical(f"Error importing modules: {str(e)}")
    logger.critical(traceback.format_exc())
    print(f"CRITICAL ERROR: {str(e)}")
    sys.exit(1)

class AutoCrateDebugApp(QMainWindow):
    """Main application window for AutoCrate Wizard with added logging"""
    
    def __init__(self):
        super().__init__()
        logger.info("Initializing AutoCrateDebugApp")
        
        try:
            # Set up UI
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            
            # Load default parameters
            self.parameters_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parameters.json")
            self.exp_output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "autocrate_expression.exp")
            
            # Get references to visualization widgets
            self.floorboard_view = self.findChild(FloorboardTopView, "floorboardView")
            self.skid_view = self.findChild(SkidFrontView, "skidView")
            
            logger.info("UI setup complete")
            
            # Connect signals
            self.ui.calculateButton.clicked.connect(self.run_calculations_and_generate_exp)
            self.ui.actionLoad_Parameters.triggered.connect(self.load_parameters)
            self.ui.actionSave_Parameters.triggered.connect(self.save_parameters)
            self.ui.actionExit.triggered.connect(self.close)
            
            # Load initial parameters
            self.load_parameters()
            logger.info("Initial parameters loaded")
            
        except Exception as e:
            logger.critical(f"Error initializing app: {str(e)}")
            logger.critical(traceback.format_exc())
            print(f"CRITICAL ERROR: {str(e)}")
    
    def load_parameters(self, file_path=None):
        """Load parameters from JSON file"""
        try:
            if not file_path:
                file_path = self.parameters_file
                
            logger.info(f"Loading parameters from {file_path}")
            
            if not os.path.exists(file_path):
                logger.warning(f"Parameters file not found: {file_path}")
                return
                
            with open(file_path, 'r') as f:
                params = json.load(f)
                
            # Load parameters into UI fields
            self.ui.productWeightSpinBox.setValue(params.get('product_weight', 500.0))
            self.ui.productWidthSpinBox.setValue(params.get('product_width', 36.0))
            self.ui.productLengthSpinBox.setValue(params.get('product_length', 48.0))
            self.ui.productHeightSpinBox.setValue(params.get('product_height', 36.0))
            
            self.ui.clearanceSideSpinBox.setValue(params.get('clearance_side', 1.0))
            self.ui.clearanceTopSpinBox.setValue(params.get('clearance_above_product', 2.0))
            
            self.ui.panelThicknessSpinBox.setValue(params.get('panel_thickness', 0.25))
            self.ui.cleatThicknessSpinBox.setValue(params.get('cleat_thickness', 0.75))
            self.ui.wallCleatWidthSpinBox.setValue(params.get('wall_cleat_width', 3.5))
            self.ui.floorboardThicknessSpinBox.setValue(params.get('floor_lumbar_thickness', 1.5))
            self.ui.capCleatWidthSpinBox.setValue(params.get('cap_cleat_width', 3.5))
            self.ui.maxCleatSpacingSpinBox.setValue(params.get('max_top_cleat_spacing', 24.0))
            
            self.ui.allow3x4SkidsCheckBox.setChecked(params.get('allow_3x4_skids', True))
            self.ui.stdFloorboardComboBox.setCurrentText(params.get('chosen_standard_floorboard_nominal', '2x8'))
            self.ui.allowCustomFloorboardCheckBox.setChecked(params.get('allow_custom_floorboard_fill', True))
            
            self.ui.frontPanelRemovableCheckBox.setChecked(params.get('end_panel_1_removable', True))
            self.ui.backPanelRemovableCheckBox.setChecked(params.get('end_panel_2_removable', True))
            self.ui.leftSidePanelRemovableCheckBox.setChecked(params.get('side_panel_1_removable', True))
            self.ui.rightSidePanelRemovableCheckBox.setChecked(params.get('side_panel_2_removable', True))
            self.ui.topPanelRemovableCheckBox.setChecked(params.get('top_panel_removable', True))
            
            self.ui.productFragileCheckBox.setChecked(params.get('product_is_fragile', False))
            self.ui.specialHandlingCheckBox.setChecked(params.get('product_requires_special_handling', False))
            
            logger.info("Parameters loaded successfully")
        except Exception as e:
            logger.error(f"Error loading parameters: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"Failed to load parameters: {str(e)}")
    
    def save_parameters(self, file_path=None):
        """Save current parameters to JSON file"""
        try:
            if not file_path:
                file_path = self.parameters_file
                
            logger.info(f"Saving parameters to {file_path}")
                
            params = self.collect_parameters()
            if not params:
                logger.warning("Failed to collect parameters for saving")
                return
                
            with open(file_path, 'w') as f:
                json.dump(params, f, indent=4)
                
            logger.info("Parameters saved successfully")
        except Exception as e:
            logger.error(f"Error saving parameters: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"Failed to save parameters: {str(e)}")
    
    def collect_parameters(self):
        """Collect parameters from UI fields"""
        try:
            logger.info("Collecting parameters from UI")
            
            params = {
                'product_weight': self.ui.productWeightSpinBox.value(),
                'product_width': self.ui.productWidthSpinBox.value(),
                'product_length': self.ui.productLengthSpinBox.value(),
                'product_height': self.ui.productHeightSpinBox.value(),
                'product_actual_height': self.ui.productHeightSpinBox.value(),  # For backward compatibility
                
                'clearance_side': self.ui.clearanceSideSpinBox.value(),
                'clearance_above_product': self.ui.clearanceTopSpinBox.value(),
                
                'panel_thickness': self.ui.panelThicknessSpinBox.value(),
                'cleat_thickness': self.ui.cleatThicknessSpinBox.value(),
                'wall_cleat_width': self.ui.wallCleatWidthSpinBox.value(),
                'floor_lumbar_thickness': self.ui.floorboardThicknessSpinBox.value(),
                'cap_cleat_width': self.ui.capCleatWidthSpinBox.value(),
                'max_top_cleat_spacing': self.ui.maxCleatSpacingSpinBox.value(),
                
                'allow_3x4_skids': self.ui.allow3x4SkidsCheckBox.isChecked(),
                'chosen_standard_floorboard_nominal': self.ui.stdFloorboardComboBox.currentText(),
                'allow_custom_floorboard_fill': self.ui.allowCustomFloorboardCheckBox.isChecked(),
                
                'end_panel_1_removable': self.ui.frontPanelRemovableCheckBox.isChecked(),
                'end_panel_2_removable': self.ui.backPanelRemovableCheckBox.isChecked(),
                'side_panel_1_removable': self.ui.leftSidePanelRemovableCheckBox.isChecked(),
                'side_panel_2_removable': self.ui.rightSidePanelRemovableCheckBox.isChecked(),
                'top_panel_removable': self.ui.topPanelRemovableCheckBox.isChecked(),
                
                'product_is_fragile': self.ui.productFragileCheckBox.isChecked(),
                'product_requires_special_handling': self.ui.specialHandlingCheckBox.isChecked(),
            }
            
            logger.info("Parameters collected successfully")
            logger.debug(f"Parameters: {json.dumps(params, indent=2)}")
            return params
        except Exception as e:
            logger.error(f"Error collecting parameters: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"Failed to collect parameters: {str(e)}")
            return None
    
    def run_calculations_and_generate_exp(self):
        """Run calculations and update UI with results"""
        logger.info("Starting calculations")
        
        params = self.collect_parameters()
        if not params:
            logger.warning("Parameter validation failed")
            self.statusBar().showMessage("Parameter validation failed. Please correct inputs.", 5000)
            return

        try:
            self.statusBar().showMessage("Running calculations...", 2000)
            
            # Calculate shipping base components
            logger.info("Calculating skid layout")
            self.skid_results = skid_logic.calculate_skid_layout(
                product_weight=params['product_weight'], product_width=params['product_width'],
                product_length=params['product_length'], clearance_side=params['clearance_side'],
                panel_thickness=params['panel_thickness'], cleat_thickness=params['cleat_thickness'],
                allow_3x4_skids_for_light_loads=params['allow_3x4_skids']
            )
            skid_results = self.skid_results  # Local variable for clarity
            
            logger.debug(f"Skid results: {json.dumps(skid_results, indent=2, default=str)}")
            
            target_span_y_floor = params['product_width'] + 2 * params['clearance_side']
            board_len_x_floor = skid_results.get('skid_actual_length', params['product_length'])
            
            logger.info("Calculating floorboard layout")
            floor_results = floorboard_logic.calculate_floorboard_layout_refined(
                target_span_to_fill_y=target_span_y_floor,
                board_length_x=board_len_x_floor, 
                chosen_standard_floorboard_nominal_key=params['chosen_standard_floorboard_nominal'],
                allow_custom_fill=params['allow_custom_floorboard_fill'],
                floorboard_actual_thickness_z=params['floor_lumbar_thickness']
            )
            
            logger.debug(f"Floorboard results: {json.dumps(floor_results, indent=2, default=str)}")

            # Calculate crate cap components
            crate_internal_h_for_walls = params['product_actual_height'] + params['clearance_above_product']
            
            logger.info("Calculating wall layout")
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
            
            logger.debug(f"Wall results: {json.dumps(wall_results, indent=2, default=str)}")
            
            logger.info("Calculating cap layout")
            cap_results = cap_logic.calculate_cap_layout(
                crate_overall_width_y=skid_results.get('crate_overall_width_calculated', 0),
                crate_overall_length_x=skid_results.get('skid_actual_length', 0),
                cap_panel_sheathing_thickness=params['panel_thickness'],
                cap_cleat_actual_thickness=params['cleat_thickness'],
                cap_cleat_actual_width=params['cap_cleat_width'],
                max_top_cleat_spacing=params['max_top_cleat_spacing'],
                top_panel_removable=params['top_panel_removable']
            )
            
            logger.debug(f"Cap results: {json.dumps(cap_results, indent=2, default=str)}")

            # Calculate decals
            side_panel_h = wall_results.get('side_panels', {}).get('panel_height_dim', 0)
            side_panel_w = wall_results.get('side_panels', {}).get('panel_width_dim', 0)
            end_panel_h = wall_results.get('end_panels', {}).get('panel_height_dim', 0)
            end_panel_w = wall_results.get('end_panels', {}).get('panel_width_dim', 0)
            overall_crate_h_for_decals = (skid_results.get('skid_actual_height',0)) + \
                                     params['floor_lumbar_thickness'] + \
                                     crate_internal_h_for_walls + \
                                     (cap_results.get('cap_panel',{}).get('thickness', params['panel_thickness']))

            logger.info("Calculating decal placements")
            decal_results = decal_logic.calculate_decal_placements(
                product_is_fragile=params['product_is_fragile'],
                product_requires_special_handling=params['product_requires_special_handling'],
                panel_height_side=side_panel_h, panel_width_side=side_panel_w,
                panel_height_end=end_panel_h, panel_width_end=end_panel_w,
                overall_crate_height=overall_crate_h_for_decals
            )
            
            logger.debug(f"Decal results: {json.dumps(decal_results, indent=2, default=str)}")
            
            # Update visualization widgets with new data
            logger.info("Updating visualization widgets")
            
            if hasattr(self, 'skid_view') and self.skid_view and self.skid_results:
                logger.info("Setting skid view data")
                logger.debug(f"Skid data for view: {json.dumps(self.skid_results, indent=2, default=str)}")
                logger.debug(f"Floorboard data for skid view: {json.dumps(floor_results, indent=2, default=str)}")
                try:
                    self.skid_view.set_data(self.skid_results, floorboard_data=floor_results)
                    logger.info("Skid view data set successfully")
                except Exception as e:
                    logger.error(f"Error setting skid view data: {str(e)}")
                    logger.error(traceback.format_exc())
            
            if hasattr(self, 'floorboard_view') and self.floorboard_view and floor_results:
                logger.info("Setting floorboard view data")
                logger.debug(f"Floorboard data: {json.dumps(floor_results, indent=2, default=str)}")
                logger.debug(f"Skid data for floorboard: {json.dumps(self.skid_results, indent=2, default=str)}")
                try:
                    self.floorboard_view.set_data(floor_results, skid_data=self.skid_results)
                    logger.info("Floorboard view data set successfully")
                except Exception as e:
                    logger.error(f"Error setting floorboard view data: {str(e)}")
                    logger.error(traceback.format_exc())

            # Update displays (table)
            logger.info("Updating results display")
            try:
                self.update_results_display(self.skid_results, floor_results, cap_results, wall_results, decal_results, params)
                logger.info("Results display updated successfully")
            except Exception as e:
                logger.error(f"Error updating results display: {str(e)}")
                logger.error(traceback.format_exc())

            # Generate expression file
            logger.info("Generating expression file")
            try:
                exp_content = exp_generator.generate_nx_exp_file_content(
                    product_params=params, skid_results=self.skid_results, floorboard_results=floor_results,
                    wall_results=wall_results, cap_results=cap_results, decal_results=decal_results,
                    app_version=config.VERSION
                )

                output_dir = os.path.dirname(self.exp_output_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                with open(self.exp_output_path, 'w') as f:
                    f.write(exp_content)
                
                logger.info(f"Expression file generated: {self.exp_output_path}")
                self.statusBar().showMessage(f"Results calculated and saved to {self.exp_output_path}", 5000)
            except Exception as e:
                logger.error(f"Error generating expression file: {str(e)}")
                logger.error(traceback.format_exc())
                self.statusBar().showMessage(f"Error generating expression file: {str(e)}", 5000)
                
        except Exception as e:
            logger.critical(f"Error in calculations: {str(e)}")
            logger.critical(traceback.format_exc())
            self.statusBar().showMessage(f"Error in calculations: {str(e)}", 5000)
            QMessageBox.critical(self, "Error", f"An error occurred during calculations: {str(e)}")
    
    def update_results_display(self, skid_results, floor_results, cap_results, wall_results, decal_results, params):
        """Update the results table with calculation results"""
        logger.info("Updating results table")
        try:
            # Just a placeholder for now - we'll expand this later as needed
            # In a real implementation, this would populate a detailed results table
            pass
        except Exception as e:
            logger.error(f"Error updating results table: {str(e)}")
            logger.error(traceback.format_exc())

# Application entry point
if __name__ == "__main__":
    try:
        logger.info("Starting application")
        app = QApplication(sys.argv)
        window = AutoCrateDebugApp()
        window.show()
        logger.info("Application window shown")
        exit_code = app.exec()
        logger.info(f"Application exited with code {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"Critical application error: {str(e)}")
        logger.critical(traceback.format_exc())
        print(f"CRITICAL ERROR: {str(e)}")
        if 'app' in locals():
            app.exit(1)
        sys.exit(1)
