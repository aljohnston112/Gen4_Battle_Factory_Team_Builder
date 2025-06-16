from PyQt5.QtWidgets import QLabel, QHBoxLayout, QGridLayout, QGroupBox, \
    QRadioButton

from data.Strings import string_last_battle, string_team, string_first_battle, \
    string_middle_battle, string_choices
from data_class.Pokemon import Pokemon
from use_case.PokemonUseCase import PokemonUseCase
from use_case.RoundUseCase import RoundUseCase, RoundStage
from use_case.TeamUseCase import TeamUseCase
from view.LayoutUtil import add_expanding_spacer
from view.PokemonAndMoveLayout import PokemonAndMoveLayout
from view_model.TeamViewmodel import TeamViewModel


class TeamLayout(QGridLayout):
    """
    Two rows of six Pokémon and move combo boxes.
    One row is for the user's team, and the other for the user's choices,
    but if it is the first round, both rows are the user's choices.
    """

    def __battle_changed__(self, battle_type: RoundStage) -> None:
        self.__view_model__.set_round_stage(battle_type)
        if battle_type != RoundStage.FIRST_BATTLE:
            self.__label_choices__.show()
        else:
            self.__label_choices__.hide()

    def __new_battle_checked__(self, checked: bool) -> None:
        if not checked:
            return
        for i in range(len(self.__radio_buttons_rounds__)):
            if self.__radio_buttons_rounds__[i].isChecked():
                self.__battle_changed__(RoundStage(i))
                break

    def __set_up_round_stage_radio_buttons__(self) -> None:
        """
        Sets up the radio buttons used to pick the round number.
        """
        self.__radio_buttons_rounds__: list[QRadioButton] = [
            QRadioButton(string)
            for string in
            [string_first_battle, string_middle_battle, string_last_battle]
        ]

        h_box_layout_rounds: QHBoxLayout = QHBoxLayout()
        for radio_button in self.__radio_buttons_rounds__:
            radio_button: QRadioButton
            h_box_layout_rounds.addWidget(radio_button)
            radio_button.toggled.connect(self.__new_battle_checked__)

        group_box_rb: QGroupBox = QGroupBox()
        group_box_rb.setLayout(h_box_layout_rounds)
        # row, column, row_span, column_span
        self.addWidget(group_box_rb, 3, 1, 1, 7)
        # Set the default round to 1
        self.__radio_buttons_rounds__[0].click()

    def user_traded(
            self,
            pokemon_traded_away: Pokemon,
            pokemon_traded_for: Pokemon
    ):
        for pokemon_box in self.__pokemon__[:3]:
            pokemon_box: PokemonAndMoveLayout
            poke: str = pokemon_box.get_selected_pokemon()
            if poke == pokemon_traded_away.name:
                pokemon_box.set_selected_pokemon(pokemon_traded_for.name)

    def __init__(
            self,
            team_use_case: TeamUseCase,
            round_case_case: RoundUseCase
    ) -> None:
        super().__init__()
        pokemon_use_cases: list[PokemonUseCase] = [
            PokemonUseCase() for _ in range(6)
        ]
        self.__view_model__: TeamViewModel = TeamViewModel(
            team_use_case=team_use_case,
            round_use_case=round_case_case,
            pokemon_use_cases=pokemon_use_cases
        )

        # Team label
        first_row: int = 0
        add_expanding_spacer(grid_layout=self, row=first_row, column=0)
        label_team: QLabel = QLabel(string_team)
        self.addWidget(label_team, first_row, 1)
        add_expanding_spacer(grid_layout=self, row=first_row, column=2)

        # Add team Pokémon and move selection boxes
        # [0:3] are the team Pokémon
        self.__pokemon__: list[PokemonAndMoveLayout] = []
        for i in range(0, 3):
            self.__pokemon__.append(
                PokemonAndMoveLayout(
                    pokemon_use_case=pokemon_use_cases[i],
                    round_use_case=round_case_case,
                    on_new_data=self.__view_model__.on_new_data,
                    is_player=True
                )
            )
            column: int = 2 * i + 3
            self.addWidget(self.__pokemon__[i], first_row, column)
            add_expanding_spacer(
                grid_layout=self,
                row=first_row,
                column=column + 1
            )

        # Choices label
        second_row: int = 1
        add_expanding_spacer(grid_layout=self, row=second_row, column=0)
        self.__label_choices__: QLabel = QLabel(string_choices)
        self.addWidget(self.__label_choices__, second_row, 1)
        # Hidden for the first battle
        self.__label_choices__.hide()
        add_expanding_spacer(grid_layout=self, row=second_row, column=2)

        # Add choice Pokémon and move selection boxes
        # [3:6] are the choice Pokémon.
        for i in range(3, 6):
            self.__pokemon__.append(
                PokemonAndMoveLayout(
                    pokemon_use_case=pokemon_use_cases[i],
                    round_use_case=round_case_case,
                    on_new_data=self.__view_model__.on_new_data,
                    is_player=True
                )
            )
            column: int = 2 * (i - 3) + 3
            self.addWidget(self.__pokemon__[i], second_row, column)
            add_expanding_spacer(
                grid_layout=self,
                row=second_row,
                column=column + 1
            )
        self.__set_up_round_stage_radio_buttons__()
        team_use_case.add_trade_listener(self.user_traded)
