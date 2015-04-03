#!/usr/bin/env python
import re

import Tkinter as tk
import tkFileDialog
import tkMessageBox

import dicom

from os import walk
from os.path import join

class MainGui(object):
    """
        Class Resposible to create the GUIs
    """
    def __init__(self):
        """
            Initiates the class and opes a dialog box
        """
        #Create a main dialog
        root = tk.Tk()
        #Hide the main dialog
        root.withdraw()
        #Opens the Dialog to choose a folder
        self.dirname = tkFileDialog.askdirectory(parent=root,
                initialdir='../..', title='Please Select a Folder')

    def _list_dir(self):
        """
            Return the name of the files in the choosen folder
        """

        files_in_folder = [file_name for file_name in self._file_generator()]

        return files_in_folder

    def _file_generator(self):
        """
            Generator of all files in the choosen folder ignoring subfolders
        """
        #walk through all files in self.dirname. Without subfolders
        for file_name in next(walk(self.dirname))[2]:
            if file_name.endswith(".dcm"):
                yield file_name

    def _get_input(self):
        """
            Callback for the Study Id Ok button
        """
        study_id = self.entry.get()
        #Check for empty field
        if study_id.strip():
            if not self._check_input(study_id):
                #If input is out of format a errormsg is raised
                tkMessageBox.showerror("Study Id Error",
                        "Study Id not recognized")
                self.root.quit()
            else:
                self.root.quit()
                return study_id

    def _input_gui(self):
        """
            Create a GUI with input field
        """
        self.root = tk.Tk()
        tk.Label(self.root, text="Study Id:").grid(row=0)
        #Input Field
        self.entry = tk.Entry(self.root)
        self.entry.grid(row=0, column=1)
        #Cancel Button
        bt1 = tk.Button(self.root, text='Cancel',
                command=self.root.quit).grid(row=2, column=0, pady=4)
        #Ok Button
        bt2 = tk.Button(self.root, text="Ok",
                command=self._get_input).grid(row=2, column=1, pady=4)
        self.root.mainloop()

    def _check_input(self, input_id):
        """
            Check the pattern of the input studyid, i.e: 12345678
            input -> text from GUI
            return -> True/False
        """
        #Only 8 digits
        id_pattern = r"\d{8}$"
        #Check input
        return True if re.match(id_pattern, input_id) else False


class Anonymize(object):
    def __init__(self, folder_path, file_name_list):
        self.folder_path = folder_path
        self.file_name_list = file_name_list

    def _open_dicom_files(self):
        pass


if __name__ == '__main__':
    gui = MainGui()
    if len(gui.dirname.strip()) > 0:
        gui._input_gui()
