import sys

from PyQt5.QtCore import QThread, QObject, QEvent, pyqtSignal
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

    window.thread = QThread()
    window.worker = BattleResultLoader()
    window.worker.moveToThread(window.thread)
    window.thread.started.connect(window.worker.run)
    window.worker.finished.connect(window.thread.quit)
    window.worker.finished.connect(window.worker.deleteLater)
    window.thread.finished.connect(window.thread.deleteLater)
    window.thread.start()

    opponent_battle_result_window: QWidget = QWidget()
    opponent_battle_result_window.setWindowTitle(string_title)
    opponent_battle_result_window.setLayout(
        OpponentBattleResultLayout(
            round_use_case=round_use_case,
            team_use_case=team_use_case
        )
    )
    opponent_battle_result_window.show()

    class WindowCloseFilter(QObject):
        def __init__(self, target_window):
            super().__init__()
            self.target_window = target_window

        def eventFilter(self, watched, event):
            if event.type() == QEvent.Close:
                self.target_window.close()
            return False

    filter1 = WindowCloseFilter(opponent_battle_result_window)
    window.installEventFilter(filter1)

    filter2 = WindowCloseFilter(window)
    opponent_battle_result_window.installEventFilter(filter2)

    sys.exit(app.exec())


class BattleResultLoader(QObject):
    """
    A thread that loads the battle results.
    """
    finished = pyqtSignal()

    def run(self):
        """
        Loads the battle results.
        """
        load_pokemon_ranks_accuracy()
        load_pokemon_ranks()
        self.finished.emit()


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
