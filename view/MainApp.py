import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout

from data.Strings import string_confirm
from use_case.CurrentRoundUseCase import CurrentRoundUseCase, Round
from use_case.Round1And2UseCase import Round1And2UseCase

from use_case.TeamUseCase import TeamUseCase
from view.HintsLayout import HintsLayout
from view_model.MainViewModel import MainViewModel


def main_app():
    """
    Creates the main application.
    """
    app = QApplication([])

    window = QWidget()
    window.setWindowTitle("Gen4 Team Builder")
    window.setLayout(MainApp())
    window.show()

    sys.exit(app.exec())


class MainApp(QGridLayout):
    """
    The main application.
    """

    def __init__(self):
        super().__init__()

        self.__view_model__ = MainViewModel()
        self.__current_round_use_case__ = CurrentRoundUseCase()
        self.__round_1_and_2_use_case__ = Round1And2UseCase()
        self.__team_use_case__ = TeamUseCase([], [])
        self.__hints__ = HintsLayout(
            self.__current_round_use_case__,
            self.__round_1_and_2_use_case__,
            self.__team_use_case__
        )
        self.addLayout(self.__hints__, 0, 0)
        self.set_up_button()

    def set_up_button(self):
        button_confirm = QPushButton(string_confirm)
        self.addWidget(button_confirm, 1, 0)
        button_confirm.clicked.connect(self.confirm_clicked)

    def confirm_clicked(self):
        match self.__current_round_use_case__.get_current_round():
            case Round.ONE:
                self.__view_model__.confirm_clicked_round_one(
                    self.__team_use_case__.get_team_pokemon(),
                    self.__team_use_case__.get_choice_pokemon(),
                    self.__round_1_and_2_use_case__.get_opponent_pokemon()
                )
            case Round.TWO:
                self.__view_model__.confirm_clicked_round_two(
                    self.__team_use_case__.get_team_pokemon(),
                    self.__team_use_case__.get_choice_pokemon(),
                    self.__round_1_and_2_use_case__.get_opponent_pokemon()
                )
