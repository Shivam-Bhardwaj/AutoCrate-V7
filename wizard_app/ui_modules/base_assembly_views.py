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
            'nail_head': QColor('#888888')    # Grey for nail heads
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
        self.skid_data = None  # Add skid_data attribute
        self.show_dimensions = True  # Whether to show dimensional annotations
        
    def set_data(self, floorboard_data, skid_data=None):
        """Update with floorboard and optional skid calculation data."""
        import traceback
        stack = traceback.extract_stack()
        caller = stack[-2]  # The caller of this method
        print(f"FloorboardTopView.set_data called from {caller.filename}:{caller.lineno}")
        print(f"  with skid_data={skid_data is not None}")
        
        if skid_data is not None:
            print(f"  skid_data type: {type(skid_data)}")
            print(f"  skid_data has 'exp_data': {'exp_data' in skid_data if isinstance(skid_data, dict) else 'Not a dict'}")
        else:
            # Print more of the call stack when skid_data is None to help diagnose
            print("CALL STACK FOR NONE skid_data:")
            for frame in stack[-5:-1]:  # Print last 4 frames
                print(f"  {frame.filename}:{frame.lineno} in {frame.name}")
        
        self.floorboard_data = floorboard_data
        # Store skid_data only if it's not None - preserve previous data if it exists
        if skid_data is not None:
            self.skid_data = skid_data
        print(f"After assignment, self.skid_data is {self.skid_data is not None}")
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
            front_board_rect = QRectF(
                offset_x,
                offset_y + y_position * scale,
                board_length * scale,
                std_board_width * scale
            )
            painter.drawRect(front_board_rect)
            
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
                int(offset_x + board_length * scale / 2 - 40),
                int(offset_y + (y_position + custom_board_width/2) * scale),
                "Custom Fill"
            )
            
            painter.setPen(board_pen)
            y_position += custom_board_width
            
        # Draw standard boards from right (back)
        for i in range(self.floorboard_data.get('std_boards_back_count', 4)):
            painter.setBrush(QBrush(self.colors['floorboard_std']))
            back_board_rect = QRectF(
                offset_x,
                offset_y + y_position * scale,
                board_length * scale,
                std_board_width * scale
            )
            painter.drawRect(back_board_rect)
            
            painter.setPen(board_pen)
            y_position += std_board_width
        
        # Draw indicators for fasteners (nail heads)
        nail_diameter = 3 # Diameter of the nail head in pixels
        current_nail_color = QColor(0,0,0) # Default to black if something goes wrong

        skid_count_for_nails = 0
        skid_positions_for_nails = [] # Unscaled, relative to board_length start
        diagnostic_info = []

        # DETAILED DIAGNOSTICS
        # Draw diagnostic text showing what's in self.skid_data
        painter.setPen(QPen(QColor(255, 0, 0), 1))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)

        # Determine if we can use skid data to position nails
        use_skid_data = False
        s_count = 0
        
        if self.skid_data is None:
            diagnostic_info.append("skid_data is None")
            current_nail_color = QColor(0, 255, 0)  # GREEN - no skid data at all
        elif not isinstance(self.skid_data, dict):
            diagnostic_info.append(f"skid_data type: {type(self.skid_data)}")
            current_nail_color = QColor(0, 0, 255)  # BLUE - wrong type
        elif 'exp_data' not in self.skid_data:
            diagnostic_info.append("No 'exp_data' in skid_data")
            diagnostic_info.append(f"Keys: {list(self.skid_data.keys())}")
            current_nail_color = QColor(255, 0, 255)  # PURPLE - no exp_data
        else:
            # We have skid_data and it has exp_data
            exp_data = self.skid_data['exp_data']
            s_count = exp_data.get('CALC_Skid_Count', 0)
            s_width = self.skid_data.get('skid_actual_width', 3.5) # From top level
            s_pitch = exp_data.get('CALC_Skid_Pitch', 24.0)
            
            diagnostic_info.append(f"s_count: {s_count}")
            diagnostic_info.append(f"s_width: {s_width}") 
            diagnostic_info.append(f"s_pitch: {s_pitch}")
            
            if s_count > 0:
                # We have valid skid count - use it!
                use_skid_data = True
                current_nail_color = QColor(255, 0, 0) # BRIGHT RED - using skid data
            else:
                diagnostic_info.append(f"s_count is zero or invalid: {s_count}")
                current_nail_color = QColor(255, 165, 0) # ORANGE - skid data exists but count invalid
        
        # Now set up nail positions based on what we found
        if use_skid_data:
            # Use actual skid count and positions
            skid_count_for_nails = s_count
            if s_count == 1:
                # Center the single skid
                skid_positions_for_nails.append(board_length / 2)
            else:
                # Calculate total span of skids (edge to edge of outermost skids)
                total_skid_span_unscaled = (s_count - 1) * s_pitch + s_width
                # Start position of the first skid (left edge)
                first_skid_edge_unscaled = (board_length - total_skid_span_unscaled) / 2
                for skid_idx in range(s_count):
                    # Center of current skid
                    skid_center_unscaled = first_skid_edge_unscaled + skid_idx * s_pitch + s_width / 2
                    skid_positions_for_nails.append(skid_center_unscaled)
        else:
            # Fallback to default 4 rows
            skid_count_for_nails = 4 # Default to 4 rows if no skid data
            for i in range(skid_count_for_nails):
                skid_positions_for_nails.append((i + 1) * board_length / (skid_count_for_nails + 1)) # Evenly space 4 rows
        
        # Draw diagnostic info at top-left of view
        for i, info in enumerate(diagnostic_info):
            painter.drawText(10, 15 + (i * 15), info)
        
        nail_head_pen = QPen(current_nail_color, 1)
        painter.setPen(nail_head_pen)
        painter.setBrush(QBrush(current_nail_color))

        for skid_center_unscaled in skid_positions_for_nails:
            for j_idx in range(std_boards_count + (1 if has_custom_board else 0)):
                x_pos_center = offset_x + skid_center_unscaled * scale
                current_y_offset = 0.0
                # Determine y-position based on board index
                if j_idx < self.floorboard_data.get('std_boards_front_count', 4):
                    current_y_offset = j_idx * std_board_width + std_board_width / 2
                elif has_custom_board and j_idx == self.floorboard_data.get('std_boards_front_count', 4):
                    current_y_offset = self.floorboard_data.get('std_boards_front_count', 4) * std_board_width + custom_board_width / 2
                else:
                    base_offset = self.floorboard_data.get('std_boards_front_count', 4) * std_board_width
                    if has_custom_board:
                        base_offset += custom_board_width
                    current_y_offset = base_offset + (j_idx - self.floorboard_data.get('std_boards_front_count', 4) - (1 if has_custom_board else 0)) * std_board_width + std_board_width / 2

                y_pos_center = offset_y + current_y_offset * scale
                # Draw a small circle for the nail head
                painter.drawEllipse(QPointF(x_pos_center, y_pos_center), nail_diameter / 2, nail_diameter / 2)
                
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
    """Widget for visualizing skids front view."""
    
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
        
        # Get skid data from self.skid_data (which is the dictionary from skid_logic)
        exp_data = self.skid_data.get('exp_data', {})

        skid_count = exp_data.get('CALC_Skid_Count', 1)  # Use 1 as default if key not found
        skid_width = self.skid_data.get('skid_actual_width', 3.5) # Assumed top-level from skid_results
        skid_height = self.skid_data.get('skid_actual_height', 3.5) # Assumed top-level from skid_results
        skid_spacing = exp_data.get('CALC_Skid_Pitch', 24.0) # Default to a common spacing
        # Try to get a sensible default for crate_width if CALC_Crate_Overall_Width_Y is not present
        # Ensure cleat_thickness is included, similar to skid_logic.py
        # Input parameters like 'product_width', 'clearance_side', 'panel_thickness', 'cleat_thickness' 
        # are expected at the top level of self.skid_data.
        cleat_thickness_val = self.skid_data.get('cleat_thickness', 0.75) # Defaulting to 0.75 if not found
        default_crate_width = self.skid_data.get('product_width', 38.0) + \
                              2 * self.skid_data.get('clearance_side', 1.0) + \
                              2 * self.skid_data.get('panel_thickness', 0.25) + \
                              2 * cleat_thickness_val
        crate_width = exp_data.get('CALC_Crate_Overall_Width_Y', default_crate_width)
        
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
        
        # Draw ground plane (Z=0)
        ground_pen = QPen(self.colors['outline'], 2)
        painter.setPen(ground_pen)
        painter.drawLine(
            int(offset_x), 
            int(center_y), 
            int(offset_x + crate_width * scale), 
            int(center_y)
        )
        
        # Label Z=0 plane
        painter.setPen(QPen(self.colors['text'], 1))
        painter.drawText(int(offset_x - 30), int(center_y), "Z=0")
        
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
