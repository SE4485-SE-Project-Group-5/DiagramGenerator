import sys
import os

BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS  # pylint: disable=no-member
