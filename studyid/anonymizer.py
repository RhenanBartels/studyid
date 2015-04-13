#!/usr/bin/env python
import re

import Tkinter as tk
import tkFileDialog
import tkMessageBox
import zipfile

import dicom
import jinja2

from os import walk, mkdir
from os.path import join
from Tkinter import Frame

from dicom.errors import InvalidDicomError

FIELD_TAGS = [(0x10, 0x10), (0x08, 0x090), ]
SECRET = "**********"

class MainGui(Frame):
    """
        Class Responsible to create the GUIs
    """
    def __init__(self):
        """
            Initiates the class and opens a dialog box
        """
        #Create a main dialog
        root = tk.Tk()
        #Hide the main dialog
        root.withdraw()
        #Opens the Dialog to choose a folder
        self.dirname = tkFileDialog.askdirectory(parent=root,
                initialdir='../..', title='Please Select a Folder')

        self.studyid = ""

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
        confirm_studyid = self.entry2.get()
        #Check for empty field
        if study_id.strip():
            if not self._check_input(study_id):
                self.show_error_msgs("Study Id Error",
                        "Study Id Format not recognized")
            elif study_id != confirm_studyid:
                self.show_error_msgs("Study Id Error",
                        "Enter with the same study id")
            else:
               #If input is out of format a errormsg is raised
                self.root.quit()

    def _input_gui(self):
        """
            Create a GUI with input field
        """
        self.root = tk.Tk()
        self.root.title("Study Id")
        self.root.update_idletasks()  # Update "requested size" from geometry manager
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) / 2
        y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) / 2
        self.root.geometry("+%d+%d" % (x, y))
        tk.Label(self.root, text="Study Id:").grid(row=0)
        tk.Label(self.root, text="Confirm:").grid(row=1)
        #Input Field
        self.entry = tk.Entry(self.root)
        self.entry.grid(row=0, column=1)
        self.entry2 = tk.Entry(self.root)
        self.entry2.grid(row=1, column=1)
        #Cancel Button
        bt1 = tk.Button(self.root, text='Cancel',
                command=self.root.quit)
        bt1.grid(row=2, column=0, pady=4)
        #Ok Button
        bt2 = tk.Button(self.root, text="Ok",
                command=self._get_input)
        bt2.grid(row=2, column=1, pady=4)
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
        if re.match(id_pattern, input_id):
            self.studyid = input_id
            return True
        return False


    def show_error_msgs(self, title, msg):
        """
            Error Log
        """
        tkMessageBox.showerror(title, msg)


class Anonymize(object):
    """
        Class responsible to anonymize DICOM files
    """
    def __init__(self, gui_object):
        self.gui_object = gui_object
        self.folder_path = gui_object.dirname
        self.file_name_list = gui_object._list_dir()

    def anonymize(self, dicom_list):
        """
            Replace all desired field (FIELD_TAGS) with ********* (SECRET)
        """
        for dicom_file, dicom_name in zip(dicom_list, self.file_name_list):
            dicom_file = self.__hide(dicom_file)
            self._save_dicom_file(dicom_file, dicom_name)

    def main(self):
        """
            Main method.
        """
        #Read DICOM files from selected folder
        dicom_list = self._open_dicom_files()
        #Check if there are more than one patient
        any_error = self._check_patient(dicom_list)
        studyid = self.gui_object.studyid
        if studyid and dicom_list:
            if not any_error:
                try:
                    #Create a SubFolder inside selected Folder
                    #Called Anonymized
                    self._make_subfolder()
                    dicom_list = self._set_studyid(dicom_list, studyid)
                    #Create a text file with DICOM information
                    self._create_text_file(dicom_list[0])
                    self.anonymize(dicom_list)
                    self._zip_files()
                except OSError, e:
                    self.gui_object.show_error_msgs("Create Folder Error", e)
            else:
                    self._patient_error_msg(any_error)

    def __hide(self, dicom_file):
        """
            Replace DICOM fields with **********
        """
        for dicom_tag in FIELD_TAGS:
            try:
                dicom_file[dicom_tag].value = SECRET
            except KeyError:
                continue
        return dicom_file

    def _set_studyid(self, dicom_list, studyid):
        """
            Replace the PatientId field with the generated one
        """
        for dicom_file in dicom_list:
            dicom_file[0x10, 0x20].value = studyid
        return dicom_list

    def _render_template(self, dicom_list, studyid):
        template_loader = jinja2.FileSystemLoader(searchpath='.')
        template_env = jinja2.Environment(loader=template_loader)
        template_file = "template.jinja"
        template = template_env.get_template(template_file)

        context = self._prepare_context(dicom_list[0])
        print context
        output_template = template.render(context)
        self._save_template(output_template, studyid)

    def _prepare_context(self, dicom_file):
        list_context = []
        for tags in FIELD_TAGS:
            sub_context = {
                    'tag' : dicom_file[tags].tag,
                    'name' :  dicom_file[tags].name,
                    'value' : dicom_file[tags].value,
            }
            list_context.append(sub_context)

        context = {'fields': list_context}
        return context

    def _save_template(self, output, studyid):
        output_path = join(self.gui_object.dirname, "Anonymized", studyid)
        output_path += ".html"
        with open(output_path, 'wb') as fobj:
            fobj.write(output)

    def _make_subfolder(self):
        """
            Create a subfolder to stored the anonymized DICOM files
        """
        mkdir(join(self.gui_object.dirname, "Anonymized"))

    def _save_dicom_file(self, dicom_file, dicom_name):
        """
            Saves the anonymized Dicom file
        """
        #Path: folder inside selected folder
        save_path = join(self.gui_object.dirname, "Anonymized", dicom_name +
                "_anonymized.dcm")
        dicom_file.save_as(save_path)


    def _zip_files(self):
        """
            Zip all anonymized DICOM files to upload in the WEB API
        """
        zip_file_name = self.gui_object.dirname.split("/")[-1]
        zip_obj = zipfile.ZipFile(join(self.gui_object.dirname, "Anonymized",
            zip_file_name + ".zip"), mode='w')
        for file_name in self.file_name_list:
            zip_obj.write(join(self.gui_object.dirname, file_name))
        zip_obj.close()

    def _open_dicom_files(self):
        """
            Create a list with all DICOM objects in the selected folder
        """
        try:
            dicom_list = [dicom.read_file(join(self.folder_path, file_name))
                    for file_name in self.file_name_list if file_name]
            return dicom_list
        except InvalidDicomError:
            self.gui_object.show_error_msgs("Dicom File Error",
                    "One or more DICOM file with Invalid format")

    def _check_patient(self, dicom_list):
        """
            Check if all files in the selected folder belongs to the same
            patient based on the name of the first patient.
            This function returns a list containing the position in the folder
            representing files with differents patient name
        """
        #Get the name in the first Dicom File and use it to compare with the
        #others Dicom files
        if dicom_list:
            pivot_name = dicom_list[0][FIELD_TAGS[0]].value
            #Find the indexes of files that are different from the pivot
            #file name
            patient_error = [file_index for file_index in
                    range(len(dicom_list)) if
                    dicom_list[file_index][FIELD_TAGS[0]].value != pivot_name]
            return patient_error

    def _patient_error_msg(self, patient_error):
        """
            Raises a Error Message if there are more than on patient inside
            selected folder
        """
        error_msg = "There are more than one patient in the selected" +\
        " folder:\n"
        patient_names = ' '.join(["\n" + str(self.file_name_list[name])
            for name in patient_error])
        error_msg += patient_names
        self.gui_object.show_error_msgs("Patient Error", error_msg)


if __name__ == '__main__':
    gui = MainGui()
    if len(gui.dirname.strip()) > 0:
        gui._input_gui()
        anonymizer_obj = Anonymize(gui)
        if not anonymizer_obj.file_name_list:
            anonymizer_obj.show_error_msgs("Dicom Files not Found",
                    "There are no DICOM files in the selected Folder")
        anonymizer_obj.main()

