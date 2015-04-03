import Tkinter as tk
import tkFileDialog

class MainGui(object):
    def __init__(self):
        #Create a main dialog
        root = tk.Tk()
        #Hide the main dialog
        root.withdraw()
        #Opens the Dialog to choose a folder
        self.dirname = tkFileDialog.askdirectory(parent=root, initialdir='/',
                title='Please Select a Folder')
