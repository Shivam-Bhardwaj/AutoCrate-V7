#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Specialized visualization widgets for the Base Assembly tab.
Provides detailed renderings for floorboards (top view) and skids (front view).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont
from PyQt6.QtCore import Qt, QRectF, QPointF

class BaseVisualizationWidget(QWidget):
    """Base class for all specialized visualization widgets."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(250)
        self.title = "Visualization"
        # Colors based on crate image
        self.colors = {
            'background': QColor('#ffffff'),  # white background
            'grid': QColor('#f0f0f0'),
            'axis': QColor('#cccccc'),
            'text': QColor('#222222'),
            'skid': QColor('#b07c24'),        # darker brown for skids
            'floorboard_std': QColor('#d9a441'),  # medium gold for std floorboards
            'floorboard_custom': QColor('#e6d3b3'),  # lighter for custom boards
            'outline': QColor('#a88c5f'),     # dark outline
            'highlight': QColor('#F44336'),   # highlight color
            'fastener': QColor('#0055aa')     # blue for fasteners
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
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 25, self.title)


class FloorboardTopView(BaseVisualizationWidget):
    """Widget for visualizing floorboards from a top-down perspective."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = "Floorboard Top View"
        self.floorboard_data = None
        self.show_dimensions = True  # Whether to show dimensional annotations
        
    def set_data(self, floorboard_data):
        """Update with floorboard calculation data."""
        self.floorboard_data = floorboard_data
        self.update()
        
    def paintEvent(self, event):
        """Render the floorboards top-down view."""
        super().paintEvent(event)
        
        if not self.floorboard_data:
            # Draw instructions if no data
            painter = QPainter(self)
            painter.setPen(QPen(self.colors['text'], 1))
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(20, 50, "Run calculations to view floorboards")
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get drawing area
        width = self.width()
        height = self.height()
        
        # Get floorboard data
        std_board_width = self.floorboard_data.get('standard_board_actual_width', 7.25)
        std_boards_count = self.floorboard_data.get('std_boards_front_count', 4) + \
                          self.floorboard_data.get('std_boards_back_count', 4)
        custom_board_width = self.floorboard_data.get('custom_board_actual_width', 0.0)
        has_custom_board = custom_board_width > 0.0
        total_span = self.floorboard_data.get('target_span_to_fill', 96.0)
        board_length = self.floorboard_data.get('board_length', 96.0)
        
        # Calculate scaling and positioning
        margin = 50
        draw_width = width - 2 * margin
        draw_height = height - 2 * margin
        
        # Scale the drawing to fit the view
        scale_x = draw_width / board_length
        scale_y = draw_height / total_span
        scale = min(scale_x, scale_y)
        
        # Center the drawing
        center_x = width / 2
        center_y = height / 2
        board_center_x = board_length / 2 * scale
        board_center_y = total_span / 2 * scale
        offset_x = center_x - board_center_x
        offset_y = center_y - board_center_y
        
        # Draw outline
        outline_pen = QPen(self.colors['outline'], 2)
        painter.setPen(outline_pen)
        outline_rect = QRectF(
            offset_x, 
            offset_y, 
            board_length * scale, 
            total_span * scale
        )
        painter.drawRect(outline_rect)
        
        # Draw floorboards
        board_pen = QPen(self.colors['outline'], 1)
        painter.setPen(board_pen)
        
        y_position = 0.0
        
        # Draw standard boards from left (front)
        for i in range(self.floorboard_data.get('std_boards_front_count', 4)):
            painter.setBrush(QBrush(self.colors['floorboard_std']))
            # Create QRectF object for drawing rectangle to fix TypeError
            front_board_rect = QRectF(
                offset_x,
                offset_y + y_position * scale,
                board_length * scale,
                std_board_width * scale
            )
            painter.drawRect(front_board_rect)
            
            # Draw wood grain lines
            grain_pen = QPen(self.colors['outline'], 0.5)
            grain_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(grain_pen)
            
            for j in range(1, 10):
                grain_y = offset_y + (y_position + j * std_board_width / 10) * scale
                painter.drawLine(
                    offset_x + 5, grain_y,
                    offset_x + board_length * scale - 5, grain_y
                )
            
            painter.setPen(board_pen)
            y_position += std_board_width
            
        # Draw custom board if present
        if has_custom_board:
            painter.setBrush(QBrush(self.colors['floorboard_custom']))
            custom_rect = QRectF(
                offset_x,
                offset_y + y_position * scale,
                board_length * scale,
                custom_board_width * scale
            )
            painter.drawRect(custom_rect)
            
            # Label custom board
            painter.setPen(QPen(self.colors['text'], 1))
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)
            painter.drawText(
                offset_x + board_length * scale / 2 - 40,
                offset_y + (y_position + custom_board_width/2) * scale,
                "Custom Fill"
            )
            
            painter.setPen(board_pen)
            y_position += custom_board_width
            
        # Draw standard boards from right (back)
        for i in range(self.floorboard_data.get('std_boards_back_count', 4)):
            painter.setBrush(QBrush(self.colors['floorboard_std']))
            # Create QRectF object for drawing rectangle to fix TypeError
            back_board_rect = QRectF(
                offset_x,
                offset_y + y_position * scale,
                board_length * scale,
                std_board_width * scale
            )
            painter.drawRect(back_board_rect)
            
            # Draw wood grain lines
            grain_pen = QPen(self.colors['outline'], 0.5)
            grain_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(grain_pen)
            
            for j in range(1, 10):
                grain_y = offset_y + (y_position + j * std_board_width / 10) * scale
                painter.drawLine(
                    offset_x + 5, grain_y,
                    offset_x + board_length * scale - 5, grain_y
                )
            
            painter.setPen(board_pen)
            y_position += std_board_width
        
        # Draw indicators for fasteners
        painter.setPen(QPen(self.colors['fastener'], 3))
        for i in range(4):  # 4 fastener positions along length
            for j in range(std_boards_count + (1 if has_custom_board else 0)):
                x_pos = offset_x + (i + 1) * board_length * scale / 5
                y_pos = offset_y + (j + 0.5) * std_board_width * scale
                if has_custom_board and j >= self.floorboard_data.get('std_boards_front_count', 4):
                    if j == self.floorboard_data.get('std_boards_front_count', 4):
                        y_pos = offset_y + (self.floorboard_data.get('std_boards_front_count', 4) * std_board_width + custom_board_width/2) * scale
                    else:
                        y_pos = offset_y + (self.floorboard_data.get('std_boards_front_count', 4) * std_board_width + custom_board_width + (j - self.floorboard_data.get('std_boards_front_count', 4) - 0.5) * std_board_width) * scale
                
                painter.drawPoint(QPointF(x_pos, y_pos))
                
        # Draw dimensions if enabled
        if self.show_dimensions:
            dimension_pen = QPen(self.colors['text'], 1)
            painter.setPen(dimension_pen)
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)
            
            # Width dimension
            width_text = f"{board_length:.2f}\""
            painter.drawText(
                int(offset_x + board_length * scale / 2 - 20),
                int(offset_y - 15),
                width_text
            )
            
            # Height dimension
            height_text = f"{total_span:.2f}\""
            painter.drawText(
                int(offset_x - 30),
                int(offset_y + total_span * scale / 2 + 5),
                height_text
            )


class SkidFrontView(BaseVisualizationWidget):
    """Widget for visualizing skids from the front view."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = "Skid Front View"
        self.skid_data = None
        self.show_dimensions = True
        
    def set_data(self, skid_data):
        """Update with skid calculation data."""
        self.skid_data = skid_data
        self.update()
        
    def paintEvent(self, event):
        """Render the skids front view."""
        super().paintEvent(event)
        
        if not self.skid_data:
            # Draw instructions if no data
            painter = QPainter(self)
            painter.setPen(QPen(self.colors['text'], 1))
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(20, 50, "Run calculations to view skids")
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get drawing area
        width = self.width()
        height = self.height()
        
        # Get skid data
        skid_count = self.skid_data.get('skid_count', 3)
        skid_width = self.skid_data.get('skid_actual_width', 3.5)
        skid_height = self.skid_data.get('skid_actual_height', 3.5)
        skid_spacing = self.skid_data.get('spacing_actual', 30.0)
        crate_width = self.skid_data.get('crate_overall_width_calculated', 96.0)
        
        # Calculate total skid span based on count and spacing
        if skid_count == 1:
            total_skid_span = skid_width
        else:
            total_skid_span = (skid_count - 1) * skid_spacing + skid_width
            
        # Calculate scaling and positioning
        margin = 50
        draw_width = width - 2 * margin
        draw_height = height - 2 * margin
        
        # Scale the drawing to fit the view
        scale_x = draw_width / crate_width
        scale_y = draw_height / (skid_height * 2)  # Double skid height for better aspect ratio
        scale = min(scale_x, scale_y)
        
        # Center the drawing
        center_x = width / 2
        center_y = height / 2 + skid_height * scale  # Lower to show floor
        skid_center_x = crate_width / 2 * scale
        offset_x = center_x - skid_center_x
        
        # Draw floor line
        floor_pen = QPen(self.colors['outline'], 2)
        painter.setPen(floor_pen)
        painter.drawLine(
            int(offset_x), 
            int(center_y), 
            int(offset_x + crate_width * scale), 
            int(center_y)
        )
        
        # Draw skids
        skid_pen = QPen(self.colors['outline'], 1)
        painter.setPen(skid_pen)
        
        for i in range(skid_count):
            # Calculate skid position
            if skid_count == 1:
                skid_x = offset_x + (crate_width / 2 - skid_width / 2) * scale
            else:
                start_pos = (crate_width - total_skid_span) / 2
                skid_x = offset_x + (start_pos + i * skid_spacing) * scale
                
            # Draw the skid
            painter.setBrush(QBrush(self.colors['skid']))
            skid_rect = QRectF(
                skid_x,
                center_y - skid_height * scale,
                skid_width * scale,
                skid_height * scale
            )
            painter.drawRect(skid_rect)
            
            # Add some detail to the skid face
            detail_pen = QPen(self.colors['outline'], 0.5)
            detail_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(detail_pen)
            
            # Add grain lines
            for j in range(1, 4):
                detail_y = center_y - skid_height * scale * j / 4
                painter.drawLine(
                    int(skid_x + 2), 
                    int(detail_y),
                    int(skid_x + skid_width * scale - 2), 
                    int(detail_y)
                )
            
            # Reset pen
            painter.setPen(skid_pen)
            
        # Draw dimensions if enabled
        if self.show_dimensions:
            dimension_pen = QPen(self.colors['text'], 1)
            painter.setPen(dimension_pen)
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)
            
            # Width dimension
            width_text = f"{crate_width:.2f}\""
            painter.drawText(
                int(offset_x + crate_width * scale / 2 - 20),
                int(center_y + 20),
                width_text
            )
            
            # Show skid count and spacing
            info_text = f"Skid Count: {skid_count}"
            spacing_text = f"Spacing: {skid_spacing:.2f}\""
            painter.drawText(10, 50, info_text)
            painter.drawText(10, 70, spacing_text)
            
            # Draw dimension lines and skid spacing if more than 1 skid
            if skid_count > 1:
                start_pos = (crate_width - total_skid_span) / 2
                
                # Draw spacing dimension for first pair of skids
                first_skid_center = start_pos + skid_width / 2
                second_skid_center = first_skid_center + skid_spacing
                
                spacing_line_y = center_y - skid_height * scale - 15
                
                # Draw dimension line
                painter.setPen(QPen(self.colors['text'], 1, Qt.PenStyle.DashLine))
                
                # Draw arrow from first to second skid
                first_x = offset_x + first_skid_center * scale
                second_x = offset_x + second_skid_center * scale
                
                painter.drawLine(
                    int(first_x), 
                    int(spacing_line_y), 
                    int(second_x), 
                    int(spacing_line_y)
                )
                
                # Draw small vertical end lines
                painter.drawLine(
                    int(first_x), 
                    int(spacing_line_y - 3), 
                    int(first_x), 
                    int(spacing_line_y + 3)
                )
                painter.drawLine(
                    int(second_x), 
                    int(spacing_line_y - 3), 
                    int(second_x), 
                    int(spacing_line_y + 3)
                )
                
                # Draw spacing text
                painter.setPen(QPen(self.colors['text'], 1))
                spacing_label = f"{skid_spacing:.2f}\""
                painter.drawText(
                    int((first_x + second_x) / 2 - 15),
                    int(spacing_line_y - 5),
                    spacing_label
                )
