#!/bin/env python3

# Imports
import tkinter as tk
from tkinter import filedialog
import os
from datetime import datetime

class BDCGUI():

    def __init__(self):

        '''

        Initialize Class with some key file elements.
        This class is specific code to supplement the BDC Tool.

        '''
        self.date_ref = datetime.today().strftime('%d-%b-%Y')
        self.home = os.getenv("HOME")
        self.outfile = self.home + f'/bdc_tool/output/bdc_tool_ouput_{self.date_ref}.csv'
        self.distance = '300'

        self.create_gui()
       

    def create_gui(self):

        '''

        Create the main user input window.

        class attributes : various

        returns: None

        '''
        # Set Window Theme
        # sg.theme('System Default')
        self.root = tk.Tk()

        # Define Window Title
        title = "BDC Tool GUI"


        # Create the main window
        self.root.title(title)
        self.root.geometry("900x300")

        # Create labels and entry fields

        # Create FCC File Entry
        tk.Label(self.root, text="Select FCC File:").grid(row=0, column=0, sticky='w')
        self.fcc_file_entry = tk.Entry(self.root, width=80)
        self.fcc_file_entry.grid(row=1, column=0)
        tk.Button(self.root, text="Browse FCC File", command=self.browse_fcc).grid(row=1, column=2)

        # Create Services Manager (SM) File Entry    
        tk.Label(self.root, text="Select SM File:").grid(row=2, column=0, sticky='w')
        self.sm_file_entry = tk.Entry(self.root, width=80)
        self.sm_file_entry.grid(row=3, column=0)
        tk.Button(self.root, text="Browse SM File", command=self.browse_sm).grid(row=3, column=2)

        # Create Output File Entry
        tk.Label(self.root, text="Enter Output File:", justify="left").grid(row=4, column=0, sticky='w')
        self.outfile_entry = tk.Entry(self.root, justify="left", width=80)
        self.outfile_entry.insert(0, self.outfile)
        self.outfile_entry.grid(row=5, column=0)

        # Create Distance Entry
        tk.Label(self.root, text="Enter Distance:", justify="left").grid(row=6, column=0, sticky='w')
        self.distance_entry = tk.Entry(self.root, justify="right", width=80)
        self.distance_entry.insert(0, self.distance)
        self.distance_entry.grid(row=7, column=0)
        tk.Label(self.root, text="Distance in feet").grid(row=7, column=2)

        # Create Submit button and close window when clicked
        tk.Button(self.root, text="Submit", command=self.process_data).grid(row=8, column=0)

        # Run the GUI
        self.root.mainloop()

        
    def browse_fcc(self):

        '''

        Browse for the FCC file and insert the path into the entry field.

        class attributes : various

        returns: None

        '''

        self.fcc_file_entry.delete(0, tk.END)
        self.fcc_file_entry.insert(0, filedialog.askopenfilename())

    def browse_sm(self):

        '''
        Browse for the SM file and insert the path into the entry field.

        class attributes : various

        returns: None
        '''

        self.sm_file_entry.delete(0, tk.END)
        self.sm_file_entry.insert(0, filedialog.askopenfilename())

    def process_data(self):

        '''
        Process the data entered by the user in the GUI.
        
        class attributes : various

        returns: None
        '''

        data_dict = {
            'fcc_file': self.fcc_file_entry.get(),
            'sm_file': self.sm_file_entry.get(),
            'outfile': self.outfile_entry.get(),
            'distance': self.distance_entry.get()
        }

        # Assign User input to class attributes for assignment in main program
        self.fcc_file = data_dict['fcc_file']
        self.sm_file = data_dict['sm_file']
        self.outfile = data_dict['outfile']
        self.distance = data_dict['distance']

        # Test for outfile path and create if it does not exist
        p, f = os.path.split(self.outfile)
        if os.path.isdir(p):
            pass
        else:
            os.makedirs(p)

        # Print the values entered by user
        # print(data_dict)

        # Close the GUI
        self.root.destroy()
