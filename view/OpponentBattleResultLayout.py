from PyQt5.QtWidgets import QGridLayout, QSizePolicy, \
    QPushButton

from data.Strings import string_confirm
from use_case.PokemonUseCase import PokemonUseCase
from use_case.PrintUseCase import PrintUseCase
from use_case.RoundUseCase import RoundUseCase
from use_case.TeamUseCase import TeamUseCase
from view.DualTextOutputWidget import DualTextOutputWidget
from view.LayoutUtil import add_expanding_spacer
from view.PokemonAndMoveLayout import PokemonAndMoveLayout
from view_model.OpponentBattleResultViewModel import \
    OpponentBattleResultViewModel


class OpponentBattleResultLayout(QGridLayout):

    def __init__(
            self,
            round_use_case: RoundUseCase,
            team_use_case: TeamUseCase,
    ):
        super().__init__()

        pokemon_use_cases: list[PokemonUseCase] = [
            PokemonUseCase() for _ in range(3)
        ]

        # Add opponent Pokémon and move selection boxes
        self.__pokemon__: list[PokemonAndMoveLayout] = []
        add_expanding_spacer(
            grid_layout=self,
            row=0,
            column=0
        )
        for i in range(0, 3):
            self.__pokemon__.append(
                PokemonAndMoveLayout(
                    pokemon_use_case=pokemon_use_cases[i],
                    round_use_case=round_use_case,
                    on_new_data=None,
                    is_player=False
                )
            )
            combo_box: PokemonAndMoveLayout = self.__pokemon__[i]
            combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.addWidget(combo_box, 0, (i * 2) + 1)
            add_expanding_spacer(
                grid_layout=self,
                row=0,
                column=(i * 2) + 2
            )

        self.__text_output_widget__ = DualTextOutputWidget()
        self.__print_use_case__: PrintUseCase = \
            PrintUseCase(self.__text_output_widget__)
        # row, column
        self.addWidget(self.__text_output_widget__, 2, 0, 1, 7)

        self.__view_model__: OpponentBattleResultViewModel = \
            OpponentBattleResultViewModel(
                round_use_case=round_use_case,
                team_use_case=team_use_case,
                pokemon_use_cases=pokemon_use_cases,
                print_use_case=self.__print_use_case__
            )

        button_confirm: QPushButton = QPushButton(string_confirm)
        self.addWidget(button_confirm, 1, 1, 1, 5)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)
