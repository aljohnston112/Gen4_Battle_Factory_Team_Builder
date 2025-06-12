from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, \
    QSizePolicy, QGridLayout, QSpacerItem

from data.Strings import string_opponents, string_confirm
from use_case.PrintUseCase import PrintUseCase
from use_case.TeamUseCase import TeamUseCase
from view.combo_boxes.PokemonComboBox import PokemonComboBox
from view_model.Round1And2ViewModel import Round1And2ViewModel


class Round1And2Layout(QWidget):
    """
    Allows the user to enter the hints given during round one and two of battle factory.
    """

    def __init__(
            self,
            team_use_case: TeamUseCase,
            print_use_case: PrintUseCase,
            is_round_2: bool,
            level: int
    ):
        super().__init__()
        num_pokemon = 2 if is_round_2 else 3
        self.__view_model__ = Round1And2ViewModel(
            team_use_case=team_use_case,
            print_use_case=print_use_case,
            is_round_2=is_round_2,
            level=level
        )

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            0
        )
        layout.addWidget(QLabel(string_opponents), 0, 1)
        layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            2
        )

        self.pokemonComboBoxes = []

        col = 3
        for i in range(num_pokemon):
            combo = PokemonComboBox()
            combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            combo.currentTextChanged.connect(self.__text_changed__)
            self.pokemonComboBoxes.append(combo)
            layout.addWidget(combo, 0, col)
            col += 1
            if i < num_pokemon - 1:
                layout.addItem(
                    QSpacerItem(
                        0,
                        0,
                        QSizePolicy.Expanding,
                        QSizePolicy.Minimum
                    ),
                    0,
                    col
                )
                col += 1
        layout.addItem(
            QSpacerItem(
                0,
                0,
                QSizePolicy.Expanding,
                QSizePolicy.Minimum
            ),
            0,
            col
        )

        button_confirm = QPushButton(string_confirm)
        if is_round_2:
            layout.addWidget(button_confirm, 1, 1, 1, 5)
        else:
            layout.addWidget(button_confirm, 1, 1, 1, 7)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)

    def __text_changed__(self):
        self.__view_model__.set_opponent_pokemon_names(self.__get_pokemon__())

    def __get_pokemon__(self):
        """
        Gets the Pokémon picked by the user.
        :return: The Pokémon picked by the user (maybe empty).
        """
        return [
            pokemonComboBox.currentText()
            for pokemonComboBox in self.pokemonComboBoxes
            if pokemonComboBox.currentText() != ""
        ]
