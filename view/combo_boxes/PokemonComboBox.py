from PyQt5.QtWidgets import QComboBox

from data_class.Pokemon import Pokemon
from repository.PokemonRepository import all_battle_factory_pokemon


class PokemonComboBox(QComboBox):
    """
    A combo box with a list of all Pokémon.
    """

    def text_changed(self, new_text):
        """
        Sets the current item of the combo box
        to the one containing the user's text.
        :param new_text: The text in the combo box.
        """
        self.setCurrentIndex(self.findText(new_text))

    def __add_all_pokemon_names__(self) -> None:
        name_set: set[str] = set()
        for pokemon in all_battle_factory_pokemon.values():
            pokemon: Pokemon
            name_set.add(pokemon.name)
        self.addItem("")
        for name in sorted(name_set):
            name: str
            self.addItem(name)

    def __init__(self):
        super().__init__()
        self.__add_all_pokemon_names__()
        self.currentTextChanged.connect(self.text_changed)
