import unittest

from os.path import join

import dicom

from .. studyid.anonymizer import MainGui
from .. studyid.anonymizer import Anonymize

GUI_OBJECT = MainGui()

class TestAnonymize(unittest.TestCase):
    def test_open_dicom(self):
        file_list = GUI_OBJECT._list_dir()
        folder_path = GUI_OBJECT.dirname
        anonymize_object = Anonymize(folder_path, file_list)


