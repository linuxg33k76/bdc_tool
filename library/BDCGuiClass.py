#!/bin/env python3

# Import PySimpleGUI
import PySimpleGUI as sg
import os

class BDCGUI():

    def __init__(self):
        self.home = os.getenv("HOME")
        self.outfile = self.home + '/bdc_tool/output/bdc_tool_ouput.csv'

        self.create_gui()
       

    def create_gui(self):
        # Define Window Title
        title = "BDC Tool GUI"
        # Define the layout of the GUI
        layout = [
            # Two file select input boxes with labels
            [sg.Text("Select FCC Fabric file:"), sg.Input(), sg.FileBrowse(initial_folder = self.home, file_types=(("Text Files", "*.csv"),))],
            [sg.Text("Select M4 SM file:       "), sg.Input(), sg.FileBrowse(initial_folder = self.home, file_types=(("Text Files", "*.csv"),))],
            # Two general input boxes with labels
            [sg.Text("Output File:                 "), sg.InputText(key="outfile",default_text = self.outfile)],
            [sg.Text("Distance in FT:           "), sg.InputText(key="distance",default_text='50')],
            # A submit button
            [sg.Button("Submit")]
        ]

        # Create the window object
        window = sg.Window(title, layout)

        # Event loop to process user input
        while True:
            event, values = window.read()
            
            # If user closes window or clicks submit, break loop
            if event in (None, "Submit"):
                break

        # Close the window
        window.close()

        # Create data dictionary of user inputs
        self.data = {
            "fcc_file" : values[0],
            "sm_file"  : values[1],
            "outfile" : values['outfile'],
            "distance" : values['distance']
        }
        self.fcc_file = values[0]
        self.sm_file = values[1]
        self.outfile = values['outfile']
        self.distance = values['distance']

        # Test for outfile path and create if it does not exist
        p, f = os.path.split(self.outfile)
        if os.path.isdir(p):
            pass
        else:
            os.makedirs(p)

        # Print the values entered by user
        # print(f"You selected {values[0]} and {values[1]} as files.")
        # print(f"You entered {values['outfile']} and {values['distance']} as values.")

        # return data
        # return self.data
