from PyQt5.QtWidgets import QComboBox, QWidget, QVBoxLayout

from data_class.Type import pokemon_types


class PokemonTypeComboBox(QComboBox):
    """
    A QComboBox containing all data_class types
    """
    def __init__(self):
        super().__init__()
        self.addItem("")
        for pokemon_type in pokemon_types:
            self.addItem(pokemon_type.name)
