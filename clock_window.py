import sys
import os
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt5.QtGui import QPainter, QPixmap, QPen, QFont
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint, QRunnable, QThreadPool, pyqtSignal, QObject


SECONDS = 30
TURN_ON = False

class SoundWorker(QRunnable):
    def __init__(self, sound_path, start_time=0, loop=False):
        super().__init__()
        self.sound_path = sound_path
        self.start_time = start_time
        self.loop = loop

    def run(self):
        sound = pygame.mixer.Sound(self.sound_path)
        if self.loop:
            sound.play(-1)
        else:
            pygame.mixer.music.load(self.sound_path)
            pygame.mixer.music.play(start=self.start_time)

class ClockSignals(QObject):
    countdown_updated = pyqtSignal(QTime)
    countdown_finished = pyqtSignal()

class RedButton(QMainWindow):
    def __init__(self):
        super().__init__()

class CustomClockWindow(QMainWindow):
    def __init__(self, scale_factor=1.0, countdown_seconds=60):
        super().__init__()
        pygame.mixer.init()
        self.threadpool = QThreadPool()
        self.signals = ClockSignals()
        
        self.setWindowTitle("Dynamic Clock App")
        
        # Image loading with scaled dimensions
        original_pixmap = QPixmap("images/clock.png")
        new_width = int(original_pixmap.width() * scale_factor)
        new_height = int(original_pixmap.height() * scale_factor)
        
        self.clock_shape = original_pixmap.scaled(
            new_width, new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Window configuration
        self.setFixedSize(self.clock_shape.size())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMask(self.clock_shape.mask())

        # Position tracking for vibration
        self.original_position = self.pos()

        # Countdown and timer state
        self.not_alarm = self.not_countdown = True
        self.countdown_time = QTime(0, countdown_seconds // 60, countdown_seconds % 60)
        
        # Hand images
        self.minute_hand_image = QPixmap("images/hour_hand.png").scaled(
            int(original_pixmap.width() * scale_factor * 0.20),
            int(original_pixmap.height() * scale_factor * 0.20),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
    
        self.second_hand_image = QPixmap("images/minute_hand.png").scaled(
            int(original_pixmap.width() * scale_factor * 0.35),
            int(original_pixmap.height() * scale_factor * 0.35),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Vibration configuration
        self.vibration_offset = [QPoint(-5, 0), QPoint(5, 0), QPoint(0, -5), QPoint(0, 5)]
        self.vibration_index = 0
        self.vibration_timer = QTimer(self)
        self.vibration_timer.timeout.connect(self.vibrate)

        # Main timer with lower resolution
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(500)  # Update every half-second

        # Background sound
        self.start_background_sound('ticking-clock-sound.mp3', loop=True)

    def start_background_sound(self, sound_path, start_time=0, loop=False):
        worker = SoundWorker(os.path.join('sounds', sound_path), start_time, loop)
        self.threadpool.start(worker)

    def update_clock(self):
        self.countdown_time = self.countdown_time.addSecs(-1)
        
        if self.countdown_time <= QTime(0, 0, 25) and self.not_countdown:
            self.vibration_timer.start(100)
            self.not_countdown = False
            start_time = 25 - self.countdown_time.second()
            self.start_background_sound('countdown.mp3', start_time=start_time)
            
            if self.not_alarm:
                self.start_background_sound('alarm.mp3', loop=True)
                self.not_alarm = False
        if self.countdown_time == QTime(0, 0, 3):
            self.start_background_sound('bomb-beeps.mp3')
            self.start_background_sound('explode.mp3')
        
        if self.countdown_time == QTime(0, 0, 0):
            self.vibration_timer.stop()
            #os.system("shutdown /s /t 1")
            self.timer.stop()
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.clock_shape)
        self.draw_dynamic_clock(painter)

    def draw_dynamic_clock(self, painter):
        center_x = (self.width() // 2)
        center_y = (self.height() // 2) - 8

        seconds = self.countdown_time.minute() * 60 + self.countdown_time.second()
        minute_angle = (360 * seconds) / 3600
        second_angle = (360 * (seconds % 60)) / 60

        # Draw minute hand
        painter.save()
        painter.translate(center_x, center_y - 15)
        painter.translate(0, self.minute_hand_image.height() // 2)
        painter.rotate(minute_angle)
        painter.drawPixmap(
            -self.minute_hand_image.width() // 2, 
            -self.minute_hand_image.height(), 
            self.minute_hand_image
        )
        painter.restore()

        # Draw second hand
        painter.save()
        painter.translate(center_x, center_y - 22)
        painter.translate(0, self.second_hand_image.height() // 2 - 22)
        painter.rotate(second_angle)
        painter.drawPixmap(
            -self.second_hand_image.width() // 2, 
            -self.second_hand_image.height(), 
            self.second_hand_image
        )
        painter.restore()      
        

    def vibrate(self):
        offset = self.vibration_offset[self.vibration_index]
        self.move(self.original_position + offset)
        self.vibration_index = (self.vibration_index + 1) % len(self.vibration_offset)

def main():
    app = QApplication(sys.argv)
    clock_app = CustomClockWindow(scale_factor=0.15, countdown_seconds=SECONDS)
    clock_app.show()
    sys.exit(app.exec_())


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
            global SECONDS, TURN_ON
            SECONDS = max(self.calculate_seconds(), 10)
            TURN_ON = True
            self.close()
            

    def calculate_seconds(self):
        """Prompt the user for input and calculate total seconds."""
        try:
            hours, ok1 = QInputDialog.getInt(self, "Input", "Enter Hours (default 0):", 0, 0)
            if not ok1:
                print(hours, ok1)
                return
            minutes, ok2 = QInputDialog.getInt(self, "Input", "Enter Minutes (default 0):", 0, 0)
            if not ok2:
                return
            seconds, ok3 = QInputDialog.getInt(self, "Input", "Enter Seconds (default 0):", 0, 0)
            if not ok3:
                return
            total_seconds = hours * 3600 + minutes * 60 + seconds
            print(f"Total seconds: {total_seconds}")
            return total_seconds
        except ValueError:
            print("Invalid input. Please enter valid integers.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    red_button_app = RedButtonWindow(scale_factor=0.15)  # Adjust scale factor as needed
    red_button_app.show()
    app.exec_()
    if TURN_ON:
        main()