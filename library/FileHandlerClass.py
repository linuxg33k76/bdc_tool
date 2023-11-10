#! /usr/bin/env python3

'''
File Handler / Misc Tools Class File

This file contains classes to manage file actions.
This class could have been included in main program, but wanted to practice
writing classes and making class instances for the two input and one output file
is a more managable way to handle file activities.

Program Created by Ben Calvert (and ChatGPT3)
Date: 2/4/2023

Apache 2.0 License

'''


import os

class FileHandler():

    def __init__(self, filename):

        '''
        Initialization Method

        filename: string (complete path to file)

        return: None
        '''

        self.filename = filename
        self.path = filename.split('/')[-1]
        self.home_dir = os.getenv('HOME')

    def get_csv_header(self):

        '''
        Get first row of CSV file (header information).

        return: Array
        '''

        with open(self.filename, 'r') as f:
            data = f.readline().strip('\n').replace('"','').replace('\ufeff','')
        return data.split(',')


    def read_file(self):

        '''
        Read file method

        return: Array
        '''

        with open(self.filename, 'r') as f:
            data = f.readlines()
        return data
    
    def write_file(self, data):

        '''
        write file method - OVERWRITES data in file

        return: None
        '''

        with open(self.filename, 'w') as f:
            f.write(data)

    def write_append_to_file(self, data):

        '''
        write file method - APPENDS data in file

        return: None
        '''

        with open(self.filename, 'a') as f:
            f.write(data)

    def get_cwd(self):

        '''
        Get current working directory.

        return: string
        '''

        return os.getcwd()

    def path_check(self):

        '''
        Validates if file path exists

        return: bool
        '''

        if os.path.exists(self.path):
            return True
        else:
            return False



    
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

    def path_check(filename):
        '''
        Test for path existance.

        file: string (complete path to file)

        return: bool
        ''' 

        path, file = os.path.split(filename)
        if os.path.isdir(path):
            return True
        else:
            return False


    def create_dir(path):

        '''
        Create directory helper method.

        return: None
        '''

        os.mkdir(path)