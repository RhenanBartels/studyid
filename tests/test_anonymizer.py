
import unittest
from .. studyid.anonymizer import MainGui

class TestGui(unittest.TestCase):
    def test_open_dialog_box(self):
        dir_name = '/Users/lep/Dropbox'
        gui_object = MainGui()
        self.assertEqual(gui_object.dirname, dir_name)

