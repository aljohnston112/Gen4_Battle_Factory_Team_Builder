from typing import List

from PyQt5.QtWidgets import QDialog, QGroupBox, QRadioButton, QLabel, QPushButton, QLayout, QVBoxLayout

from data.Strings import string_pick, string_confirm
from data_class.Pokemon import Pokemon


class PokemonPickerDialog(QDialog):
    """
    A dialog that asks the user to pick a pokemon.
    """

    def __init__(self, pokemon: List[Pokemon]):
        super().__init__()
        self.layout = QVBoxLayout()
        label_team = QLabel(string_pick)
        self.layout.addWidget(label_team)

        group_box_rb = QGroupBox()
        self.radio_buttons = []
        for poke in pokemon:
            self.radio_buttons.append(QRadioButton(poke.name))
        self.layout.addWidget(group_box_rb)

        button_confirm = QPushButton(string_confirm)
        self.layout.addWidget(button_confirm)
        button_confirm.clicked.connect(self.confirm_clicked)

        self.setLayout(self.layout)

    def confirm_clicked(self):
        self.done(QDialog.Accepted)

