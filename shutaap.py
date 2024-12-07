import sys, json
import pygame
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, 
    QMessageBox, QApplication, QMainWindow, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap, QColor, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint, QRunnable, QThreadPool, pyqtSignal, QObject

COUNTDOWN = 0
CONFIGURATION = 10

import platform
import os

import subprocess

def resource_path(relative_path):
    """
    Get the absolute path to a resource.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def shutdown_system(action='shutdown'):
    """
    Perform system action based on user selection, cross-platform compatible.
    
    Args:
        action (str): Desired system action ('shutdown', 'restart', 'sleep').
    """
    try:
        if action is None:
            return
        system = platform.system()
        if system == "Windows":
            action_map = {
                'shutdown': ['shutdown', '/s', '/t', '1'],
                'restart': ['shutdown', '/r', '/t', '1'],
                'sleep': ['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0']
            }
        elif system == "Linux":
            action_map = {
                'shutdown': ['shutdown', '-h', 'now'],
                'restart': ['shutdown', '-r', 'now'],
                'sleep': ['systemctl', 'suspend']
            }
        elif system == "Darwin":  # macOS
            action_map = {
                'shutdown': ['shutdown', '-h', 'now'],
                'restart': ['shutdown', '-r', 'now'],
                'sleep': ['pmset', 'sleepnow']
            }
        else:
            raise OSError(f"Unsupported OS: {system}")
        
        subprocess.run(action_map.get(action, action_map['shutdown']), check=True)
    except Exception as e:
        print(f"Error: {e}")

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

class ShutdownTimerApp(QMainWindow):
    def __init__(self, scale_factor=1.0):
        super().__init__()
        pygame.mixer.init()
        self.threadpool = QThreadPool()
        self.on = False
        # Initialize window properties
        self.setWindowTitle("Shutdown Timer")

        config_path = os.path.join(os.path.expanduser("~"), "shutdown_timer_config.json")

        try:
            if os.path.isfile(config_path):
                global CONFIGURATION
                with open(config_path) as file:
                    data = json.load(file)
                CONFIGURATION = data["total increase in timer"]
                self.system_action = data["system action"]
            else:
                self.system_action = "shutdown"
        except:
            self.system_action = "shutdown"
        
        # Load and scale clock image
        original_pixmap = QPixmap(resource_path("images/clock.png"))
        new_width = int(original_pixmap.width() * scale_factor)
        new_height = int(original_pixmap.height() * scale_factor)
        self.clock_shape = original_pixmap.scaled(
            new_width, new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.red_btn_pos_x = new_width // 2 - 20

        # Load red button image
        red_button_pixmap = QPixmap(resource_path("images/red-button.png")).scaled(
            int(new_width * 0.15),  # Smaller button size
            int(new_height * 0.15),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.red_button = red_button_pixmap

        # Create a custom mask that includes the red button
        full_mask = QPixmap(self.clock_shape.size())
        full_mask.fill(Qt.transparent)
    
        painter = QPainter(full_mask)
        painter.drawPixmap(0, 0, self.clock_shape)
        # Ensure red button area is also transparent
        painter.drawPixmap(self.red_btn_pos_x, 0, self.red_button)
        painter.end()

        # Set the new mask
        self.setFixedSize(full_mask.size())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMask(full_mask.mask())
        
        # Countdown state
        self.countdown_time = QTime(0, 0, 0)
        self.not_alarm = self.not_countdown = True
        
        # Total countdown time for red region rising
        self.total_countdown_seconds = 0

        # Load hand images
        self.minute_hand_image = QPixmap(resource_path(resource_path("images/hour_hand.png"))).scaled(
            int(original_pixmap.width() * scale_factor * 0.20),
            int(original_pixmap.height() * scale_factor * 0.20),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
    
        self.second_hand_image = QPixmap(resource_path(resource_path("images/minute_hand.png"))).scaled(
            int(original_pixmap.width() * scale_factor * 0.35),
            int(original_pixmap.height() * scale_factor * 0.35),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        print(self.system_action)
        # Vibration setup
        self.original_position = self.pos()
        self.vibration_offset = [QPoint(-5, 0), QPoint(5, 0), QPoint(0, -5), QPoint(0, 5)]
        self.vibration_index = 0
        self.vibration_timer = QTimer(self)
        self.vibration_timer.timeout.connect(self.vibrate)

        # Main timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)

    def mousePressEvent(self, event):
        """Handle mouse clicks for red button"""
        global COUNTDOWN, CONFIGURATION
        if event.button() == Qt.LeftButton:
            # Check if click is within red button area
            if (event.x() >= self.red_btn_pos_x and 
                event.x() <= self.red_btn_pos_x + self.red_button.width() and 
                event.y() <= self.red_button.height()):
                COUNTDOWN += CONFIGURATION
                if COUNTDOWN > 0:
                    self.on = True
                    self.stop_vibration()
                    self.stop_background_sound()
                    self.start_countdown(COUNTDOWN)
            else:
                button_rect = self.red_button.rect()
                if button_rect.contains(event.pos()):
                    CONFIGURATION, self.system_action = self.configure_countdown_time()

    def configure_countdown_time(self):
        """
        Prompt user for countdown time and system action with an elegantly designed dialog.
        
        Returns:
            tuple: (total seconds, system action) or (0, None) if canceled
        """
        # Custom styled dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("System Action Timer")
        dialog.setMinimumWidth(450)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                margin-bottom: 10px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid #ff0000;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QPushButton {
                background-color: #ff0000;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Title and description
        title_label = QLabel("Configuration")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            text-align: center;
        """)
        layout.addWidget(title_label)
        
        # System Action Dropdown
        action_layout = QHBoxLayout()
        action_label = QLabel("Select System Action:")
        action_dropdown = QComboBox()
        action_dropdown.addItems(["Shutdown", "Restart", "Sleep", "Nothing"])
        if self.system_action == "restart":
            x = 1
        elif self.system_action == "sleep":
            x = 2
        elif self.system_action is None:
            x = 3
        else:
            x = 0
        action_dropdown.setCurrentIndex(x)
        
        action_layout.addWidget(action_label)
        action_layout.addWidget(action_dropdown)
        layout.addLayout(action_layout)
        
        # Time input layout
        input_layout = QHBoxLayout()
        time_label = QLabel("Enter Time (HH:MM:SS):")
        time_input = QLineEdit()
        time_input.setPlaceholderText("01:30:45")
        
        input_layout.addWidget(time_label)
        input_layout.addWidget(time_input)
        layout.addLayout(input_layout)
        
        # Example and hint
        hint_label = QLabel(
            "Examples:\n"
            "• 01:30:45 = 1 hour, 30 minutes, 45 seconds\n"
            "• 00:15:00 = 15 minutes\n"
            "• 02:00:00 = 2 hours"
        )
        hint_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(hint_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        confirm_btn = QPushButton("Save Settings")
        cancel_btn = QPushButton("Cancel")
        
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Connect buttons
        confirm_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Show dialog and process result
        if dialog.exec_() == QDialog.Accepted:
            try:
                # Parse input
                input_text = time_input.text()
                hours, minutes, seconds = map(int, input_text.split(':'))
                
                # Get selected system action
                system_action = action_dropdown.currentText().lower()
                if system_action == "nothing":
                    system_action = None
                # Validate time ranges
                if (0 <= hours <= 24 and 
                    0 <= minutes <= 59 and 
                    0 <= seconds <= 59):
                    
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                    
                    # Confirmation message
                    confirm = QMessageBox(self)
                    confirm.setWindowTitle("Confirm Action")
                    confirm.setText(
                        f"System will {system_action} in:\n"
                        f"• {hours} hours\n"
                        f"• {minutes} minutes\n"
                        f"• {seconds} seconds"
                    )
                    confirm.setIcon(QMessageBox.Question)
                    confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    config_file = os.path.join(os.path.expanduser("~"), "shutdown_timer_config.json")
                    if confirm.exec_() == QMessageBox.Yes:
                        if not os.path.isfile(config_file):
                            with open(config_file, "w") as file:
                                json.dump({
                                    "total increase in timer": total_seconds,
                                    "system action": system_action
                                }, file, indent=4)
                        else:
                                                # Update the existing config.json file
                            with open(config_file, "r") as file:
                                data = json.load(file)  # Load current data into a dictionary

                            # Update the data with new values
                            data.update({
                                "total increase in timer": total_seconds,
                                "system action": system_action
                            })

                            # Write updated data back to the file
                            with open(config_file, "w") as file:
                                json.dump(data, file, indent=4)
                        return total_seconds, system_action
                else:
                    QMessageBox.warning(
                        self, 
                        "Invalid Input", 
                        "Please enter valid times:\n"
                        "• Hours: 0-24\n"
                        "• Minutes: 0-59\n"
                        "• Seconds: 0-59"
                    )
            
            except ValueError:
                QMessageBox.warning(
                    self, 
                    "Incorrect Format", 
                    "Please use 'HH:MM:SS' format\n"
                    "Example: 01:30:45"
                )
        
        return CONFIGURATION, self.system_action
    
    def start_countdown(self, total_seconds):
        """Start the countdown timer"""
        self.start_background_sound('ticking-clock-sound.mp3', loop=True)
        self.total_countdown_seconds = total_seconds
        self.countdown_time = QTime(0, total_seconds // 60, total_seconds % 60)
        self.timer.start(1000)  # Update every second

    def start_background_sound(self, sound_path, start_time=0, loop=False):
        """Play background sound asynchronously"""
        worker = SoundWorker(resource_path(os.path.join('sounds', sound_path)), start_time, loop)
        self.threadpool.start(worker)

    def stop_vibration(self):
        """Stop the vibration effect"""
        self.vibration_timer.stop()
        self.move(self.original_position)

    def stop_background_sound(self):
        """Stop all background music and sounds"""
        pygame.mixer.music.stop()
        pygame.mixer.stop()
    
    def update_clock(self):
        """Update clock state and countdown"""
        self.countdown_time = self.countdown_time.addSecs(-1)
        global COUNTDOWN
        COUNTDOWN -= 1

        if self.countdown_time > QTime(0, 0, 25) and not self.not_countdown:
            self.not_countdown = True
            self.stop_background_sound()
            self.stop_vibration()
        
        elif self.countdown_time <= QTime(0, 0, 23) and self.not_countdown:
            self.vibration_timer.start(100)
            self.not_countdown = False
            # start_time = 24 - self.countdown_time.second()
            self.start_background_sound('countdown.mp3', start_time=0)
            
            if self.not_alarm:
                self.start_background_sound('alarm.mp3', loop=True)
                self.not_alarm = False
        
        if self.countdown_time == QTime(0, 0, 3):
            self.start_background_sound('bomb-beeps.mp3')
            self.start_background_sound('explode.mp3')
        
        if self.countdown_time == QTime(0, 0, 0):
            self.vibration_timer.stop()
            self.timer.stop()
            self.stop_background_sound()
            # Uncomment to actually shutdown system
            shutdown_system(action=self.system_action)
        
        self.update()

    def paintEvent(self, event):
        """Redraw the clock and red button"""
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.clock_shape)
        
        # Draw red button in top-left corner
        painter.drawPixmap(self.red_btn_pos_x, 0, self.red_button)
        
        self.draw_dynamic_clock(painter)
        self.draw_rising_red_region(painter)

    def draw_dynamic_clock(self, painter):
        """Draw and rotate clock hands"""
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
        
    def draw_rising_red_region(self, painter):
        """Draw a rising red region as countdown approaches zero"""
        if self.total_countdown_seconds == 0:
            return

        # Calculate remaining time fraction
        remaining_fraction = (self.countdown_time.minute() * 60 + self.countdown_time.second()) / self.total_countdown_seconds
        
        # Center of the clock
        center_x = (self.width() // 2)
        center_y = (self.height() // 2) - 8

        # Dimensions for the rising region
        width = self.width()   # 60% of clock width
        height = self.height()   # 50% of clock height

        # Calculate current height of the red region
        current_height = height * (1 - remaining_fraction)

        # Create a path for the rising region
        path = QPainterPath()
        path.addRect(
            center_x - width/2, 
            center_y + height/2 - current_height, 
            width, 
            current_height
        )

        # Set up semi-transparent red color
        painter.setBrush(QColor(198, 40, 40, 255))  # Slightly transparent red
        painter.setPen(Qt.NoPen)

        # Draw the rising red region
        painter.drawPath(path)
        
    def vibrate(self):
        """Simulate vibration effect"""
        offset = self.vibration_offset[self.vibration_index]
        self.move(self.original_position + offset)
        self.vibration_index = (self.vibration_index + 1) % len(self.vibration_offset)

def main():
    """Main function to start the app"""
    app = QApplication(sys.argv)
    shutdown_timer = ShutdownTimerApp(scale_factor=0.15)
    shutdown_timer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()