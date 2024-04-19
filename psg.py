"""
File: psg.py
Author: Kevin Li
Description: This file creates the gui for the grade formatting program.
"""

import PySimpleGUI as sg

def run_gui():
    retVal = ["-i", "txt.txt", "csv.csv"]
    layout = [
        [sg.Text("Enter the usage mode: ")],
        [sg.In(size = (25, 1), enable_events = True)],
        [sg.Text("Enter txt file name: ")],
        [sg.In(size=(25, 1), enable_events=True)], 
        [sg.Text("Enter csv file name: ")], 
        [sg.In(size=(25, 1), enable_events=True)], 
        [sg.Button("SUBMIT")]
        ]

    # Create the Window
    window = sg.Window("Grade Formatter", layout)


    # Event Loop
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "SUBMIT":
            retVal[0] = values[0]
            retVal[1] = values[1]
            retVal[2] = values[2]
            break

    window.close()

    return retVal;