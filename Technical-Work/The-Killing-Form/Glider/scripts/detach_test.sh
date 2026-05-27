#!/bin/bash
# Trivial detach-reliability test: writes START, sleeps 4s, writes DONE.
# If the detached child survives parent exit, the log gets BOTH lines.
echo "START $(date +%T) arg=$1"
sleep 4
echo "DONE  $(date +%T) arg=$1"
