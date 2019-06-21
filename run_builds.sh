#!/usr/bin/env bash

# Nuke old vagrant-cloud boxes
bash ${PWD}/cleanup_boxes.sh

# Cleanout old build artifacts
python utils.py cleanup_builds

# Create all vagrant boxes
python utils.py create_all

# Build all the things
time (python utils.py build_all | tee build.log)
#time (python utils.py gotta_go_fast | tee build.log)
