from typing import List

from PyQt5.QtWidgets import QDialog, QGroupBox, QRadioButton, QLabel, QPushButton, QLayout, QVBoxLayout, QHBoxLayout

from data.Strings import string_pick, string_confirm
from data_class.Pokemon import Pokemon
from view.PokemonButton import PokemonButton


class PokemonPickerDialog(QDialog):
    """
    A dialog that asks the user to pick a pokemon.
    """

    def __init__(self, pokemon_names: List[str], callback_picked):
        super().__init__()
        self.callback_picked = callback_picked
        self.layout = QVBoxLayout()

        label_team = QLabel(string_pick)
        self.layout.addWidget(label_team)

        group_box_rb = QGroupBox()
        h_box_layout_pokemon = QHBoxLayout()
        self.push_buttons = []
        for name in pokemon_names:
            push_button = PokemonButton(name, self.confirm_clicked)
            h_box_layout_pokemon.addWidget(push_button)
            self.push_buttons.append(push_button)
        group_box_rb.setLayout(h_box_layout_pokemon)

        self.layout.addWidget(group_box_rb)

        self.setLayout(self.layout)

    def confirm_clicked(self, pokemon_name):
        self.callback_picked(pokemon_name)
        self.close()

