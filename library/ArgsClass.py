#!/usr/bin/env python3



import argparse


class CLIParser(argparse.ArgumentParser):

    '''
    --------------------------------------------------------------------------------
    Description:  Collect cli arguments and present help commands - an extension
    of argparse.ArgumentParser() class.
    Parameter(s):  None
    Return: None.
    --------------------------------------------------------------------------------
    '''

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-c', '--cli', help='CLI Interface for Data Input', action='store_true')
        self.parser.add_argument('-v', '--verbose', help='Display output traps', action='store_true')
        self.parser.add_argument('-t','--test', help='Turn on test features', action='store_true')
        self.args = self.parser.parse_args()

    def get_args(self):

        '''
        --------------------------------------------------------------------------------
        Description:  Return cli arguments.
        Parameter(s):  self : instance of CLIParser() class
        Return: self.args : object
        --------------------------------------------------------------------------------
        '''

        return self.args