from PyQt5.QtWidgets import QComboBox

from repository.PokemonRepository import all_battle_factory_pokemon


class PokemonComboBox(QComboBox):
    """
    A combo box with a list of all data_class
    """
    def __init__(self):
        super().__init__()

        # No data_class has this string of letters in their name
        name_set = set()
        for pokemon_key in all_battle_factory_pokemon.keys():
            pokemon_name = all_battle_factory_pokemon[pokemon_key].name
            name_set.add(pokemon_name)

        self.addItem("")
        for name in sorted(name_set):
            self.addItem(name)

        self.currentTextChanged.connect(self.text_changed)

    def text_changed(self, new_text):
        """
        Sets the current item of the combo box to the one containing the user's text.
        :param new_text: The text in the combo box.
        """
        self.setCurrentIndex(self.findText(new_text))
