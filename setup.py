import sys
from cx_Freeze import setup, Executable

setup(
    name = "DonutAI",
    version = "23.12.10",
    description = "DonutAI Assistant",
    executables = [Executable("DonutAI.py", base = "Win32GUI")]
)
