#!/bin/bash

# Update pacman cache and install dependencies
pacman --noconfirm -Sy git python-pip

# Clone the repository
git clone https://github.com/grm34/PyArchboot.git

# Install requirements
pip install -r PyArchboot/requirements.txt
