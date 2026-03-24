#coding: UTF8
"""
Setup program for Memory Serves

"""

from cx_Freeze import setup, Executable

base = "Win32GUI"


def main():
    """
    runs setup when called as main
    """
    setup(name="MemoryServes",
          version="0.1",
          description="Server for Felix translation memories and glossaries",
          options=dict(build_exe=dict(
              excludes=['tkinter']
          )),
          executables=[Executable("main.py", base=base)])

if __name__ == "__main__":
    main()
