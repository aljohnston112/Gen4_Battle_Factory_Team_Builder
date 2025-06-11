from PyQt5.QtWidgets import QLabel, QHBoxLayout, QGridLayout, QGroupBox, \
    QRadioButton, QSpacerItem, QSizePolicy

from data.Strings import string_last_battle, string_team, string_first_battle, \
    string_middle_battle, string_choices
from use_case.PokemonUseCase import PokemonUseCase
from use_case.TeamUseCase import TeamUseCase
from view.PokemonAndMoveLayout import PokemonAndMoveLayout
from view_model.TeamViewmodel import TeamViewModel, RoundStage


class TeamLayout(QGridLayout):
    """
    Two rows of six data_class and move layouts.
    One for the user's team, and another for choices
    unless it is the first round,
    in which case all six are the user's choices.
    """

    def __battle_changed__(self, battle_type: RoundStage) -> None:
        self.__view_model__.set_round_stage(battle_type)
        if battle_type != RoundStage.FIRST_BATTLE:
            self.label_choices.show()
        else:
            self.label_choices.hide()

    def __new_battle_checked__(self, checked) -> None:
        if not checked:
            return
        for i in range(len(self.radio_buttons_rounds)):
            if self.radio_buttons_rounds[i].isChecked():
                self.__battle_changed__(RoundStage(i))
                break

    def __set_up_round_radio_buttons__(self) -> None:
        """
        Sets up the radio buttons used to pick the round number.
        """
        self.radio_buttons_rounds: list[QRadioButton] = [
            QRadioButton(string)
            for string in
            [string_first_battle, string_middle_battle, string_last_battle]
        ]

        h_box_layout_rounds: QHBoxLayout = QHBoxLayout()
        for radio_button in self.radio_buttons_rounds:
            radio_button: QRadioButton
            h_box_layout_rounds.addWidget(radio_button)
            radio_button.toggled.connect(self.__new_battle_checked__)

        group_box_rb: QGroupBox = QGroupBox()
        group_box_rb.setLayout(h_box_layout_rounds)
        self.addWidget(group_box_rb, 3, 1, 1, 7)
        # Set the default round to 1
        self.radio_buttons_rounds[0].click()

    def __on_new_data__(self) -> None:
        self.__view_model__.on_new_data()

    def __init__(self, team_use_case: TeamUseCase):
        super().__init__()
        pokemon_use_cases: list[PokemonUseCase] = [
            PokemonUseCase() for _ in range(6)
        ]
        self.__view_model__: TeamViewModel = TeamViewModel(
            team_use_case=team_use_case,
            pokemon_use_cases=pokemon_use_cases
        )

        # Team label
        first_row: int = 0
        self.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            first_row,
            0
        )
        label_team: QLabel = QLabel(string_team)
        self.addWidget(label_team, 0, 1)
        self.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            first_row,
            2
        )

        # Add team Pokémon and move selection boxes
        # [0:3] are the team Pokémon
        self.pokemon: list[PokemonAndMoveLayout] = []
        for i in range(0, 3):
            self.pokemon.append(
                PokemonAndMoveLayout(
                    pokemon_use_case=pokemon_use_cases[i],
                    on_new_data=self.__on_new_data__
                )
            )
            column: int = 2 * i + 3
            self.addWidget(self.pokemon[i], 0, column)
            self.addItem(
                QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
                first_row,
                column + 1
            )

        # Choices label
        second_row: int = 1
        self.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            second_row,
            0
        )
        self.label_choices: QLabel = QLabel(string_choices)
        self.addWidget(self.label_choices, 1, 1)
        # Hidden for the first battle
        self.label_choices.hide()
        self.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            second_row,
            2
        )

        # Add choice Pokémon and move selection boxes
        # [3:6] are the choice Pokémon.
        for i in range(3, 6):
            self.pokemon.append(
                PokemonAndMoveLayout(
                    pokemon_use_case=pokemon_use_cases[i],
                    on_new_data=self.__on_new_data__
                )
            )
            column = 2 * (i - 3) + 3
            self.addWidget(self.pokemon[i], second_row, column)
            self.addItem(
                QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
                second_row,
                column + 1
            )
        self.__set_up_round_radio_buttons__()
