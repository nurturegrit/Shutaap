from cx_Freeze import setup, Executable
import sys
import os
import PyQt5

# Get the QML imports path
qml_path = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'qml')
qt_plugins_path = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins')

include_files = [
    'images',
    'sounds',
    # Specify the QML and plugins directories
    (qml_path, 'qml'),
    (qt_plugins_path, 'plugins')
]

# Determine the correct base
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # This will prevent a console window from appearing

build_exe_options = {
    "packages": ["pygame", "PyQt5", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets", "PyQt5.QtQml"],
    "include_files": include_files,
    "excludes": ["tkinter", "unittest"],
    "zip_include_packages": ["*"],
    "zip_exclude_packages": ["PyQt5"],
}

# Specify the path to your main Python file
executables = [Executable('shutaap.py', base=base)]

setup(
    name="Shutaap",
    version="1.0",
    description="Shutaap app",
    options={"build_exe": build_exe_options},
    executables=executables
)