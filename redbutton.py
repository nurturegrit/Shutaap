from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt
import os
import sys

class RedButtonWindow(QMainWindow):
    def __init__(self, scale_factor=1.0):
        super().__init__()
        self.setWindowTitle("Red Button App")
        
        # Load the red button image
        self.image_path = os.path.join("images", "red-button.png")  # Adjust the path as needed
        if not os.path.exists(self.image_path):
            print(f"Error: Image not found at {self.image_path}")
            sys.exit(1)
        
        original_pixmap = QPixmap(self.image_path)
        
        # Scale the image
        new_width = int(original_pixmap.width() * scale_factor)
        new_height = int(original_pixmap.height() * scale_factor)
        self.red_button = original_pixmap.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Set the window size to match the scaled image
        self.setFixedSize(self.red_button.size())

        # Remove the window frame
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Apply the button shape as the window mask
        self.setMask(self.red_button.mask())

    def paintEvent(self, event):
        """Paint the red button image as the background."""
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.red_button)

    def mousePressEvent(self, event):
        """Handle mouse click events."""
        if event.button() == Qt.LeftButton:
            self.calculate_seconds()

    def calculate_seconds(self):
        """Prompt the user for input and calculate total seconds."""
        try:
            hours, ok1 = QInputDialog.getInt(self, "Input", "Enter Hours (default 0):", 0, 0)
            if not ok1:
                return
            minutes, ok2 = QInputDialog.getInt(self, "Input", "Enter Minutes (default 0):", 0, 0)
            if not ok2:
                return
            seconds, ok3 = QInputDialog.getInt(self, "Input", "Enter Seconds (default 0):", 0, 0)
            if not ok3:
                return
            total_seconds = hours * 3600 + minutes * 60 + seconds
            print(f"Total seconds: {total_seconds}")
        except ValueError:
            print("Invalid input. Please enter valid integers.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    red_button_app = RedButtonWindow(scale_factor=0.15)  # Adjust scale factor as needed
    red_button_app.show()
    sys.exit(app.exec_())
