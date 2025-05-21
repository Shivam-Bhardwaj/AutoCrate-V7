#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visualization components for AutoCrate logic calculations.
This module provides PyQt6 widgets for visualizing different aspects of crate design.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSizePolicy, QGridLayout)
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont
from PyQt6.QtCore import Qt, QRectF, QPointF

class BaseVisualizationWidget(QWidget):
    """Base class for all visualization widgets."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(250)
        self.title = "Visualization"
        # Colors based on crate image
        self.colors = {
            'background': QColor('#fffbe8'),  # very light tan
            'grid': QColor('#f0f0f0'),
            'axis': QColor('#cccccc'),
            'text': QColor('#222222'),
            'skid': QColor('#e6d3b3'),      # light wood (skids/cleats)
            'floorboard_std': QColor('#e6d3b3'),
            'floorboard_custom': QColor('#e6d3b3'),
            'wall_panel': QColor('#e2b86b'), # tan/yellow (plywood)
            'cap_panel': QColor('#e2b86b'),
            'cleat': QColor('#e6d3b3'),
            'outline': QColor('#a88c5f'),
            'highlight': QColor('#F44336'),
            'decal': QColor('#111111'),      # black for decals
            'fastener': QColor('#b0b0b0')    # gray for fasteners
        }
        
    def paintEvent(self, event):
        """Base paint event."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), self.colors['background'])
        
        # Draw title
        painter.setPen(QPen(self.colors['text'], 1))
        font = painter.font()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 18, self.title)


class SkidVisualizationWidget(BaseVisualizationWidget):
    """Widget for visualizing the skid layout."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = "Skid Layout Visualization"
        self.data = None
        
    def update_data(self, skid_results):
        """Update with skid calculation results."""
        self.data = skid_results
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # Scale for drawing - we'll use a scale where 1 inch = 3 pixels
        scale = min(width / (self.data.get('crate_overall_width_calculated', 80) * 1.2), 
                   (height - 40) / (self.data.get('skid_actual_length', 120) * 1.2))
        
        # Draw coordinate system
        painter.setPen(QPen(self.colors['axis'], 1, Qt.PenStyle.DashLine))
        painter.drawLine(int(center_x), 30, int(center_x), height - 10)  # Y-axis
        painter.drawLine(10, int(center_y), width - 10, int(center_y))  # X-axis
        
        # Draw skids
        skid_count = self.data.get('skid_count', 0)
        skid_width = self.data.get('skid_actual_width', 3.5) * scale
        skid_length = self.data.get('skid_actual_length', 100) * scale
        skid_spacing = self.data.get('actual_center_to_center_spacing', 0) * scale
        first_pos_x = self.data.get('first_skid_position_offset_x', 0) * scale
        
        painter.setPen(QPen(self.colors['outline'], 2))
        painter.setBrush(QBrush(self.colors['skid']))
        
        # Draw each skid
        for i in range(skid_count):
            # Calculate position of this skid's center
            skid_center_x = center_x + first_pos_x + (i * skid_spacing)
            skid_left = skid_center_x - (skid_width / 2)
            
            # Draw the skid
            painter.drawRect(int(skid_left), int(center_y - (skid_length / 2)), 
                            int(skid_width), int(skid_length))
            
            # Label the skid
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            label_x = skid_left + (skid_width / 2) - 5
            label_y = center_y
            painter.drawText(int(label_x), int(label_y), f"{i+1}")
            
        # Draw information text
        painter.setPen(QPen(self.colors['text'], 1))
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)
        
        info_text = [
            f"Skid Type: {self.data.get('skid_type_nominal', '-')}",
            f"Skid Count: {skid_count}",
            f"Spacing: {self.data.get('actual_center_to_center_spacing', 0):.2f}\"",
            f"Skid Length: {self.data.get('skid_actual_length', 0):.2f}\""
        ]
        
        for i, text in enumerate(info_text):
            painter.drawText(10, height - 20 - (i * 15), text)


class FloorboardVisualizationWidget(BaseVisualizationWidget):
    """Widget for visualizing the floorboard layout."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = "Floorboard Layout Visualization"
        self.data = None
        
    def update_data(self, floorboard_results):
        """Update with floorboard calculation results."""
        self.data = floorboard_results
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        margin = 40
        
        # Get floorboard data
        board_length = self.data.get('board_length_x', 100)
        target_span = self.data.get('target_span_to_fill_y', 50)
        std_board_width = self.data.get('standard_board_actual_width', 7.25)
        
        # Calculate scale
        scale_x = (width - 2 * margin) / board_length
        scale_y = (height - 2 * margin) / target_span
        scale = min(scale_x, scale_y)
        
        # Draw board outlines
        x_offset = margin + (width - 2 * margin - board_length * scale) / 2
        y_offset = margin + (height - 2 * margin - target_span * scale) / 2
        
        # Draw boards from the details
        boards = self.data.get('boards_placed_details', [])
        for board in boards:
            board_width = board.get('width', std_board_width)
            board_y_pos = board.get('y_pos', 0)
            
            # Set color based on board type
            if board.get('type') == 'custom_center':
                painter.setBrush(QBrush(self.colors['floorboard_custom']))
            else:
                painter.setBrush(QBrush(self.colors['floorboard_std']))
                
            painter.setPen(QPen(self.colors['outline'], 2))
            
            # Draw board
            painter.drawRect(
                int(x_offset),
                int(y_offset + board_y_pos * scale),
                int(board_length * scale),
                int(board_width * scale)
            )
            
            # Add label
            painter.setPen(QPen(self.colors['text'], 1))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            label_y = y_offset + board_y_pos * scale + (board_width * scale / 2)
            
            if board.get('type') == 'custom_center':
                text = f"Custom: {board_width:.2f}\""
            else:
                text = f"{self.data.get('standard_board_nominal_type', '2x?')}"
                
            painter.drawText(int(x_offset + 10), int(label_y), text)
        
        # Draw legend and information
        painter.setPen(QPen(self.colors['text'], 1))
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)
        
        legend_x = width - 150
        legend_y = 40
        
        # Standard board legend
        painter.setBrush(QBrush(self.colors['floorboard_std']))
        painter.drawRect(legend_x, legend_y, 20, 10)
        painter.drawText(legend_x + 25, legend_y + 10, "Standard Board")
        
        # Custom board legend
        painter.setBrush(QBrush(self.colors['floorboard_custom']))
        painter.drawRect(legend_x, legend_y + 20, 20, 10)
        painter.drawText(legend_x + 25, legend_y + 30, "Custom Fill")
        
        # Info text
        info_text = [
            f"Total Span: {target_span:.2f}\"",
            f"Std Boards: {self.data.get('std_boards_front_count', 0) + self.data.get('std_boards_back_count', 0)}",
            f"Custom Boards: {self.data.get('custom_board_count', 0)}",
            f"Remaining Gap: {self.data.get('final_gap_y_remaining', 0):.2f}\""
        ]
        
        for i, text in enumerate(info_text):
            painter.drawText(10, height - 20 - (i * 15), text)


class WallVisualizationWidget(BaseVisualizationWidget):
    """Widget for visualizing the wall panels."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = "Wall Panel Visualization"
        self.data = None
        
    def update_data(self, wall_results):
        """Update with wall calculation results."""
        self.data = wall_results
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        margin = 40
        
        # Extract data
        side_panel_data = self.data.get('side_panels', {})
        end_panel_data = self.data.get('end_panels', {})
        
        side_width = side_panel_data.get('panel_width_dim', 100)
        side_height = side_panel_data.get('panel_height_dim', 50)
        end_width = end_panel_data.get('panel_width_dim', 50)
        end_height = end_panel_data.get('panel_height_dim', 50)
        
        # Calculate scale
        max_dim = max(side_width, side_height, end_width, end_height)
        scale = min((width - 2 * margin) / (side_width + end_width + 20), 
                   (height - 2 * margin) / (max(side_height, end_height) + 20))
        
        # Get removable panel info
        removable_info = self.data.get('removable_panels', {})
        removable_positions = removable_info.get('positions', [])
        
        # Draw side panel 1
        x_pos = margin
        y_pos = margin
        panel_color = self.colors['wall_panel']
        outline_color = self.colors['outline']
        cleat_color = self.colors['cleat']
        
        if 'side_1' in removable_positions:
            outline_color = self.colors['highlight']
            
        # Panel background
        painter.setBrush(QBrush(panel_color))
        painter.setPen(QPen(outline_color, 2))
        painter.drawRect(int(x_pos), int(y_pos), int(side_width * scale), int(side_height * scale))
        
        # Draw cleats
        painter.setBrush(QBrush(cleat_color))
        cleat_width = side_panel_data.get('cleats', {}).get('horizontal_edge_length', side_width - 2) * scale
        cleat_height = 5  # Simplified cleat height visual
        
        # Horizontal cleats (top & bottom)
        painter.drawRect(int(x_pos + ((side_width * scale) - cleat_width) / 2), int(y_pos), 
                         int(cleat_width), int(cleat_height))
        painter.drawRect(int(x_pos + ((side_width * scale) - cleat_width) / 2), int(y_pos + side_height * scale - cleat_height), 
                         int(cleat_width), int(cleat_height))
        
        # Label
        painter.setPen(QPen(self.colors['text'], 1))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        label_text = "Side Panel 1"
        if 'side_1' in removable_positions:
            label_text += " (Removable)"
        painter.drawText(int(x_pos + 10), int(y_pos + side_height * scale - 10), label_text)
        
        # Draw end panel
        x_pos = margin + side_width * scale + 20
        
        if 'end_1' in removable_positions:
            outline_color = self.colors['highlight']
        else:
            outline_color = self.colors['outline']
            
        # Panel background  
        painter.setBrush(QBrush(panel_color))
        painter.setPen(QPen(outline_color, 2))
        painter.drawRect(int(x_pos), int(y_pos), int(end_width * scale), int(end_height * scale))
        
        # Draw cleats (vertical)
        cleat_width = 5  # Simplified cleat width visual
        cleat_height = end_panel_data.get('cleats', {}).get('vertical_edge_length', end_height) * scale
        
        painter.setBrush(QBrush(cleat_color))
        painter.drawRect(int(x_pos), int(y_pos), int(cleat_width), int(cleat_height))
        painter.drawRect(int(x_pos + end_width * scale - cleat_width), int(y_pos), 
                         int(cleat_width), int(cleat_height))
        
        # Label
        painter.setPen(QPen(self.colors['text'], 1))
        label_text = "End Panel 1"
        if 'end_1' in removable_positions:
            label_text += " (Removable)"
        painter.drawText(int(x_pos + 10), int(y_pos + end_height * scale - 10), label_text)
        
        # Draw Style B indicator if applicable
        if removable_info.get('drop_end_style', False):
            painter.setPen(QPen(self.colors['highlight'], 1.5))
            font = painter.font()
            font.setPointSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(10, height - 10, "Style B: Drop-End Style Panels")


class CapVisualizationWidget(BaseVisualizationWidget):
    """Widget for visualizing the cap assembly."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = "Cap Assembly Visualization"
        self.data = None
        
    def update_data(self, cap_results):
        """Update with cap calculation results."""
        self.data = cap_results
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        margin = 40
        
        # Extract data
        cap_panel = self.data.get('cap_panel', {})
        long_cleats = self.data.get('longitudinal_cleats', {})
        trans_cleats = self.data.get('transverse_cleats', {})
        
        panel_width = cap_panel.get('width', 80)
        panel_length = cap_panel.get('length', 100)
        
        # Calculate scale
        scale = min((width - 2 * margin) / panel_length, (height - 2 * margin) / panel_width)
        
        # Set colors
        panel_color = self.colors['cap_panel']
        outline_color = self.colors['outline']
        cleat_color = self.colors['cleat']
        
        if cap_panel.get('removable', False):
            outline_color = self.colors['highlight']
        
        # Draw panel
        x_pos = margin + (width - 2 * margin - panel_length * scale) / 2
        y_pos = margin + (height - 2 * margin - panel_width * scale) / 2
        
        painter.setBrush(QBrush(panel_color))
        painter.setPen(QPen(outline_color, 2))
        painter.drawRect(int(x_pos), int(y_pos), int(panel_length * scale), int(panel_width * scale))
        
        # Draw longitudinal cleats
        painter.setBrush(QBrush(cleat_color))
        painter.setPen(QPen(self.colors['outline'], 1))
        
        long_count = long_cleats.get('count', 0)
        long_positions = long_cleats.get('positions_from_center', [])
        long_cleat_width = long_cleats.get('width', 3.5) * scale
        
        # Origin is center of panel
        center_x = x_pos + (panel_length * scale / 2)
        center_y = y_pos + (panel_width * scale / 2)
        
        for pos_y in long_positions:
            cleat_y = center_y + pos_y * scale - long_cleat_width / 2
            painter.drawRect(int(x_pos), int(cleat_y), int(panel_length * scale), int(long_cleat_width))
        
        # Draw transverse cleats
        trans_count = trans_cleats.get('count', 0)
        trans_positions = trans_cleats.get('positions_from_center', [])
        trans_cleat_width = trans_cleats.get('width', 3.5) * scale
        
        for pos_x in trans_positions:
            cleat_x = center_x + pos_x * scale - trans_cleat_width / 2
            painter.drawRect(int(cleat_x), int(y_pos), int(trans_cleat_width), int(panel_width * scale))
        
        # Draw label
        painter.setPen(QPen(self.colors['text'], 1))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        
        label_text = f"Cap Panel ({panel_length:.1f}\" x {panel_width:.1f}\")"
        if cap_panel.get('removable', False):
            label_text += " (Removable)"
        
        painter.drawText(int(x_pos + 10), int(y_pos + 20), label_text)
        
        # Draw fastener info if removable
        if cap_panel.get('removable', False) and 'fasteners' in self.data:
            fasteners = self.data['fasteners']
            
            info_text = []
            if fasteners.get('klimps_required', False):
                info_text.append(f"Klimps: {fasteners.get('klimp_count', 0)}")
            if fasteners.get('lag_screws_required', False):
                info_text.append(f"Lag Screws: {fasteners.get('lag_screw_count', 0)}")
            if fasteners.get('exemption_applies', False):
                info_text.append("Small Top Exemption Applied")
            
            y_text = height - 30
            for text in info_text:
                painter.drawText(10, y_text, text)
                y_text -= 15


class CrateVisualizationManager:
    """Manager class for integrating visualizations into the UI."""
    
    def __init__(self, parent_widget=None):
        """Initialize visualization widgets and layout."""
        self.parent = parent_widget
        
        if parent_widget:
            # Use grid layout for a more compact display
            self.layout = QGridLayout()
            self.layout.setContentsMargins(5, 5, 5, 5)
            self.layout.setSpacing(5)
            
            # Create visualization widgets
            self.skid_viz = SkidVisualizationWidget()
            self.floor_viz = FloorboardVisualizationWidget()
            self.wall_viz = WallVisualizationWidget()
            self.cap_viz = CapVisualizationWidget()
            
            # Adjust minimum heights for more compact display
            min_height = 300
            self.skid_viz.setMinimumHeight(min_height)
            self.floor_viz.setMinimumHeight(min_height)
            self.wall_viz.setMinimumHeight(min_height)
            self.cap_viz.setMinimumHeight(min_height)
            
            # Add widgets to grid layout - 2x2 grid
            self.layout.addWidget(self.skid_viz, 0, 0)
            self.layout.addWidget(self.floor_viz, 0, 1)
            self.layout.addWidget(self.wall_viz, 1, 0)
            self.layout.addWidget(self.cap_viz, 1, 1)
            
            self.parent.setLayout(self.layout)
    
    def update_visualizations(self, skid_results=None, floorboard_results=None, 
                             wall_results=None, cap_results=None):
        """Update all visualizations with calculation results."""
        if skid_results:
            self.skid_viz.update_data(skid_results)
        
        if floorboard_results:
            self.floor_viz.update_data(floorboard_results)
            
        if wall_results:
            self.wall_viz.update_data(wall_results)
            
        if cap_results:
            self.cap_viz.update_data(cap_results)
