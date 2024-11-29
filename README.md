# Shutdown App README

## Overview
This application is designed to provide a dynamic clock interface with a countdown timer. It also includes a red button that, when clicked, triggers the countdown. Once the countdown reaches zero, the app can trigger a shutdown operation. The clock is represented as a visually dynamic interface with ticking sounds, vibration effects, and a bomb-like countdown sound for the final seconds.

## Features
- **Dynamic Clock Interface**: Displays a clock with minute and second hands, which move according to the countdown timer.
- **Background Sounds**: Includes ticking sounds, countdown beeps, and alarm sounds that play based on the countdown status.
- **Vibration Effect**: The window shakes slightly as the countdown approaches zero to add a sense of urgency.
- **Red Button**: A red button interface that allows the user to set the countdown timer (in hours, minutes, and seconds) by inputting their desired time.
- **Shutdown Trigger**: When the countdown reaches zero, a system shutdown command can be executed.

## Requirements
- **Python 3.x**: This app is built using Python.
- **PyQt5**: For creating the GUI.
- **pygame**: For handling sound playback.
- **OS**: The app uses OS commands to trigger the shutdown operation (Windows-based).

To install the required libraries, use the following command:
```bash
pip install pygame PyQt5
```

## Installation
1. Clone or download the repository to your local machine.
2. Ensure that you have the required dependencies installed (PyQt5, pygame).
3. Place your sound files in a folder called `sounds/` (if the folder doesn't exist, create it).
4. Make sure the following image files are present in the `images/` folder:
   - `clock.png` (image for the clock face)
   - `hour_hand.png` (image for the hour hand)
   - `minute_hand.png` (image for the minute hand)
   - `red-button.png` (image for the red button)

## Usage
1. When you run the app, the red button window will appear.
2. Click the red button to input the time for the countdown.
3. Once you have set the time, the countdown will start, and the clock's hands will reflect the passing time.
4. When the countdown reaches zero, the app will trigger a shutdown (currently only on Windows with the `shutdown` command).

### Running the App:
To run the app, simply execute the following in your terminal:
```bash
python shutaap.py
```

## Customization
- **Countdown Time**: You can modify the countdown time by clicking the red button and entering the desired hours, minutes, and seconds.
- **Sound Files**: You can replace the default sounds (e.g., `ticking-clock-sound.mp3`, `countdown.mp3`, etc.) with your own custom sounds, ensuring they are placed in the `sounds/` directory.
- **Shutdown Command**: The current shutdown command is configured for Windows. If you're using a different operating system, you may need to modify the command in the `update_clock` method:
   ```python
   #os.system("shutdown /s /t 1")  # For Windows
   ```

## Notes
- This app is currently designed for use on Windows OS due to the shutdown command.
- If you wish to disable the shutdown feature for testing, you can comment out the `os.system("shutdown /s /t 1")` line in the `update_clock` method.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
- PyQt5 for the GUI framework.
- pygame for sound handling.
