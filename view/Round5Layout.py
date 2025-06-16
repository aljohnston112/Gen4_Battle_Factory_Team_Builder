from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout

from data.Strings import string_type, string_confirm
from use_case.PrintUseCase import PrintUseCase
from use_case.RoundUseCase import RoundUseCase
from use_case.TeamUseCase import TeamUseCase
from view.LayoutUtil import add_expanding_spacer
from view.combo_boxes.PokemonTypeComboBox import PokemonTypeComboBox
from view_model.Round5ViewModel import Round5ViewModel


class Round5Layout(QWidget):
    """
    Allows the user to enter hints for round five of the battle factory
    """

    def __init__(
            self,
            team_use_case: TeamUseCase,
            print_use_case: PrintUseCase,
            round_use_case: RoundUseCase,
            level: int
    ) -> None:
        super().__init__()
        self.__view_model__: Round5ViewModel = Round5ViewModel(
            team_use_case=team_use_case,
            print_use_case=print_use_case,
            current_round_use_case=round_use_case,
            level=level
        )
        layout: QGridLayout = QGridLayout()
        self.setLayout(layout)

        # Most common type
        add_expanding_spacer(grid_layout=layout, row=0, column=0)
        label_type: QLabel = QLabel(string_type)
        # row, column
        layout.addWidget(label_type, 0, 1)
        add_expanding_spacer(grid_layout=layout, row=0, column=2)

        pokemon_type: PokemonTypeComboBox = PokemonTypeComboBox()
        pokemon_type.currentTextChanged.connect(
            self.__view_model__.set_pokemon_type
        )
        # row, column
        layout.addWidget(pokemon_type, 0, 3)
        add_expanding_spacer(grid_layout=layout, row=0, column=4)

        button_confirm = QPushButton(string_confirm)
        # row, column, row_span, column_span
        layout.addWidget(button_confirm, 1, 1, 1, 3)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)
