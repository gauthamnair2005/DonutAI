import sys
from cx_Freeze import setup, Executable

setup(
    name = "DonutAI",
    version = "1.0",
    description = "DonutAI Assistant",
    executables = [Executable("DAIB.py", base = "Win32GUI")]
)
