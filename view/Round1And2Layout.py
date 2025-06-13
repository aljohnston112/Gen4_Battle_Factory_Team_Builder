from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, \
    QSizePolicy, QGridLayout

from data.Strings import string_opponents, string_confirm
from use_case.PrintUseCase import PrintUseCase
from use_case.TeamUseCase import TeamUseCase
from view.LayoutUtil import add_expanding_spacer
from view.combo_boxes.PokemonComboBox import PokemonComboBox
from view_model.Round1And2ViewModel import Round1And2ViewModel


class Round1And2Layout(QWidget):
    """
    Allows the user to enter the hints given
    during round one and two of battle factory.
    """

    def __get_pokemon__(self):
        """
        Gets the Pokémon picked by the user.
        :return: The Pokémon picked by the user (maybe empty).
        """
        return [
            pokemonComboBox.currentText()
            for pokemonComboBox in self.__pokemon_combo_boxes__
            if pokemonComboBox.currentText() != ""
        ]

    def __text_changed__(self):
        self.__view_model__.set_opponent_pokemon_names(self.__get_pokemon__())

    def __init__(
            self,
            team_use_case: TeamUseCase,
            print_use_case: PrintUseCase,
            is_round_2: bool,
            level: int
    ) -> None:
        super().__init__()
        self.__view_model__: Round1And2ViewModel = Round1And2ViewModel(
            team_use_case=team_use_case,
            print_use_case=print_use_case,
            is_round_2=is_round_2,
            level=level
        )

        layout: QGridLayout = QGridLayout()
        self.setLayout(layout)
        add_expanding_spacer(grid_layout=layout, row=0, column=0)
        layout.addWidget(QLabel(string_opponents), 0, 1)
        add_expanding_spacer(grid_layout=layout, row=0, column=2)


        column: int = 3
        num_pokemon: int = 2 if is_round_2 else 3
        self.__pokemon_combo_boxes__: list[PokemonComboBox] = []
        for i in range(num_pokemon):
            i: int
            combo_box: PokemonComboBox = PokemonComboBox()
            combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            combo_box.currentTextChanged.connect(self.__text_changed__)
            self.__pokemon_combo_boxes__.append(combo_box)
            layout.addWidget(combo_box, 0, column)
            column += 1
            add_expanding_spacer(grid_layout=layout, row=0, column=column)
            column += 1

        button_confirm: QPushButton = QPushButton(string_confirm)
        if is_round_2:
            # row, column, row_span, column_span
            layout.addWidget(button_confirm, 1, 1, 1, 5)
        else:
            layout.addWidget(button_confirm, 1, 1, 1, 7)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)
