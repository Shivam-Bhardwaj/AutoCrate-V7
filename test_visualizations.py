#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for visualizing AutoCrate components.
This shows all visualization components in a tabbed interface.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from wizard_app.ui_modules.visualizations import (
    SkidVisualizationWidget,
    FloorboardVisualizationWidget,
    WallVisualizationWidget,
    CapVisualizationWidget
)

class TestVisualizationApp(QMainWindow):
    """Simple test application for visualizations."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoCrate Visualization Test")
        self.setGeometry(100, 100, 900, 700)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create visualization widgets
        self.skid_viz = SkidVisualizationWidget()
        self.floor_viz = FloorboardVisualizationWidget()
        self.wall_viz = WallVisualizationWidget()
        self.cap_viz = CapVisualizationWidget()
        
        # Add test data for example crate 0205-13057
        self.skid_viz.update_data({
            'skid_type_nominal': '4x4',
            'skid_count': 2,
            'skid_actual_width': 3.5,
            'skid_actual_length': 48.0,
            'actual_center_to_center_spacing': 34.5,
            'first_skid_position_offset_x': -17.25,
            'crate_overall_width_calculated': 40.0
        })
        
        self.floor_viz.update_data({
            'board_length_x': 48.0,
            'target_span_to_fill_y': 38.0,
            'standard_board_nominal_type': '2x8',
            'standard_board_actual_width': 7.25,
            'std_boards_front_count': 5,
            'std_boards_back_count': 0,
            'custom_board_count': 1,
            'custom_board_actual_width': 1.75,
            'final_gap_y_remaining': 0.0,
            'boards_placed_details': [
                {'type': 'std_front', 'id': 1, 'width': 7.25, 'y_pos': 0},
                {'type': 'std_front', 'id': 2, 'width': 7.25, 'y_pos': 7.25},
                {'type': 'std_front', 'id': 3, 'width': 7.25, 'y_pos': 14.5},
                {'type': 'std_front', 'id': 4, 'width': 7.25, 'y_pos': 21.75},
                {'type': 'std_front', 'id': 5, 'width': 7.25, 'y_pos': 29.0},
                {'type': 'custom_center', 'id': 1, 'width': 1.75, 'y_pos': 36.25}
            ]
        })
        
        self.wall_viz.update_data({
            'side_panels': {
                'panel_width_dim': 48.0,
                'panel_height_dim': 91.5,
                'cleats': {
                    'horizontal_edge_length': 46.0
                }
            },
            'end_panels': {
                'panel_width_dim': 38.0,
                'panel_height_dim': 91.5,
                'cleats': {
                    'vertical_edge_length': 91.5
                }
            },
            'removable_panels': {
                'count': 1,
                'positions': ['side_1'],
                'drop_end_style': True
            }
        })
        
        self.cap_viz.update_data({
            'cap_panel': {
                'width': 40.0,
                'length': 48.0,
                'thickness': 0.25,
                'removable': False
            },
            'longitudinal_cleats': {
                'count': 3,
                'width': 3.5,
                'positions_from_center': [-12.25, 0, 12.25]
            },
            'transverse_cleats': {
                'count': 3,
                'width': 3.5,
                'positions_from_center': [-15.0, 0, 15.0]
            },
            'fasteners': {
                'klimps_required': True,
                'klimp_count': 13
            }
        })
        
        # Add widgets to tabs
        self.tabs.addTab(self.skid_viz, "Shipping Base - Skids")
        self.tabs.addTab(self.floor_viz, "Shipping Base - Floorboards")
        self.tabs.addTab(self.wall_viz, "Crate Cap - Wall Panels")
        self.tabs.addTab(self.cap_viz, "Crate Cap - Top Panel")

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Optional: Use Fusion style for consistent look
    window = TestVisualizationApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 