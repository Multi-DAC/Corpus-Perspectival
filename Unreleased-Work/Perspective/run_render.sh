#!/bin/bash
# Detached launcher for the Perspective audiobook render.
# Invoked as a single space-free arg by Start-Process wsl.exe so nothing gets re-split.
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Unreleased-Work/Perspective || exit 1
exec > audiobook/render.log 2>&1                       # redirect all output to the log
exec python3 -u make_audiobook.py bf_emma --blend=bf_lily --blend-amt=0.5 --speed=0.78
