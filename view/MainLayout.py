import sys

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout

from data.Strings import string_title
from view.HintsLayout import HintsLayout
from view_model.MainViewModel import MainViewModel


def run_main_app() -> None:
    """
    Creates and runs the main application.
    """
    app = QApplication([])
    create_main_window()
    sys.exit(app.exec())


def create_main_window() -> None:
    """
    Creates the main window of the app.
    """

    # All top level widgets create a window
    window = QWidget()
    window.setWindowTitle(string_title)
    window.setLayout(MainLayout())
    window.show()


class MainLayout(QGridLayout):
    """
    The top-level layout.
    """

    def __init__(self):
        super().__init__()

        self.__view_model__ = MainViewModel()

        # Set up the layout that provides the hints
        self.__hints__ = HintsLayout()
        self.addLayout(self.__hints__, 0, 0)
