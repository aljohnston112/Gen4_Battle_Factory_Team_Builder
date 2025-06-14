import sys

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLayout

from algorithm.FrontierTeamBuilder import load_pokemon_ranks_accuracy, \
    load_pokemon_ranks
from data.Strings import string_title
from use_case.RoundUseCase import RoundUseCase
from use_case.TeamUseCase import TeamUseCase
from view.HintsLayout import HintsLayout

__LEVEL__ = 50

from view.OpponentBattleResultLayout import OpponentBattleResultLayout

"""
The level of the battle factory Pokemon.
"""


def run_main_app() -> None:
    """
    Creates and runs the main application.
    """
    app: QApplication = QApplication([])

    team_use_case: TeamUseCase = TeamUseCase(
        team_pokemon=[],
        choice_pokemon=[]
    )
    round_use_case: RoundUseCase = RoundUseCase()

    # All top-level widgets create a window
    window: QWidget = QWidget()
    window.setWindowTitle(string_title)
    window.setLayout(
        MainLayout(
            level=__LEVEL__,
            round_use_case=round_use_case,
            team_use_case=team_use_case
        )
    )
    window.show()

    opponent_battle_result_window: QWidget = QWidget()
    opponent_battle_result_window.setWindowTitle(string_title)
    opponent_battle_result_window.setLayout(
        OpponentBattleResultLayout(
            round_use_case=round_use_case,
            team_use_case=team_use_case
        )
    )
    opponent_battle_result_window.show()

    # Load the battle results in the background
    window.thread = BattleResultLoader()
    window.thread.start()

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

    def __init__(
            self,
            level: int,
            round_use_case: RoundUseCase,
            team_use_case: TeamUseCase
    ) -> None:
        """
        :param level: (int): The level of the battle factory Pokémon.
        """
        super().__init__()

        self.__hints__: QLayout = HintsLayout(
            level=level,
            round_use_case=round_use_case,
            team_use_case=team_use_case
        )
        # row, column
        self.addLayout(self.__hints__, 0, 0)
