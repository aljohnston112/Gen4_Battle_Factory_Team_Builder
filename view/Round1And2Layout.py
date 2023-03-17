from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton

from data.Strings import string_opponents, string_confirm
from view.combo_boxes.PokemonComboBox import PokemonComboBox
from view_model.Round1And2ViewModel import Round1And2ViewModel


class Round1And2Layout(QWidget):
    """
    Allows the user to enter the hints given during round one and two of battle factory.
    """
    def __init__(self, team_use_case, is_round_2=False):
        super().__init__()
        num_pokemon = 2 if is_round_2 else 3
        self.__view_model__ = Round1And2ViewModel(team_use_case)
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel(string_opponents))
        self.pokemonComboBoxes = []
        for i in range(0, num_pokemon):
            self.pokemonComboBoxes.append(PokemonComboBox())
        for pokemonComboBox in self.pokemonComboBoxes:
            pokemonComboBox.currentTextChanged.connect(self.__text_changed__)
            layout.addWidget(pokemonComboBox)

    def set_up_button(self):
        button_confirm = QPushButton(string_confirm)
        self.addWidget(button_confirm, 1, 0)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)

    def __text_changed__(self):
        self.__view_model__.set_opponent_pokemon_names(self.__get_pokemon__())

    def __get_pokemon__(self):
        """
        Gets the data_class picked by the user.
        :return: The data_class picked by the user (maybe empty).
        """
        return [
            pokemonComboBox.currentText()
            for pokemonComboBox in self.pokemonComboBoxes
            if pokemonComboBox.currentText() != ""
        ]
