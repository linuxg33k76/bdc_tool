#! /usr/bin/env python3

import os

class FileHandler():

    def __init__(self, filename):
        self.filename = filename
        self.path = filename.split('/')[-1]
        self.home_dir = os.getenv('HOME')

    def get_csv_header(self):

        with open(self.filename, 'r') as f:
            data = f.readline().strip('\n').replace('"','').replace('\ufeff','')
        return data.split(',')


    def read_file(self):
        with open(self.filename, 'r') as f:
            data = f.readlines()
        return data
    
    def write_file(self, data):
        # path_exists = self.path_check()
        # if path_exists is False:
        #     self.create_dir()
        with open(self.filename, 'w') as f:
            f.write(data)

    def write_append_to_file(self, data):
        # path_exists = self.path_check()
        # if path_exists is False:
        #     self.create_dir()
        with open(self.filename, 'a') as f:
            f.write(data)

    def get_cwd(self):
        return os.getcwd()

    def path_check(self):
        if os.path.exists(self.path):
            return True
        else:
            return False

    def create_dir(self):
        os.mkdir(self.path)


    
    
class MiscTools():


    def get_terminal_width(self):
       
        '''
        Check for terminal window size

        return: integer
        '''

        width = os.popen('stty size', 'r').read().split()[1]

        return int(width)

    def file_check(filename):

        '''
        Test for file existance.

        file: string (complete path to file)

        return: bool
        '''
        
        if os.path.isfile(filename):
            return True
        else:
            return False