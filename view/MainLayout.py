import sys

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout

from data.Strings import string_title
from view.HintsLayout import HintsLayout


def run_main_app() -> None:
    """
    Creates and runs the main application.
    """
    app: QApplication = QApplication([])

    # All top level widgets create a window
    window: QWidget = QWidget()
    window.setWindowTitle(string_title)
    window.setLayout(MainLayout())
    window.show()

    sys.exit(app.exec())


class MainLayout(QGridLayout):
    """
    The top-level layout.
    """

    def __init__(self):
        super().__init__()

        # Set up the layout that provides the hints
        self.__hints__ = HintsLayout()
        self.addLayout(self.__hints__, 0, 0)
