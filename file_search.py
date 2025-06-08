import os
import re
import sys
import shutil
import json
import subprocess
import platform
import webbrowser
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QFileDialog, 
                             QMessageBox, QGraphicsBlurEffect, QGraphicsOpacityEffect, QProgressBar, QMenu)
from PyQt6.QtGui import (QPainter, QLinearGradient, QColor, QBrush, QFont, QPalette, QPen, QPixmap, QRadialGradient)
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup, QPoint, QPointF, QTimer, QThread, pyqtSignal, QSize
import random
import math

def normalize_filename(filename):
    """Normalize the filename by converting to lowercase and removing non-alphanumeric characters except for letters, numbers, and dots."""
    return re.sub(r'[^a-zA-Z0-9.]', '', filename.lower())

def search_files(directory, keyword, indexed_files=None):
    results = []
    normalized_keyword = normalize_filename(keyword)

    source_files = indexed_files if indexed_files else []
    if not source_files and directory:
        for root, _, files in os.walk(directory):
            for file in files:
                source_files.append(os.path.join(root, file))

    if not normalized_keyword:
        return source_files
    else:
        for file_path in source_files:
            normalized_filename = normalize_filename(file_path)
            if normalized_keyword in normalized_filename:
                results.append(file_path)
    return results

def open_file(file_path):
    """Open a file using the system's default application."""
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(file_path)
        print(f"Attempting to open file: {abs_path}")
        
        if platform.system() == 'Windows':
            os.startfile(abs_path)
        elif platform.system() == 'Darwin':
            subprocess.run(f'open "{abs_path}"', shell=True, env=os.environ)
        else:  # Linux and others
            # Try xdg-open with full path
            subprocess.run(f'xdg-open "{abs_path}"', shell=True, env=os.environ)
        
        print("File open command executed")
    except Exception as e:
        print(f"Error opening file: {str(e)}")
        import traceback
        print("Full error traceback:")
        print(traceback.format_exc())

def open_file_explorer(file_path):
    """Open the file's containing folder in the system's file manager."""
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(file_path)
        dir_path = os.path.dirname(abs_path)
        print(f"Attempting to open folder: {dir_path}")
        
        if platform.system() == 'Windows':
            subprocess.run(f'explorer /select,"{abs_path}"', shell=True, env=os.environ)
        elif platform.system() == 'Darwin':
            subprocess.run(f'open -R "{abs_path}"', shell=True, env=os.environ)
        else:  # Linux and others
            subprocess.run(f'xdg-open "{dir_path}"', shell=True, env=os.environ)
        
        print("Folder open command executed")
    except Exception as e:
        print(f"Error opening file explorer: {str(e)}")
        import traceback
        print("Full error traceback:")
        print(traceback.format_exc())

class AnimatedLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
    def setText(self, text):
        super().setText(text)
        
    def animate_text_change(self, new_text):
        try:
            self.setText(new_text)
        except Exception as e:
            print(f"Error updating label: {str(e)}")

class AeroButton(QPushButton):
    """Custom button with authentic Aero glass effect."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(255, 255, 255, 180),
                    stop:0.3 rgba(220, 240, 255, 140),
                    stop:0.6 rgba(200, 230, 255, 120),
                    stop:1 rgba(180, 220, 255, 100));
                border: 1px solid rgba(255, 255, 255, 180);
                border-radius: 3px;
                padding: 6px;
                color: rgba(0, 0, 0, 180);
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 220),
                    stop:0.3 rgba(230, 245, 255, 180),
                    stop:0.6 rgba(210, 235, 255, 160),
                    stop:1 rgba(190, 225, 255, 140));
                border: 1px solid rgba(255, 255, 255, 220);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 220, 255, 100),
                    stop:0.3 rgba(200, 230, 255, 120),
                    stop:0.6 rgba(220, 240, 255, 140),
                    stop:1 rgba(255, 255, 255, 180));
                padding-top: 7px;
                padding-bottom: 5px;
            }
        """)
        self.setMinimumHeight(28)
        
        # Add click animation
        self.click_animation = QPropertyAnimation(self, b"geometry")
        self.click_animation.setDuration(100)
        self.click_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Add hover animation
        self.hover_opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.hover_opacity)
        self.hover_opacity.setOpacity(1.0)
        
        self.hover_animation = QPropertyAnimation(self.hover_opacity, b"opacity")
        self.hover_animation.setDuration(150)
        
    def enterEvent(self, event):
        self.hover_animation.setStartValue(1.0)
        self.hover_animation.setEndValue(0.8)
        self.hover_animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.hover_animation.setStartValue(0.8)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            rect = self.geometry()
            self.click_animation.setStartValue(rect)
            self.click_animation.setEndValue(rect.adjusted(1, 1, -1, -1))
            self.click_animation.start()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            rect = self.geometry()
            self.click_animation.setStartValue(rect)
            self.click_animation.setEndValue(rect.adjusted(-1, -1, 1, 1))
            self.click_animation.start()
        super().mouseReleaseEvent(event)

class AnimatedButton(AeroButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.pulse_animation = QPropertyAnimation(self, b"geometry")
        self.pulse_animation.setDuration(1500)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.is_pulsing = False
        
    def start_pulse(self):
        if not self.is_pulsing:
            self.is_pulsing = True
            rect = self.geometry()
            self.pulse_animation.setStartValue(rect)
            self.pulse_animation.setEndValue(rect.adjusted(-2, -2, 2, 2))
            self.pulse_animation.setLoopCount(-1)  # Infinite loop
            self.pulse_animation.start()
            
    def stop_pulse(self):
        if self.is_pulsing:
            self.is_pulsing = False
            self.pulse_animation.stop()
            rect = self.geometry()
            self.setGeometry(rect)

class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(255, 255, 255, 180);
                border-radius: 3px;
                text-align: center;
                background: rgba(255, 255, 255, 100);
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 220, 255, 180),
                    stop:1 rgba(180, 200, 255, 140));
                border-radius: 2px;
            }
        """)
        self.wave_animation = QPropertyAnimation(self, b"value")
        self.wave_animation.setDuration(1000)
        self.wave_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.is_waving = False
        
    def start_wave(self):
        if not self.is_waving:
            self.is_waving = True
            self.wave_animation.setStartValue(0)
            self.wave_animation.setEndValue(100)
            self.wave_animation.setLoopCount(-1)
            self.wave_animation.start()
            
    def stop_wave(self):
        if self.is_waving:
            self.is_waving = False
            self.wave_animation.stop()
            self.setValue(100)  # Set to 100% when stopping
            self.hide()  # Hide the progress bar immediately

class AnimatedListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.animation_duration = 800  # Longer duration for more magical effect
        self.animations = []
        self.item_delay = 50  # Longer delay between items for more dramatic effect
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        item = self.itemAt(position)
        if item:
            # Get the widget from the item
            widget = self.itemWidget(item)
            # Get the label from the widget's layout
            label = widget.findChild(QLabel)
            if label:
                file_path = label.text()
                menu = QMenu()
                open_action = menu.addAction("Open")
                show_in_folder_action = menu.addAction("Show in File Manager")
                
                action = menu.exec(self.mapToGlobal(position))
                if action == open_action:
                    open_file(file_path)
                elif action == show_in_folder_action:
                    open_file_explorer(file_path)
        
    def add_item_with_animation(self, text):
        # Create a widget to hold the text
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)  # Increased padding
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: rgba(0, 0, 0, 180);
                padding: 2px;
                font-size: 12px;
            }
        """)
        layout.addWidget(label)
        
        # Create opacity effect for the widget
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(0.0)
        
        # Create and configure the animation
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(self.animation_duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Calculate delay based on item position, ensure it's not negative
        delay = max(0, (self.count() - 1) * self.item_delay)
        
        # Create list item and set the widget
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        # Add extra height to the item
        size_hint = item.sizeHint()
        item.setSizeHint(QSize(size_hint.width(), size_hint.height() + 8))  # Add 8 pixels of height
        self.addItem(item)
        self.setItemWidget(item, widget)
        
        # Keep reference to prevent garbage collection
        self.animations.append((animation, widget, item))
        
        def cleanup():
            if (animation, widget, item) in self.animations:
                self.animations.remove((animation, widget, item))
        
        animation.finished.connect(cleanup)
        
        # Start animation after delay
        QTimer.singleShot(delay, lambda: animation.start())

class SearchWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)  # current, total
    large_directory = pyqtSignal(int)  # Signal for large directory detection
    
    def __init__(self, directory, keyword, indexed_files=None):
        super().__init__()
        self.directory = directory
        self.keyword = keyword
        self.indexed_files = indexed_files
        self.is_running = True
        
    def stop(self):
        self.is_running = False
        
    def run(self):
        try:
            # Check if directory exists and is accessible
            if not os.path.exists(self.directory):
                self.error.emit(f"Error: Directory '{self.directory}' does not exist.")
                return
                
            if not os.access(self.directory, os.R_OK):
                self.error.emit(f"Error: No read permission for directory '{self.directory}'")
                return

            if self.indexed_files:
                # Use indexed files if available
                results = search_files(self.directory, self.keyword, self.indexed_files)
                self.finished.emit(results)
            else:
                # For non-indexed search, count files first
                total_files = 0
                try:
                    for _, _, files in os.walk(self.directory):
                        total_files += len(files)
                except Exception as e:
                    self.error.emit(f"Error counting files: {str(e)}")
                    return
                
                if total_files > 10000:  # Warning threshold
                    self.large_directory.emit(total_files)
                    return
                
                # Perform search with progress updates
                results = []
                processed_files = 0
                
                try:
                    for root, _, files in os.walk(self.directory):
                        if not self.is_running:
                            break
                            
                        for file in files:
                            if not self.is_running:
                                break
                                
                            try:
                                file_path = os.path.join(root, file)
                                if self.keyword.lower() in file.lower():
                                    results.append(file_path)
                                
                                processed_files += 1
                                if processed_files % 100 == 0:  # Update progress every 100 files
                                    self.progress.emit(processed_files, total_files)
                            except Exception as e:
                                print(f"Error processing file {file}: {str(e)}")
                                continue
                    
                    self.finished.emit(results)
                except Exception as e:
                    self.error.emit(f"Error during file search: {str(e)}")
                
        except Exception as e:
            self.error.emit(f"Unexpected error: {str(e)}")
            import traceback
            print("Full error traceback:")
            print(traceback.format_exc())

class FileSearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Search - Frosted Glass")
        self.setGeometry(100, 100, 600, 600)
        self.setWindowOpacity(0.95)  # Slightly more transparent
        
        # Initialize UI elements first
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Add Help Button
        self.help_btn = AeroButton("?")
        self.help_btn.setFixedSize(30, 30)  # Make it square
        self.help_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(255, 255, 255, 180),
                    stop:0.3 rgba(220, 240, 255, 140),
                    stop:0.6 rgba(200, 230, 255, 120),
                    stop:1 rgba(180, 220, 255, 100));
                border: 1px solid rgba(255, 255, 255, 180);
                border-radius: 15px;
                padding: 0px;
                color: rgba(0, 0, 0, 180);
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 220),
                    stop:0.3 rgba(230, 245, 255, 180),
                    stop:0.6 rgba(210, 235, 255, 160),
                    stop:1 rgba(190, 225, 255, 140));
                border: 1px solid rgba(255, 255, 255, 220);
            }
        """)
        self.help_btn.clicked.connect(self.show_help)
        
        # Create a horizontal layout for the help button
        help_layout = QHBoxLayout()
        help_layout.addStretch()  # Push button to the right
        help_layout.addWidget(self.help_btn)
        self.layout.addLayout(help_layout)
        
        # Directory Row
        dir_row = QHBoxLayout()
        self.dir_label = QLabel("Directory Path:")
        self.dir_label.setStyleSheet("color: rgba(0, 0, 0, 180);")  # Set label color to black
        self.dir_input = QLineEdit()
        self.browse_btn = AeroButton("Browse")
        self.index_btn = AeroButton("Reindex")
        dir_row.addWidget(self.dir_label)
        dir_row.addWidget(self.dir_input)
        dir_row.addWidget(self.browse_btn)
        dir_row.addWidget(self.index_btn)
        self.layout.addLayout(dir_row)
        
        # Initialize indexing data after UI elements
        self.index_file = 'file_index.json'
        self.indexed_files = []
        self.indexed_directory = None
        
        # Snowflake animation properties
        self.snowflakes = []
        self.snowflake_count = 50  # More snowflakes for better effect
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_snowflakes)
        self.animation_timer.start(16)  # ~60 FPS
        
        # Initialize snowflakes with random positions and velocities
        for _ in range(self.snowflake_count):
            snowflake = {
                'x': random.randint(0, self.width()),
                'y': random.randint(-100, 0),  # Start above the window
                'size': random.randint(2, 6),  # Smaller sizes for snowflakes
                'speed': random.uniform(1, 3),  # Falling speed
                'sway': random.uniform(-1, 1),  # Sideways movement
                'sway_speed': random.uniform(0.02, 0.05)  # Speed of swaying
            }
            self.snowflakes.append(snowflake)
            
        # Load index after UI is initialized
        self.load_index()
        
        # Status Label
        self.status_label = AnimatedLabel("No index loaded")
        self.status_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 220, 255, 160),
                    stop:0.3 rgba(180, 210, 255, 140),
                    stop:0.6 rgba(160, 200, 255, 120),
                    stop:1 rgba(140, 190, 255, 100));
                padding: 8px;
                border-radius: 3px;
                border: 1px solid rgba(255, 255, 255, 180);
                color: rgba(0, 0, 0, 200);
                font-weight: bold;
                font-size: 11px;
            }
        """)
        self.layout.addWidget(self.status_label)  # Add the label directly
        
        # Add a glass highlight effect to the status label
        highlight = QGraphicsBlurEffect()
        highlight.setBlurRadius(1)
        self.status_label.setGraphicsEffect(highlight)
        
        # Search Row
        search_row = QHBoxLayout()
        self.search_label = QLabel("Search Keyword:")
        self.search_label.setStyleSheet("color: rgba(0, 0, 0, 180);")  # Set label color to black
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.on_search)
        self.search_btn = AnimatedButton("Search")
        self.cancel_btn = AnimatedButton("Cancel")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setFixedWidth(60)  # Set fixed width to prevent layout issues
        self.cancel_btn.clicked.connect(self.cancel_search)
        search_row.addWidget(self.search_label)
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_btn)
        search_row.addWidget(self.cancel_btn)
        search_row.addStretch()  # Add stretch to push buttons to the left
        self.layout.addLayout(search_row)
        
        # Add progress bar
        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)
        
        # Results List
        self.results_list = AnimatedListWidget()
        self.results_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.results_list.itemDoubleClicked.connect(self.on_select)
        self.results_list.setStyleSheet("""
            QListWidget {
                background: rgba(60, 64, 72, 120);
                border: 1px solid rgba(255, 255, 255, 180);
                border-radius: 3px;
                color: rgba(0, 0, 0, 180);
            }
            QWidget {
                background: transparent;
            }
            QLabel {
                color: rgba(0, 0, 0, 180);
                padding: 2px;
            }
            QListWidget::item {
                background: transparent;
                border-radius: 2px;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 220, 255, 180),
                    stop:1 rgba(180, 200, 255, 140));
            }
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(220, 240, 255, 180),
                    stop:1 rgba(200, 230, 255, 140));
            }
            /* Custom Scrollbar Styling */
            QScrollBar:vertical {
                border: none;
                background: rgba(60, 64, 72, 40);
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 104, 112, 180),
                    stop:0.5 rgba(80, 84, 92, 160),
                    stop:1 rgba(60, 64, 72, 180));
                min-height: 20px;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 180);
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(120, 124, 132, 200),
                    stop:0.5 rgba(100, 104, 112, 180),
                    stop:1 rgba(80, 84, 92, 200));
            }
            QScrollBar::handle:vertical:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(80, 84, 92, 160),
                    stop:0.5 rgba(60, 64, 72, 140),
                    stop:1 rgba(40, 44, 52, 160));
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: rgba(60, 64, 72, 40);
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(100, 104, 112, 180),
                    stop:0.5 rgba(80, 84, 92, 160),
                    stop:1 rgba(60, 64, 72, 180));
                min-width: 20px;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 180);
            }
            QScrollBar::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(120, 124, 132, 200),
                    stop:0.5 rgba(100, 104, 112, 180),
                    stop:1 rgba(80, 84, 92, 200));
            }
            QScrollBar::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(80, 84, 92, 160),
                    stop:0.5 rgba(60, 64, 72, 140),
                    stop:1 rgba(40, 44, 52, 160));
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        self.layout.addWidget(self.results_list)
        
        # Action Buttons
        action_row = QHBoxLayout()
        self.select_all_btn = AeroButton("Select All")
        self.copy_btn = AeroButton("Copy")
        self.move_btn = AeroButton("Move")
        self.delete_btn = AeroButton("Delete")
        action_row.addWidget(self.select_all_btn)
        action_row.addWidget(self.copy_btn)
        action_row.addWidget(self.move_btn)
        action_row.addWidget(self.delete_btn)
        self.layout.addLayout(action_row)
        
        # Connect buttons
        self.browse_btn.clicked.connect(self.on_browse)
        self.index_btn.clicked.connect(self.on_index)
        self.search_btn.clicked.connect(self.on_search)
        self.select_all_btn.clicked.connect(self.on_select_all)
        self.copy_btn.clicked.connect(self.on_copy)
        self.move_btn.clicked.connect(self.on_move)
        self.delete_btn.clicked.connect(self.on_delete)

        # Add Aero glass style to message boxes
        self.setStyleSheet(self.styleSheet() + """
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 180),
                    stop:0.3 rgba(220, 240, 255, 140),
                    stop:0.6 rgba(200, 230, 255, 120),
                    stop:1 rgba(180, 220, 255, 100));
                border: 1px solid rgba(255, 255, 255, 180);
                border-radius: 3px;
            }
            QMessageBox QLabel {
                color: rgba(0, 0, 0, 180);
                background: transparent;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 180),
                    stop:0.3 rgba(220, 240, 255, 140),
                    stop:0.6 rgba(200, 230, 255, 120),
                    stop:1 rgba(180, 220, 255, 100));
                border: 1px solid rgba(255, 255, 255, 180);
                border-radius: 3px;
                padding: 6px;
                color: rgba(0, 0, 0, 180);
                font-weight: bold;
                min-height: 20px;
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 220),
                    stop:0.3 rgba(230, 245, 255, 180),
                    stop:0.6 rgba(210, 235, 255, 160),
                    stop:1 rgba(190, 225, 255, 140));
                border: 1px solid rgba(255, 255, 255, 220);
            }
            QMessageBox QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 220, 255, 100),
                    stop:0.3 rgba(200, 230, 255, 120),
                    stop:0.6 rgba(220, 240, 255, 140),
                    stop:1 rgba(255, 255, 255, 180));
                padding-top: 7px;
                padding-bottom: 5px;
            }
        """)

    def update_snowflakes(self):
        """Update snowflake positions and handle falling animation."""
        for snowflake in self.snowflakes:
            # Update position
            snowflake['y'] += snowflake['speed']
            snowflake['x'] += snowflake['sway'] * math.sin(snowflake['y'] * snowflake['sway_speed'])
            
            # Reset snowflake when it goes below the window
            if snowflake['y'] > self.height():
                snowflake['y'] = random.randint(-100, 0)
                snowflake['x'] = random.randint(0, self.width())
        
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Custom painting for futuristic glass and metal interface."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Futuristic base gradient with metallic tint
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(240, 245, 255, 220))  # Brighter top
        gradient.setColorAt(0.3, QColor(230, 240, 250, 200))
        gradient.setColorAt(0.6, QColor(220, 235, 250, 180))
        gradient.setColorAt(1, QColor(210, 230, 250, 160))
        painter.fillRect(self.rect(), gradient)
        
        # Metallic frame effect
        frame_gradient = QLinearGradient(0, 0, 0, self.height())
        frame_gradient.setColorAt(0, QColor(200, 220, 255, 100))
        frame_gradient.setColorAt(0.5, QColor(180, 200, 255, 80))
        frame_gradient.setColorAt(1, QColor(160, 180, 255, 60))
        painter.setPen(QPen(frame_gradient, 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        # Draw snowflakes
        painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
        for snowflake in self.snowflakes:
            # Draw a simple snowflake shape
            x, y = int(snowflake['x']), int(snowflake['y'])
            size = int(snowflake['size'])
            
            # Main snowflake body
            painter.drawLine(x, y - size, x, y + size)
            painter.drawLine(x - size, y, x + size, y)
            
            # Diagonal lines
            painter.drawLine(x - size//2, y - size//2, x + size//2, y + size//2)
            painter.drawLine(x - size//2, y + size//2, x + size//2, y - size//2)
            
            # Add some sparkle
            painter.drawPoint(x, y)
        
        # Enhanced top glass highlight with metallic tint
        highlight = QLinearGradient(0, 0, 0, 150)
        highlight.setColorAt(0, QColor(255, 255, 255, 100))  # Brighter highlight
        highlight.setColorAt(0.3, QColor(220, 240, 255, 80))
        highlight.setColorAt(0.6, QColor(200, 220, 255, 60))
        highlight.setColorAt(1, QColor(180, 200, 255, 0))
        painter.fillRect(QRectF(0, 0, self.width(), 150), highlight)
        
        # Futuristic bottom reflection with metallic effect
        bottom_reflection = QLinearGradient(0, self.height() - 100, 0, self.height())
        bottom_reflection.setColorAt(0, QColor(180, 200, 255, 0))
        bottom_reflection.setColorAt(0.7, QColor(160, 180, 255, 30))
        bottom_reflection.setColorAt(1, QColor(140, 160, 255, 50))
        painter.fillRect(QRectF(0, self.height() - 100, self.width(), 100), bottom_reflection)
        
        # Metallic corner accents
        corner_size = 30
        corner_gradient = QRadialGradient(corner_size, corner_size, corner_size, corner_size, corner_size)
        corner_gradient.setColorAt(0, QColor(200, 220, 255, 80))
        corner_gradient.setColorAt(0.5, QColor(180, 200, 255, 40))
        corner_gradient.setColorAt(1, QColor(160, 180, 255, 0))
        painter.setBrush(corner_gradient)
        painter.drawEllipse(0, 0, corner_size * 2, corner_size * 2)
        painter.drawEllipse(self.width() - corner_size * 2, 0, corner_size * 2, corner_size * 2)
        
        # Futuristic shine effects
        shine = QLinearGradient(0, 0, self.width(), 0)
        shine.setColorAt(0, QColor(255, 255, 255, 0))
        shine.setColorAt(0.3, QColor(220, 240, 255, 40))
        shine.setColorAt(0.7, QColor(200, 220, 255, 40))
        shine.setColorAt(1, QColor(180, 200, 255, 0))
        painter.fillRect(QRectF(0, 0, self.width(), 3), shine)
        
        # Vertical metallic accent
        v_shine = QLinearGradient(0, 0, 0, self.height())
        v_shine.setColorAt(0, QColor(200, 220, 255, 0))
        v_shine.setColorAt(0.3, QColor(180, 200, 255, 30))
        v_shine.setColorAt(0.7, QColor(160, 180, 255, 30))
        v_shine.setColorAt(1, QColor(140, 160, 255, 0))
        painter.fillRect(QRectF(0, 0, 3, self.height()), v_shine)
        
        # Futuristic bottom edge
        bottom_edge = QLinearGradient(0, self.height() - 3, 0, self.height())
        bottom_edge.setColorAt(0, QColor(180, 200, 255, 60))
        bottom_edge.setColorAt(1, QColor(160, 180, 255, 80))
        painter.fillRect(QRectF(0, self.height() - 3, self.width(), 3), bottom_edge)

    def load_index(self):
        """Load the index from the JSON file if it exists."""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.indexed_files = data.get('files', [])
                    self.indexed_directory = data.get('directory', None)
                    if self.indexed_directory:
                        self.dir_input.setText(self.indexed_directory)
                        self.status_label.setText(f"Loaded index: {len(self.indexed_files)} files")
        except Exception as e:
            print(f"Error loading index: {str(e)}")
            self.indexed_files = []
            self.indexed_directory = None

    def save_index(self):
        """Save the current index to the JSON file."""
        try:
            data = {
                'directory': self.indexed_directory,
                'files': self.indexed_files,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving index: {str(e)}")

    def on_search(self):
        try:
            self.results_list.clear()
            directory = self.dir_input.text()
            keyword = self.search_input.text()
            
            if not directory:
                QMessageBox.warning(self, "Search Error", "Please enter a directory path")
                return
                
            if not os.path.exists(directory):
                QMessageBox.warning(self, "Search Error", f"Directory '{directory}' does not exist")
                return
                
            if not os.access(directory, os.R_OK):
                QMessageBox.warning(self, "Search Error", f"No read permission for directory '{directory}'")
                return
            
            # Auto-index if directory changed
            if directory != self.indexed_directory:
                self.index_directory(directory)
                
            # Start animations
            self.search_btn.start_pulse()
            self.search_btn.setEnabled(False)
            self.search_btn.setText("Searching...")
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.progress_bar.start_wave()
            self.cancel_btn.setVisible(True)
            
            # Create and start search worker
            self.search_worker = SearchWorker(directory, keyword, self.indexed_files)
            self.search_worker.finished.connect(self.on_search_complete)
            self.search_worker.error.connect(self.on_search_error)
            self.search_worker.progress.connect(self.update_progress)
            self.search_worker.large_directory.connect(self.handle_large_directory)
            self.search_worker.start()
            
        except Exception as e:
            QMessageBox.warning(self, "Search Error", f"An error occurred during search: {str(e)}")
            import traceback
            print("Full error traceback:")
            print(traceback.format_exc())
            
    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
            
    def on_search_complete(self, results):
        # Stop the wave animation and hide progress bar immediately
        self.progress_bar.stop_wave()
        
        # Stop animations and reset UI
        self.search_btn.stop_pulse()
        self.search_btn.setEnabled(True)
        self.search_btn.setText("Search")
        self.cancel_btn.setVisible(False)
        
        # Clear and add results to list with animation
        self.results_list.clear()  # Clear any existing items
        for item in results:
            self.results_list.add_item_with_animation(item)

    def on_search_error(self, error_message):
        # Stop animations and reset UI
        self.search_btn.stop_pulse()
        self.search_btn.setEnabled(True)
        self.search_btn.setText("Search")
        self.progress_bar.stop_wave()  # This will also hide the progress bar
        self.cancel_btn.setVisible(False)
        
        # Show error message with more details
        QMessageBox.warning(self, "Search Error", error_message)
        print(f"Search error: {error_message}")  # Log to console for debugging
        
    def cancel_search(self):
        if hasattr(self, 'search_worker'):
            self.search_worker.stop()
            self.search_worker.wait()
            self.on_search_complete([])

    def on_index(self):
        """Reindex the current directory."""
        directory = self.dir_input.text()
        if directory and os.path.isdir(directory):
            self.index_directory(directory)
        else:
            QMessageBox.warning(self, "Error", "Please select a valid directory first")

    def on_browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose a directory")
        if directory:
            self.dir_input.setText(directory)
            # Auto-index the directory if it's different from the current one
            if directory != self.indexed_directory:
                self.index_directory(directory)

    def on_select(self, item):
        # Get the widget from the item
        widget = self.results_list.itemWidget(item)
        # Get the label from the widget's layout
        label = widget.findChild(QLabel)
        if label:
            file_path = label.text()
            open_file(file_path)

    def on_select_all(self):
        self.results_list.selectAll()  # Use the built-in selectAll method

    def get_selected_files(self):
        """Get the file paths of selected items."""
        selected_files = []
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if item.isSelected():
                widget = self.results_list.itemWidget(item)
                label = widget.findChild(QLabel)
                if label:
                    selected_files.append(label.text())
        return selected_files

    def on_copy(self):
        selected = self.get_selected_files()
        if selected:
            dest_dir = QFileDialog.getExistingDirectory(self, "Choose destination directory")
            if dest_dir:
                try:
                    for source in selected:
                        dest = os.path.join(dest_dir, os.path.basename(source))
                        if not os.path.exists(dest):
                            shutil.copy2(source, dest_dir)
                    QMessageBox.information(self, "Copy Complete", f"Files copied to {dest_dir}")
                except Exception as e:
                    QMessageBox.warning(self, "Copy Error", f"Error copying files: {str(e)}")

    def on_move(self):
        selected = self.get_selected_files()
        if selected:
            dest_dir = QFileDialog.getExistingDirectory(self, "Choose destination directory")
            if dest_dir:
                try:
                    for source in selected:
                        dest = os.path.join(dest_dir, os.path.basename(source))
                        if not os.path.exists(dest):
                            shutil.move(source, dest_dir)
                            if source in self.indexed_files:
                                self.indexed_files.remove(source)
                    self.save_index()  # Save the updated index
                    self.on_search()  # Refresh list
                    QMessageBox.information(self, "Move Complete", f"Files moved to {dest_dir}")
                except Exception as e:
                    QMessageBox.warning(self, "Move Error", f"Error moving files: {str(e)}")

    def on_delete(self):
        selected = self.get_selected_files()
        if selected and QMessageBox.question(self, "Confirm Delete", "Are you sure?") == QMessageBox.StandardButton.Yes:
            try:
                for file_path in selected:
                    os.remove(file_path)
                    if file_path in self.indexed_files:
                        self.indexed_files.remove(file_path)
                self.save_index()  # Save the updated index
                self.on_search()  # Refresh list
                QMessageBox.information(self, "Delete Complete", "Selected files deleted")
            except Exception as e:
                QMessageBox.warning(self, "Delete Error", f"Error deleting files: {str(e)}")

    def handle_large_directory(self, total_files):
        # Re-enable search button and hide progress
        self.search_btn.setEnabled(True)
        self.search_btn.setText("Search")
        self.progress_bar.hide()
        self.cancel_btn.setVisible(False)
        
        # Ask user if they want to index the directory
        reply = QMessageBox.question(
            self, 
            "Large Directory Detected",
            f"This directory contains {total_files} files. Would you like to index it first for better performance?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Index the directory
            self.index_directory(self.dir_input.text())
        else:
            # Continue with non-indexed search
            self.search_worker = SearchWorker(self.dir_input.text(), self.search_input.text())
            self.search_worker.finished.connect(self.on_search_complete)
            self.search_worker.error.connect(self.on_search_error)
            self.search_worker.progress.connect(self.update_progress)
            self.search_worker.large_directory.connect(self.handle_large_directory)
            self.search_worker.start()
            
    def index_directory(self, directory):
        """Index the directory and save to JSON file."""
        try:
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.progress_bar.start_wave()
            
            # Count total files first
            total_files = 0
            for _, _, files in os.walk(directory):
                total_files += len(files)
            
            # Index files with progress
            self.indexed_files = []
            processed_files = 0
            
            for root, _, files in os.walk(directory):
                for file in files:
                    self.indexed_files.append(os.path.join(root, file))
                    processed_files += 1
                    if processed_files % 100 == 0:
                        self.progress_bar.setValue(int(processed_files * 100 / total_files))
            
            self.indexed_directory = directory
            self.save_index()
            
            # Update status
            self.status_label.setText(f"Indexed {len(self.indexed_files)} files")
            self.progress_bar.stop_wave()
            self.progress_bar.hide()
            
        except Exception as e:
            QMessageBox.warning(self, "Indexing Error", f"An error occurred while indexing: {str(e)}")
            self.progress_bar.stop_wave()
            self.progress_bar.hide()

    def show_help(self):
        """Show help message with GitHub link."""
        help_text = """
        <h3>File Search Help</h3>
        <p>This application helps you search through your files with a beautiful frosted glass interface.</p>
        
        <h4>Features:</h4>
        <ul>
            <li>Search files by name or extension</li>
            <li>Auto-indexing for faster searches</li>
            <li>Copy, move, and delete files</li>
            <li>Beautiful frosted glass UI with snow animation</li>
        </ul>
        
        <h4>How to use:</h4>
        <ol>
            <li>Select a directory to search in</li>
            <li>Enter your search term</li>
            <li>Use the buttons to manage your files</li>
        </ol>
        
        <p>For more information, visit the project on GitHub:<br>
        <a href="https://github.com/m0nnnna/Filesearch">https://github.com/m0nnnna/Filesearch</a></p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Help")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 180),
                    stop:0.3 rgba(220, 240, 255, 140),
                    stop:0.6 rgba(200, 230, 255, 120),
                    stop:1 rgba(180, 220, 255, 100));
                border: 1px solid rgba(255, 255, 255, 180);
                border-radius: 3px;
            }
            QMessageBox QLabel {
                color: rgba(0, 0, 0, 180);
                background: transparent;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 180),
                    stop:0.3 rgba(220, 240, 255, 140),
                    stop:0.6 rgba(200, 230, 255, 120),
                    stop:1 rgba(180, 220, 255, 100));
                border: 1px solid rgba(255, 255, 255, 180);
                border-radius: 3px;
                padding: 6px;
                color: rgba(0, 0, 0, 180);
                font-weight: bold;
                min-height: 20px;
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 220),
                    stop:0.3 rgba(230, 245, 255, 180),
                    stop:0.6 rgba(210, 235, 255, 160),
                    stop:1 rgba(190, 225, 255, 140));
                border: 1px solid rgba(255, 255, 255, 220);
            }
        """)
        msg.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FileSearchWindow()
    window.show()
    sys.exit(app.exec())