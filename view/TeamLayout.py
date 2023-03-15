from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QGridLayout, QCheckBox

from data.Strings import string_first_battle, string_team, string_choices
from use_case.PokemonUseCase import PokemonUseCase
from view.PokemonAndMoveLayout import PokemonAndMoveLayout
from view_model.TeamViewmodel import TeamViewModel


class TeamLayout(QGridLayout):
    """
    Two rows of six data_class and move layouts.
    One for the user's team, and another for choices
    unless it is the first round
    in which case all six are the user's choices.
    """

    def __init__(self, team_use_case):
        super().__init__()
        pokemon_use_cases = [
            PokemonUseCase(),
            PokemonUseCase(),
            PokemonUseCase(),
            PokemonUseCase(),
            PokemonUseCase(),
            PokemonUseCase()
        ]
        self.__view_model__ = TeamViewModel(
            team_use_case,
            pokemon_use_cases
        )

        # Add first battle checkbox
        first_battle_check_box = QCheckBox(string_first_battle)
        first_battle_check_box.setChecked(True)
        first_battle_check_box.stateChanged.connect(self.check_box_first_battle_state_changed)
        self.addWidget(first_battle_check_box, 3, 0)

        # [0:3] are the team data_class; [3:6] are the choices.
        # If it is the first battle, all are choices.
        self.pokemon = []
        # Add team layout
        team = QHBoxLayout()
        label_team = QLabel(string_team)
        self.addWidget(label_team, 1, 0, alignment=Qt.AlignTop)
        for i in range(0, 3):
            self.pokemon.append(PokemonAndMoveLayout(pokemon_use_cases[i], self.__on_new_data__))
            team.addWidget(self.pokemon[i])
        self.addLayout(team, 1, 1)

        # Add choices layout
        choices = QHBoxLayout()
        self.label_choices = QLabel(string_choices)
        self.label_choices.setVisible(False)
        self.addWidget(self.label_choices, 2, 0, alignment=Qt.AlignTop)
        for i in range(3, 6):
            self.pokemon.append(PokemonAndMoveLayout(pokemon_use_cases[i], self.__on_new_data__))
            choices.addWidget(self.pokemon[i])
        self.addLayout(choices, 2, 1)

    def check_box_first_battle_state_changed(self, state: Qt.CheckState):
        """
        For when the state of the first round check box is changed.
        Changes whether the first row of three data_class is considered team or choices.
        :param state: The old state of the checkbox.
        """
        if state != Qt.CheckState.Checked:
            self.label_choices.setVisible(True)
            self.__is_first_battle__(False)
        else:
            self.label_choices.setVisible(False)
            self.__is_first_battle__(True)

    def __is_first_battle__(self, is_first_battle):
        self.__view_model__.is_first_battle(is_first_battle)

    def __on_new_data__(self):
        self.__view_model__.on_new_data()
