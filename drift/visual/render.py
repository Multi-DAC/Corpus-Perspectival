#!/usr/bin/env python3
"""Launch Manim with MiKTeX and FFmpeg on PATH."""
import os
import sys
import subprocess

# Add MiKTeX and our bin to PATH
miktex = r'C:\Users\mercu\AppData\Local\Programs\MiKTeX\miktex\bin\x64'
userbin = r'C:\Users\mercu\bin'
os.environ['PATH'] = miktex + ';' + userbin + ';' + os.environ.get('PATH', '')

# Run manim with forwarded args
args = [sys.executable, '-m', 'manim'] + sys.argv[1:]
sys.exit(subprocess.run(args).returncode)
