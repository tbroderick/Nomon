import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["new_broderclocks","dtree","config","kconfig","widgets","new_subWindows","mainWindow","string","time","PyQt4.QtGui","PyQt4.QtCore","numpy","sys","cPickle","random","os"],
                     "include_files": ["data", "save", "corpus", "phrases", "icons", 'user_preferences',"../kernel_density_estimation/pretraining_inference.py","../kernel_density_estimation/clock_util.py","../kernel_density_estimation/clock_inference_engine.py"]}#"pygame",

base = None

if sys.platform == "win32":
    base = "Win32GUI"
    
elif sys.platform == "win64":
    base = "Win64GUI"

setup(name = "Nomon",
      version = "1.0",
      description = "Add description",
      options = {"build_exe": build_exe_options},
      executables = [Executable("new_keyboard.py", base=base,
                                icon="nomon.ico",
                                shortcutName="Nomon",
                                shortcutDir="DesktopFolder",)])
