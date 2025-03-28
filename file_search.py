import os
import re
import sys
import shutil
import json
import subprocess
import platform
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QFileDialog, 
                             QMessageBox, QGraphicsBlurEffect, QGraphicsOpacityEffect)
from PyQt6.QtGui import (QPainter, QLinearGradient, QColor, QBrush, QFont, QPalette, QPen, QPixmap, QRadialGradient)
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup, QPoint, QTimer

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

def open_file_explorer(file_path):
    if platform.system() == 'Windows':
        subprocess.run(['explorer', '/select,', file_path])
    elif platform.system() == 'Darwin':
        subprocess.run(['open', '-R', file_path])
    elif platform.system() == 'Linux':
        subprocess.run(['xdg-open', os.path.dirname(file_path)])
        subprocess.run(['nautilus', '--select', file_path])

def open_file(file_path):
    if platform.system() == 'Windows':
        os.startfile(file_path)
    elif platform.system() == 'Darwin':
        subprocess.run(['open', file_path])
    elif platform.system() == 'Linux':
        subprocess.run(['xdg-open', file_path])

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

class AnimatedListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.animation_duration = 150
        self.animations = []
        
    def add_item_with_animation(self, text):
        # Create a simple item without custom widget
        item = QListWidgetItem(text)
        self.addItem(item)
        
        # Create opacity effect for the item
        effect = QGraphicsOpacityEffect(self)
        item.setData(Qt.ItemDataRole.UserRole, effect)
        effect.setOpacity(0.0)
        
        # Create and configure the animation
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(self.animation_duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Keep reference to prevent garbage collection
        self.animations.append((animation, item))
        
        def cleanup():
            if (animation, item) in self.animations:
                self.animations.remove((animation, item))
        
        animation.finished.connect(cleanup)
        animation.start()

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

class FileSearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Search - Aero Glass")
        self.setGeometry(100, 100, 600, 600)
        self.setWindowOpacity(0.98)
        
        # Background widget with frosted glass texture
        self.background_widget = QWidget(self)
        self.background_widget.setGeometry(0, 0, 600, 600)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(10)
        self.background_widget.setGraphicsEffect(blur)
        self.background_widget.setAutoFillBackground(True)
        palette = self.background_widget.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(QColor(230, 240, 250, 160)))
        self.background_widget.setPalette(palette)
        
        # Main widget and layout (foreground)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Styling: Aero glass theme
        self.setStyleSheet("""
            QMainWindow { background: transparent; }
            QWidget { 
                background: transparent; 
                color: rgba(0, 0, 0, 180); 
                font-family: Segoe UI; 
                font-size: 12px; 
            }
            QLineEdit { 
                background: rgba(255, 255, 255, 140); 
                border: 1px solid rgba(255, 255, 255, 180); 
                border-radius: 3px; 
                padding: 5px; 
                color: rgba(0, 0, 0, 180); 
            }
            QListWidget { 
                background: rgba(255, 255, 255, 120); 
                border: 1px solid rgba(255, 255, 255, 180); 
                border-radius: 3px; 
                color: rgba(0, 0, 0, 180); 
            }
            QListWidget::item:hover { 
                background: rgba(220, 240, 255, 140); 
            }
            QLabel { 
                color: rgba(0, 0, 0, 180);
                font-weight: bold;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 40);
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(200, 220, 255, 180),
                    stop:0.5 rgba(180, 200, 255, 160),
                    stop:1 rgba(160, 180, 255, 180));
                min-height: 20px;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 180);
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(220, 235, 255, 200),
                    stop:0.5 rgba(200, 220, 255, 180),
                    stop:1 rgba(180, 200, 255, 200));
            }
            QScrollBar::handle:vertical:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(180, 200, 255, 160),
                    stop:0.5 rgba(160, 180, 255, 140),
                    stop:1 rgba(140, 160, 255, 160));
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: rgba(255, 255, 255, 40);
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 220, 255, 180),
                    stop:0.5 rgba(180, 200, 255, 160),
                    stop:1 rgba(160, 180, 255, 180));
                min-width: 20px;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 180);
            }
            QScrollBar::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(220, 235, 255, 200),
                    stop:0.5 rgba(200, 220, 255, 180),
                    stop:1 rgba(180, 200, 255, 200));
            }
            QScrollBar::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(180, 200, 255, 160),
                    stop:0.5 rgba(160, 180, 255, 140),
                    stop:1 rgba(140, 160, 255, 160));
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
        # Data
        self.indexed_files = []
        self.indexed_directory = None
        self.saved_indexes = {}
        self.load_saved_indexes()
        
        # Directory Row
        dir_row = QHBoxLayout()
        self.dir_label = QLabel("Directory Path:")
        self.dir_input = QLineEdit()
        self.browse_btn = AeroButton("Browse")
        self.index_btn = AeroButton("Index")
        self.save_btn = AeroButton("Save Index")
        self.load_btn = AeroButton("Load Index")
        dir_row.addWidget(self.dir_label)
        dir_row.addWidget(self.dir_input)
        dir_row.addWidget(self.browse_btn)
        dir_row.addWidget(self.index_btn)
        dir_row.addWidget(self.save_btn)
        dir_row.addWidget(self.load_btn)
        self.layout.addLayout(dir_row)
        
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
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.on_search)
        self.search_btn = AeroButton("Search")
        search_row.addWidget(self.search_label)
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_btn)
        self.layout.addLayout(search_row)
        
        # Results List
        self.results_list = AnimatedListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_select)
        self.results_list.setStyleSheet("""
            QListWidget {
                background: rgba(255, 255, 255, 120);
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
        self.save_btn.clicked.connect(self.on_save_index)
        self.load_btn.clicked.connect(self.on_load_index)
        self.search_btn.clicked.connect(self.on_search)
        self.select_all_btn.clicked.connect(self.on_select_all)
        self.copy_btn.clicked.connect(self.on_copy)
        self.move_btn.clicked.connect(self.on_move)
        self.delete_btn.clicked.connect(self.on_delete)

    def paintEvent(self, event):
        """Custom painting for Aero glass background."""
        painter = QPainter(self)
        # Base gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(240, 245, 255, 180))
        gradient.setColorAt(1, QColor(220, 235, 250, 160))
        painter.fillRect(self.rect(), gradient)
        
        # Subtle pattern
        painter.setPen(QPen(QColor(255, 255, 255, 15), 1))
        size = 40
        for i in range(0, self.width(), size):
            for j in range(0, self.height(), size):
                if (i + j) % (size * 2) == 0:
                    painter.drawEllipse(i, j, size, size)
        
        # Top glass highlight
        highlight = QLinearGradient(0, 0, 0, 120)
        highlight.setColorAt(0, QColor(255, 255, 255, 60))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillRect(QRectF(0, 0, self.width(), 120), highlight)
        
        # Subtle border
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def load_saved_indexes(self):
        try:
            with open('file_indexes.json', 'r') as f:
                self.saved_indexes = json.load(f)
        except FileNotFoundError:
            self.saved_indexes = {}

    def save_indexes_to_file(self):
        with open('file_indexes.json', 'w') as f:
            json.dump(self.saved_indexes, f)

    def on_search(self):
        try:
            self.results_list.clear()
            directory = self.dir_input.text()
            keyword = self.search_input.text()
            if directory:
                files_to_search = self.indexed_files if self.indexed_files else None
                results = search_files(directory, keyword, files_to_search)
                for item in results:
                    self.results_list.add_item_with_animation(item)
        except Exception as e:
            QMessageBox.warning(self, "Search Error", f"An error occurred during search: {str(e)}")

    def on_index(self):
        try:
            directory = self.dir_input.text()
            if directory and os.path.isdir(directory):
                self.indexed_files = []
                for root, _, files in os.walk(directory):
                    for file in files:
                        self.indexed_files.append(os.path.join(root, file))
                self.indexed_directory = directory
                
                # Update status label without animation
                status_text = f"Current index: {len(self.indexed_files)} files from {directory}"
                self.status_label.setText(status_text)
                
                QMessageBox.information(self, "Indexing Complete", f"Indexed {len(self.indexed_files)} files")
        except Exception as e:
            QMessageBox.warning(self, "Indexing Error", f"An error occurred while indexing: {str(e)}")

    def on_save_index(self):
        if not self.indexed_files or not self.indexed_directory:
            QMessageBox.warning(self, "Error", "Please create an index first")
            return
        name, ok = QFileDialog.getSaveFileName(self, "Save Index", "", "Index Name")
        if ok and name:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.saved_indexes[name] = {
                'directory': self.indexed_directory,
                'files': self.indexed_files,
                'timestamp': timestamp
            }
            self.save_indexes_to_file()
            QMessageBox.information(self, "Save Complete", f"Index '{name}' saved")

    def on_load_index(self):
        if not self.saved_indexes:
            QMessageBox.warning(self, "Error", "No saved indexes available")
            return
        items = [f"{name} ({data['timestamp']}) - {data['directory']}" 
                 for name, data in self.saved_indexes.items()]
        item, ok = QComboBox(self).showPopup() or (items[0], True)  # Simplified for example
        if ok:
            index_name = item.split(' (')[0]
            self.indexed_files = self.saved_indexes[index_name]['files']
            self.indexed_directory = self.saved_indexes[index_name]['directory']
            self.dir_input.setText(self.indexed_directory)
            self.status_label.animate_text_change(
                f"Loaded index '{index_name}': {len(self.indexed_files)} files"
            )
            QMessageBox.information(self, "Load Complete", f"Loaded index '{index_name}' with {len(self.indexed_files)} files")

    def on_browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose a directory")
        if directory:
            self.dir_input.setText(directory)

    def on_select(self, item):
        file_path = item.text()
        open_file(file_path)
        open_file_explorer(file_path)

    def on_select_all(self):
        for i in range(self.results_list.count()):
            self.results_list.item(i).setSelected(True)

    def on_copy(self):
        selected = [self.results_list.item(i).text() for i in range(self.results_list.count()) if self.results_list.item(i).isSelected()]
        if selected:
            dest_dir = QFileDialog.getExistingDirectory(self, "Choose destination directory")
            if dest_dir:
                for source in selected:
                    dest = os.path.join(dest_dir, os.path.basename(source))
                    if not os.path.exists(dest):
                        shutil.copy2(source, dest_dir)
                QMessageBox.information(self, "Copy Complete", f"Files copied to {dest_dir}")

    def on_move(self):
        selected = [self.results_list.item(i).text() for i in range(self.results_list.count()) if self.results_list.item(i).isSelected()]
        if selected:
            dest_dir = QFileDialog.getExistingDirectory(self, "Choose destination directory")
            if dest_dir:
                for source in selected:
                    dest = os.path.join(dest_dir, os.path.basename(source))
                    if not os.path.exists(dest):
                        shutil.move(source, dest_dir)
                        if source in self.indexed_files:
                            self.indexed_files[self.indexed_files.index(source)] = dest
                self.on_search()  # Refresh list
                QMessageBox.information(self, "Move Complete", f"Files moved to {dest_dir}")

    def on_delete(self):
        selected = [self.results_list.item(i).text() for i in range(self.results_list.count()) if self.results_list.item(i).isSelected()]
        if selected and QMessageBox.question(self, "Confirm Delete", "Are you sure?") == QMessageBox.StandardButton.Yes:
            for file_path in selected:
                try:
                    os.remove(file_path)
                    if file_path in self.indexed_files:
                        self.indexed_files.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            self.on_search()  # Refresh list
            QMessageBox.information(self, "Delete Complete", "Selected files deleted")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FileSearchWindow()
    window.show()
    sys.exit(app.exec())