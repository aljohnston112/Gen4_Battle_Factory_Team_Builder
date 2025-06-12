import sys

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout

from algorithm.FrontierTeamBuilder import load_pokemon_ranks_accuracy, \
    load_pokemon_ranks
from data.Strings import string_title
from view.HintsLayout import HintsLayout

__LEVEL__ = 50
"""
The level of the battle factory Pokemon.
"""


def run_main_app() -> None:
    """
    Creates and runs the main application.
    """
    app: QApplication = QApplication([])

    # All top-level widgets create a window
    window: QWidget = QWidget()
    window.setWindowTitle(string_title)
    window.setLayout(MainLayout(__LEVEL__))
    window.show()

    sys.exit(app.exec())


class MainLayout(QGridLayout):
    """
    The top-level layout.
    """

    def __init__(self, level: int):
        super().__init__()

        class WorkerThread(QThread):

            def run(self):
                load_pokemon_ranks_accuracy()
                load_pokemon_ranks()

        self.thread = WorkerThread()
        self.thread.start()

        self.__hints__ = HintsLayout(level=level)
        # row, column
        self.addLayout(self.__hints__, 0, 0)
