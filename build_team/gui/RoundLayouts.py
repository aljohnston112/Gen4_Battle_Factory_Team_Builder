from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from build_team.gui.ComboBoxes import PokemonComboBox, MoveComboBox, TypeComboBox, PokemonMoveComboBox
from build_team.Strings import string_opponents, string_name, string_move, string_type


class Round1And2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        label_names = QLabel(string_opponents)
        layout.addWidget(label_names)
        self.pokemon1 = PokemonComboBox()
        self.pokemon2 = PokemonComboBox()
        self.pokemon3 = PokemonComboBox()
        layout.addWidget(self.pokemon1)
        layout.addWidget(self.pokemon2)
        layout.addWidget(self.pokemon3)

    def get_pokemon(self):
        return [
            self.pokemon1.currentText(),
            self.pokemon2.currentText(),
            self.pokemon3.currentText(),
        ]


class Round3(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        label_name = QLabel(string_name)
        layout.addWidget(label_name)
        pokemon_combo_box = PokemonComboBox()
        layout.addWidget(pokemon_combo_box)
        label_move = QLabel(string_move)
        layout.addWidget(label_move)
        move = MoveComboBox()
        layout.addWidget(move)


class Round4(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        label_move = QLabel(string_move)
        layout.addWidget(label_move)
        move = MoveComboBox()
        layout.addWidget(move)


class Round5(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        label_type = QLabel(string_type)
        layout.addWidget(label_type)
        move = TypeComboBox()
        layout.addWidget(move)
