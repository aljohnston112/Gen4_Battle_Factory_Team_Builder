from typing import List

from PyQt5.QtWidgets import QDialog, QGroupBox, QRadioButton, QLabel, QPushButton, QLayout

from data.Strings import string_pick, string_confirm
from data_class.Pokemon import Pokemon

class PokemonPickerLayout(QLayout):
    pass


class PokemonPickerDialog(QDialog):

    def __init__(self, pokemon: List[Pokemon]):
        super().__init__()
        label_team = QLabel(string_pick)
        self.addWidget(label_team)
        group_box_rb = QGroupBox()
        self.radio_buttons = []
        for poke in pokemon:
            self.radio_buttons.append(QRadioButton(poke.name))
        self.addWidget(group_box_rb)
        button_confirm = QPushButton(string_confirm)
        self.addWidget(button_confirm)
        button_confirm.clicked.connect(self.confirm_clicked)
        self.setLayout()

    def confirm_clicked(self):
        pass
