import unittest
from .. studyid.anonymizer import MainGui
from .. studyid.anonymizer import Anonymize

NAME_PATTERN = 'IM-0001-000'
GUI_OBJECT = MainGui()
OUTPUT_DIRNAME = GUI_OBJECT.dirname

class TestGui(unittest.TestCase):
    def test_open_dialog_box_ok(self):
        dir_name = '/Users/lep/Dropbox/Python/Test_dicom'
        if OUTPUT_DIRNAME.strip():
            self.assertEqual(OUTPUT_DIRNAME, dir_name)

    def test_file_list_generator(self):
        file_names = [NAME_PATTERN + str(value) +
                ".dcm" for value in range(4, 10)]
        if OUTPUT_DIRNAME.strip():
            self.assertItemsEqual(GUI_OBJECT._list_dir(), file_names)

    def test_input_gui(self):
        if OUTPUT_DIRNAME.strip():
            GUI_OBJECT._input_gui()

class TestId(unittest.TestCase):
    def test_check_input_1(self):
        input_id = "12345678"
        self.assertTrue(GUI_OBJECT._check_input(input_id))

    def test_check_input_2(self):
        input_id = "123-45678"
        self.assertFalse(GUI_OBJECT._check_input(input_id))

    def test_check_input_3(self):
        input_id = "123456789"
        self.assertFalse(GUI_OBJECT._check_input(input_id))

    def test_check_input_4(self):
        input_id = "Whatever plus"
        self.assertFalse(GUI_OBJECT._check_input(input_id))
