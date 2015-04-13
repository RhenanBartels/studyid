import unittest

from os.path import join

import dicom

from dicom.errors import InvalidDicomError

from .. studyid.anonymizer import MainGui
from .. studyid.anonymizer import Anonymize

GUI_OBJECT = MainGui()

class TestAnonymize(unittest.TestCase):
    def test_open_dicom(self):
        anonymize_object = Anonymize(GUI_OBJECT)
        path = anonymize_object.folder_path
        file_list = anonymize_object.file_name_list
        try:
            dicom_list = [dicom.read_file(join(path, file_name)) for
                    file_name in file_list]
            self.assertItemsEqual(anonymize_object._open_dicom_files(),
                    dicom_list)
        except InvalidDicomError:
            pass

    def test_check_one_patient_error(self):
        anonymize_object = Anonymize(GUI_OBJECT)
        dicom_list = anonymize_object._open_dicom_files()
        file_error_error = [2, 3, 4, 5]
        file_error_ok = []
        #Choose correct folder
        if GUI_OBJECT.dirname.split("/")[-1] == "Test_dicom":
            self.assertItemsEqual(anonymize_object._check_patient(dicom_list),
                                  file_error_ok)
        #Choose folder with more than one patient
        elif GUI_OBJECT.dirname.split("/")[-1] == "Test_dicom_error":
            self.assertItemsEqual(anonymize_object._check_patient(dicom_list),
                                  file_error_error)
        #Choose folder without DICOM files.
        else:
            self.assertIsNone(anonymize_object._check_patient(dicom_list))

    def test_wrong_dicom_file(self):
        anonymize_object = Anonymize(GUI_OBJECT)
        self.assertRaises(InvalidDicomError,
                anonymize_object._open_dicom_files())


    def test_anonymizer(self):
        anonymize_object = Anonymize(GUI_OBJECT)
        anonymize_object.anonymize()

