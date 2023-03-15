from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from data.Strings import string_name, string_move
from view.combo_boxes.MoveComboBox import MoveComboBox
from view.combo_boxes.PokemonComboBox import PokemonComboBox


class Round3Layout(QWidget):
    """
    Allows the user to enter hints for round three of battle factory
    """
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        # One names
        label_name = QLabel(string_name)
        layout.addWidget(label_name)
        pokemon_combo_box = PokemonComboBox()
        pokemon_combo_box.currentTextChanged.connect(self.text_changed)
        layout.addWidget(pokemon_combo_box)
        self.pokemonComboBox = pokemon_combo_box

        # One move
        label_move = QLabel(string_move)
        layout.addWidget(label_move)
        move = MoveComboBox()
        layout.addWidget(move)
        self.moveComboBox = move

    def text_changed(self):
        self.round_three_use_case.set_pokemon_name_and_move(self.get_pokemon(), self.get_move())

    def get_pokemon(self):
        return self.pokemonComboBox.currentText()

    def get_move(self):
        return self.moveComboBox.currentText()