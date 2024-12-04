import sys
import os
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt5.QtGui import QPainter, QPixmap, QPen, QFont
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint, QRunnable, QThreadPool, pyqtSignal, QObject

# Global variables for countdown settings
SECONDS = 30
TURN_ON = False

class SoundWorker(QRunnable):
    """
    A worker class for playing sound asynchronously using pygame.
    """
    def __init__(self, sound_path, start_time=0, loop=False):
        super().__init__()
        self.sound_path = sound_path
        self.start_time = start_time
        self.loop = loop

    def run(self):
        # Load and play sound at the specified path
        sound = pygame.mixer.Sound(self.sound_path)
        if self.loop:
            sound.play(-1)  # Loop indefinitely
        else:
            pygame.mixer.music.load(self.sound_path)
            pygame.mixer.music.play(start=self.start_time)

class ClockSignals(QObject):
    """
    Custom signals for communication regarding clock countdown state.
    """
    countdown_updated = pyqtSignal(QTime)  # Signal to update countdown time
    countdown_finished = pyqtSignal()      # Signal when countdown finishes

class RedButton(QMainWindow):
    """
    A simple QMainWindow subclass for future functionalities.
    """
    def __init__(self):
        super().__init__()

class CustomClockWindow(QMainWindow):
    """
    Main window for a customizable clock application with countdown and vibration effects.
    """
    def __init__(self, scale_factor=1.0, countdown_seconds=60):
        super().__init__()
        pygame.mixer.init()  # Initialize pygame mixer for sound functionalities
        self.threadpool = QThreadPool()  # Thread pool for handling background tasks
        self.signals = ClockSignals()  # Create clock-related signals
        
        self.setWindowTitle("Dynamic Clock App")  # Set window title
        
        # Load and scale clock image based on scale factor
        original_pixmap = QPixmap("images/clock.png")
        new_width = int(original_pixmap.width() * scale_factor)
        new_height = int(original_pixmap.height() * scale_factor)
        self.clock_shape = original_pixmap.scaled(
            new_width, new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Configure the window appearance and shape
        self.setFixedSize(self.clock_shape.size())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMask(self.clock_shape.mask())

        # Original position for vibration reference
        self.original_position = self.pos()

        # Countdown and timer state initialization
        self.not_alarm = self.not_countdown = True
        self.countdown_time = QTime(0, countdown_seconds // 60, countdown_seconds % 60)
        
        # Load and scale hand images for the clock
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

        # Configure vibration effects
        self.vibration_offset = [QPoint(-5, 0), QPoint(5, 0), QPoint(0, -5), QPoint(0, 5)]
        self.vibration_index = 0
        self.vibration_timer = QTimer(self)
        # Connect vibration timer to vibrate method
        self.vibration_timer.timeout.connect(self.vibrate)

        # Main timer for clock updates
        self.timer = QTimer(self)
        # Connect timer to update the clock
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(500)  # Update every half-second

        # Start background ticking sound
        self.start_background_sound('ticking-clock-sound.mp3', loop=True)

    def start_background_sound(self, sound_path, start_time=0, loop=False):
        """
        Play a background sound asynchronously.
        """
        # Create and start a sound worker
        worker = SoundWorker(os.path.join('sounds', sound_path), start_time, loop)
        self.threadpool.start(worker)

    def update_clock(self):
        """
        Update clock state, countdown, and play sounds for key intervals.
        """
        # Decrement the countdown time by one second
        self.countdown_time = self.countdown_time.addSecs(-1)
        
        # Check for countdown nearing end and play respective sound effects
        if self.countdown_time <= QTime(0, 0, 25) and self.not_countdown:
            self.vibration_timer.start(100)  # Start vibration effect
            self.not_countdown = False
            # Calculate and start countdown sound
            start_time = 25 - self.countdown_time.second()
            self.start_background_sound('countdown.mp3', start_time=start_time)
            
            if self.not_alarm:
                # Play alarm sound as a loop
                self.start_background_sound('alarm.mp3', loop=True)
                self.not_alarm = False
        if self.countdown_time == QTime(0, 0, 3):
            # Play bomb beeps and explosion sounds
            self.start_background_sound('bomb-beeps.mp3')
            self.start_background_sound('explode.mp3')
        
        if self.countdown_time == QTime(0, 0, 0):
            self.vibration_timer.stop()  # Stop vibration
            # Trigger system shutdown (commented for safety)
            #os.system("shutdown /s /t 1")
            self.timer.stop()  # Stop all updates
        
        self.update()  # Update the paint event

    def paintEvent(self, event):
        """
        Redraw the clock image and clock hands at each paint event.
        """
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.clock_shape)
        self.draw_dynamic_clock(painter)

    def draw_dynamic_clock(self, painter):
        """
        Draw and rotate clock hands according to countdown time.
        """
        center_x = (self.width() // 2)
        center_y = (self.height() // 2) - 8

        # Calculate angles for hand rotations
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
        """
        Simulate a vibration effect by changing window position.
        """
        offset = self.vibration_offset[self.vibration_index]
        self.move(self.original_position + offset)
        self.vibration_index = (self.vibration_index + 1) % len(self.vibration_offset)

def main():
    """
    Main function to start the clock application with specified settings.
    """
    app = QApplication(sys.argv)
    # Initialize and show the clock app window
    clock_app = CustomClockWindow(scale_factor=0.15, countdown_seconds=SECONDS)
    clock_app.show()
    sys.exit(app.exec_())

class RedButtonWindow(QMainWindow):
    """
    A window displaying a red button that allows users to set a countdown timer.
    """
    def __init__(self, scale_factor=1.0):
        super().__init__()
        self.setWindowTitle("Red Button App")
        
        # Load the red button image
        self.image_path = os.path.join("images", "red-button.png")  # Ensure path is correct
        if not os.path.exists(self.image_path):
            print(f"Error: Image not found at {self.image_path}")
            sys.exit(1)
        
        original_pixmap = QPixmap(self.image_path)
        
        # Scale the image according to the given factor
        new_width = int(original_pixmap.width() * scale_factor)
        new_height = int(original_pixmap.height() * scale_factor)
        self.red_button = original_pixmap.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Configure the window size and shape
        self.setFixedSize(self.red_button.size())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMask(self.red_button.mask())

    def paintEvent(self, event):
        """
        Draw the red button as the window background.
        """
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.red_button)

    def mousePressEvent(self, event):
        """
        Handle mouse click event to start countdown.
        """
        if event.button() == Qt.LeftButton:
            global SECONDS, TURN_ON
            SECONDS = max(self.calculate_seconds(), 10)  # Prevent very short countdowns
            TURN_ON = True
            self.close()

    def calculate_seconds(self):
        """
        Prompt the user to input hours, minutes, and seconds, then calculate total seconds.
        """
        try:
            hours, ok1 = QInputDialog.getInt(self, "Input", "Enter Hours (default 0):", 0, 0)
            if not ok1:
                print(hours, ok1)  # For debugging purposes
                return
            minutes, ok2 = QInputDialog.getInt(self, "Input", "Enter Minutes (default 0):", 0, 0)
            if not ok2:
                return
            seconds, ok3 = QInputDialog.getInt(self, "Input", "Enter Seconds (default 0):", 0, 0)
            if not ok3:
                return
            total_seconds = hours * 3600 + minutes * 60 + seconds
            print(f"Total seconds: {total_seconds}")  # Output the calculated result for confirmation
            return total_seconds
        except ValueError:
            print("Invalid input. Please enter valid integers.")  # Handle invalid input

if __name__ == "__main__":
    """
    Entry point for the application. Displays a RedButtonWindow to set countdown time, then launches main.
    """
    app = QApplication(sys.argv)
    # Show the red button window first
    red_button_app = RedButtonWindow(scale_factor=0.15)  # Adjust scale factor as needed
    red_button_app.show()
    app.exec_()
    if TURN_ON:
        main()