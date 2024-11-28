import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QPixmap, QPen
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint

class CustomClockWindow(QMainWindow):
    def __init__(self, scale_factor=1.0, countdown_seconds=60):  # Adjusted default scale factor
        super().__init__()
        self.setWindowTitle("Dynamic Clock App")
        
        # Load the clock-shaped image with more precise scaling
        original_pixmap = QPixmap("images/clock.png")  # Your hollowed clock image
        
        # Calculate new dimensions with more control
        new_width = int(original_pixmap.width() * scale_factor)
        new_height = int(original_pixmap.height() * scale_factor)
        
        self.clock_shape = original_pixmap.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Set the size of the window based on the scaled image
        self.setFixedSize(self.clock_shape.size())

        # Remove the default window frame
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMask(self.clock_shape.mask())

        # Store the original position for vibration
        self.original_position = self.pos()


        # Timer for countdown
        self.countdown_time = QTime(0, countdown_seconds // 60, countdown_seconds % 60)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second

        self.minute_hand_image = QPixmap("images/hour_hand.png").scaled(
            int(original_pixmap.width() * scale_factor * 0.30),
            int(original_pixmap.height() * scale_factor * 0.30),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
    
        self.second_hand_image = QPixmap("images/minute_hand.png").scaled(
            int(original_pixmap.width() * scale_factor * 0.20),
            int(original_pixmap.height() * scale_factor * 0.20),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Vibration parameters
        self.vibration_offset = [QPoint(-5, 0), QPoint(5, 0), QPoint(0, -5), QPoint(0, 5)]
        self.vibration_index = 0
        self.vibration_timer = QTimer(self)  # Separate timer for vibration
        self.vibration_timer.timeout.connect(self.vibrate)

        

    def paintEvent(self, event):
        # Draw the static clock shape
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.clock_shape)
        
        # Draw dynamic clock face
        self.draw_dynamic_clock(painter)

    def draw_dynamic_clock(self, painter):
        center_x = (self.width() // 2) 
        center_y = (self.height() // 2) - 40
    
        # Draw countdown time
        painter.setPen(QPen(Qt.black, 3))
        painter.setFont(self.font())
        time_str = self.countdown_time.toString("mm:ss")
        painter.drawText(self.rect(), Qt.AlignCenter, time_str)

        # Calculate angles
        seconds = self.countdown_time.minute() * 60 + self.countdown_time.second()
        minute_angle = (360 * seconds) / 3600
        second_angle = (360 * (seconds % 60)) / 60

        # Draw minute hand image
        painter.save()
        painter.translate(center_x, center_y)
        painter.translate(0, self.minute_hand_image.height() // 2)
        painter.rotate(minute_angle)
        # Translate back by the full height of the image to rotate from the tail
        painter.drawPixmap(
            -self.minute_hand_image.width() // 2, 
            -self.minute_hand_image.height(), 
            self.minute_hand_image
        )
        painter.restore()

        # Draw second hand image
        painter.save()
        painter.translate(center_x, center_y - 5)
        # Translate back by the full height of the image to rotate from the tail
        painter.translate(0, self.second_hand_image.height() // 2)
        painter.rotate(second_angle)
        painter.drawPixmap(
            -self.second_hand_image.width() // 2, 
            -self.second_hand_image.height(), 
            self.second_hand_image
        )
        painter.restore()

    def update_clock(self):
        """Update the countdown timer and refresh the display."""
        self.countdown_time = self.countdown_time.addSecs(-1)  # Subtract 1 second
        if self.countdown_time == QTime(0, 0, 30):
            self.vibration_timer.start(100)  # Start vibration
        if self.countdown_time == QTime(0, 0, 0):
            self.vibration_timer.stop()  # Stop vibration
            self.timer.stop()  # Stop the countdown at zero
        self.update()  # Redraw the window

    def vibrate(self):
        """Move the window in a vibrating pattern."""
        offset = self.vibration_offset[self.vibration_index]
        self.move(self.original_position + offset)
        self.vibration_index = (self.vibration_index + 1) % len(self.vibration_offset)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Suggested scaling options
    # Uncomment and adjust the scale_factor as needed
    clock_app = CustomClockWindow(scale_factor=0.15, countdown_seconds=60)
    # Alternative: clock_app = CustomClockWindow(scale_factor=0.25, countdown_seconds=60)
    # Alternative: clock_app = CustomClockWindow(scale_factor=0.5, countdown_seconds=60)
    
    clock_app.show()
    
    sys.exit(app.exec_())