#!/usr/bin/env python3

import os

# Uninstall the virtual environment
directory = os.getcwd()

# Deactivate the virtual environment
os.system('deactivate')

# Uninstall the virtual environment
os.system(f'rm -rf {directory}/bin')
os.system(f'rm -rf {directory}/include')
os.system(f'rm -rf {directory}/lib')
os.system(f'rm -rf {directory}/lib64')
os.system(f'rm -rf {directory}/pyvenv.cfg')

# Print uninstallation message
print('\n***Virtual environment uninstalled successfully!***\n')