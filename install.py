#!/usr/bin/env python3

import os

# Create Python virtual environment
directory = os.getcwd()
os.system(f'python3 -m venv {directory}')
os.system('source bin/activate')
os.system(f'{directory}/bin/python3 -m pip install -r requirements.txt')

print('Virtual environment created and packages installed successfully!')
print('To activate the virtual environment, run the following command:')
print(f'cd {directory} && source bin/activate')
print('To deactivate the virtual environment, run the following command:')
print('deactivate')


       