import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import Qt, QTimer, QPoint

class CustomClockWindow(QMainWindow):
    def __init__(self, scale_factor=0.5):  # Scale factor to resize the window
        super().__init__()
        self.setWindowTitle("Clock-Shaped App")
        
        # Load the clock-shaped image
        original_pixmap = QPixmap("clock.png")  # Your clock image
        
        # Debug: Check the original image size
        print(f"Original image size: {original_pixmap.width()}x{original_pixmap.height()}")
        
        # Scale the image (convert dimensions to integers)
        new_width = int(original_pixmap.width() * scale_factor)
        new_height = int(original_pixmap.height() * scale_factor)
        
        # Ensure scaling is happening
        print(f"Scaled image size: {new_width}x{new_height}")
        
        self.clock_shape = original_pixmap.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,  # Maintain aspect ratio
            Qt.SmoothTransformation  # Smooth scaling
        )
        
        # Set the size of the window based on the scaled image
        self.setFixedSize(self.clock_shape.size())
        print(f"Window size set to: {self.width()}x{self.height()}")  # Debug output

        # Remove the default window frame
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setMask(self.clock_shape.mask())

        # Original position of the window
        self.original_position = self.pos()

        # Timer for vibration effect
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.vibrate)

        # Vibration parameters
        self.vibration_offset = [QPoint(-5, 0), QPoint(5, 0), QPoint(0, -5), QPoint(0, 5)]
        self.vibration_index = 0

    def paintEvent(self, event):
        # Paint the custom shape
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.clock_shape)
        
    def start_vibrating(self):
        """Start the vibration effect."""
        self.original_position = self.pos()
        self.timer.start(50)  # Vibrate every 50 milliseconds

    def stop_vibrating(self):
        """Stop the vibration effect."""
        self.timer.stop()
        self.move(self.original_position)  # Reset to the original position

    def vibrate(self):
        """Move the window in a vibrating pattern."""
        offset = self.vibration_offset[self.vibration_index]
        self.move(self.original_position + offset)
        self.vibration_index = (self.vibration_index + 1) % len(self.vibration_offset)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Try a very small scale factor
    clock_app = CustomClockWindow(scale_factor=0.1)
    clock_app.show()
    
    # Start vibrating for demonstration
    clock_app.start_vibrating()
    
    # Stop vibrating after 5 seconds
    QTimer.singleShot(5000, clock_app.stop_vibrating)
    
    sys.exit(app.exec_())
