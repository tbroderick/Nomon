import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["new_subWindows","new_broderclocks","pickle_util","dtree","config","kconfig","widgets","subWindows","mainWindow","string","time","PyQt4.QtGui","PyQt4.QtCore","numpy","sys","cPickle","random","os"],
                     "include_files": ["data",  "corpus", "phrases", "icons", 'user_preferences','../kernel_density_estimation']}#"pygame",

# =============================================================================
# base = "Win64GUI"
# 
# if sys.platform == "win32":
#     base = "Win32GUI"
#     
# elif sys.platform == "win64":
#     base = "Win64GUI"
# 
# =============================================================================
setup(name = "Nomon",
      version = "0.4",
      description = "Add description",
      options = {"build_exe": build_exe_options},
      executables = [Executable("new_keyboard.py", base=None,
                                icon="nomon.ico",
                                shortcutName="Nomon",
                                shortcutDir="DesktopFolder")])
