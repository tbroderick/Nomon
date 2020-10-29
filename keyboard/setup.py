######################################
# Copyright 2019 Nicholas Bonaker, Keith Vertanen, Emli-Mari Nel, Tamara Broderick
# This file is part of the Nomon software.
# Nomon is free software: you can redistribute it and/or modify it
# under the terms of the MIT License reproduced below.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY
# OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR
#OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# <https://opensource.org/licenses/mit-license.html>
######################################


import sys, os
from cx_Freeze import setup, Executable

import os.path
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
# os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6'
# os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')


build_exe_options = {"packages": ["broderclocks","kenlm_lm","predictor","char_predictor","vocabtrie","config","kconfig","widgets","subWindows","mainWindow",
                                  "string", "time", "numpy", "win32api", "win32con", "win_output", "playsound", "gtts",
                                  "sys","Pickle","pickle_util", "random", "pathlib", "appdirs", "re", "emoji", "socket",
                                  "os","pretraininginference","clock_util","clock_inference_engine", "kenlm", "phrases"],
                     "include_files": ["icons", "resources"]}#"pygame",

base = None

if sys.platform == "win32":
    base = "Win32GUI"

elif sys.platform == "win64":
    base = "Win64GUI"

setup(name="Nomon",
      version="3.6.0",
      description = "Python 3, PySide2, Text Output, TTS",
      options={"build_exe": build_exe_options},
      executables=[Executable("keyboard.py", base=base,
                                icon="nomon.ico",
                                shortcutName="Nomon",
                                shortcutDir="DesktopFolder",)])
