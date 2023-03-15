from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from data.Strings import string_type
from view.combo_boxes.PokemonTypeComboBox import PokemonTypeComboBox


class Round5Layout(QWidget):
    """
    Allows the user to enter hints for round five of battle factory
    """
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Most common type
        label_type = QLabel(string_type)
        layout.addWidget(label_type)
        pokemon_type = PokemonTypeComboBox()
        layout.addWidget(pokemon_type)
