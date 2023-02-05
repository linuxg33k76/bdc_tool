#! /usr/bin/env python3

import os

class FileHandler():

    def __init__(self, filepath, filename):
        self.filename = filename
        self.filepath = filepath
        self.fullfile = os.path.join(filepath, filename)
        self.home_dir = os.getenv('HOME')

    def get_csv_headers(self):

        with open(self.fullfile, 'r') as f:
            data = f.readline().strip('\n').replace('"','')
        return data.split(',')


    def read_file(self):
        with open(self.fullfile, 'r') as f:
            data = f.readlines()
        return data
    
    def write_file(self, data):
        with open(self.fullfile, 'w') as f:
            f.write_line(data)

    def get_home_directory(self):
        return os.gethome()

    def get_cwd(self):
        return os.getcwd()

    def path_check(self):
        
        if os.path.exists(self.filepath):
            return True
        else:
            return False


    def file_check(self):

        '''
        Test for file existance.

        file: string (complete path to file)

        return: bool
        '''
        
        if os.path.isfile(self.fullfile):
            return True
        else:
            return False
    
class MiscTools():

    def __init__(self):
        pass

    def get_terminal_width(self):
       
        '''
        Check for terminal window size

        return: integer
        '''

        width = os.popen('stty size', 'r').read().split()[1]

        print(f'Screen Width: {width}')

        return int(width)
