import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["broderclocks","dtree","config","kconfig","ToolTip","string","time","Tkinter","numpy","sys","cPickle","random","os"],
                     "include_files": ["data", "corpus", "phrases", "save"]}#"pygame",

base = None

if sys.platform == "win32":
    base = "Win32GUI"
    
elif sys.platform == "win64":
    base = "Win64GUI"

setup(name = "Nomon",
      version = "0.4",
      description = "Add description",
      options = {"build_exe": build_exe_options},
      executables = [Executable("keyboard.py", base=base)])
