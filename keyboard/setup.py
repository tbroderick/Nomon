import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["newbroderclocks","dtree","config","kconfig","widgets","new_subWindows","mainWindow","string","time","PyQt4.QtGui","PyQt4.QtCore","numpy","sys","cPickle","pickle_util","random","os","pretraininginference","clock_util","clock_inference_engine"],
                     "include_files": ["data", "save", "corpus", "phrases", "icons", 'user_preferences']}#"pygame",

base = None

if sys.platform == "win32":
    base = "Win32GUI"
    
elif sys.platform == "win64":
    base = "Win64GUI"

setup(name="Nomon",
      version="1.1",
      description = "Add description",
      options={"build_exe": build_exe_options},
      executables=[Executable("new_keyboard.py", base=base,
                                icon="nomon.ico",
                                shortcutName="Nomon",
                                shortcutDir="DesktopFolder",)])
