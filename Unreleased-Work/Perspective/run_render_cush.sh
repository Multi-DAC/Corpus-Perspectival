#!/bin/bash
# Detached launcher for the Chatterbox (Cush Jumbo) full-book render.
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Unreleased-Work/Perspective || exit 1
exec > audiobook/render_cush.log 2>&1
exec python3 -u make_audiobook3.py --cfg=0.3
