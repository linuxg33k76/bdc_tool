#!/usr/bin/env python3

import os

# Create Python virtual environment

# Get the current working directory
directory = os.getcwd()

# Create a virtual environment
os.system(f'python3 -m venv {directory}')

# Install the required packages in the virtual environment
print('\n***Creating virtual environment and installing packages...***\n')
os.system('source bin/activate')
os.system(f'{directory}/bin/python3 -m pip install -r requirements.txt')

# Print the command to activate the virtual environment
print('\n***Virtual environment created and packages installed successfully!***')
print('\nTo activate the virtual environment, run the following command:')
print(f'\n\tcd {directory} && source bin/activate')
print('\nTo deactivate the virtual environment, run the following command:')
print('\n\tdeactivate\n')




       