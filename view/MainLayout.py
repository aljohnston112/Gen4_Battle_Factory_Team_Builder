import sys

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLayout

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


class BattleResultLoader(QThread):
    """
    A thread that loads the battle results.
    """
    def run(self):
        """
        Loads the battle results.
        """
        load_pokemon_ranks_accuracy()
        load_pokemon_ranks()


class MainLayout(QGridLayout):
    """
    The top-level layout.
    """

    def __init__(self, level: int):
        """
        :param level: (int): The level of the battle factory Pokémon.
        """
        super().__init__()

        # Load the battle results in the background
        self.thread = BattleResultLoader()
        self.thread.start()

        self.__hints__: QLayout = HintsLayout(level=level)
        # row, column
        self.addLayout(self.__hints__, 0, 0)
