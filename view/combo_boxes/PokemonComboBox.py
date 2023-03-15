from PyQt5.QtWidgets import QComboBox

from repository.PokemonRepository import pokemon


class PokemonComboBox(QComboBox):
    """
    A combo box with a list of all data_class
    """
    def __init__(self):
        super().__init__()

        # No data_class has this string of letters in their name
        previous_pokemon_name = "ZZZ"
        self.addItem("")
        for pokemon_name in sorted(pokemon.keys()):
            if previous_pokemon_name not in pokemon_name:
                self.addItem(pokemon_name)
            else:
                pokemon_name = previous_pokemon_name
            previous_pokemon_name = pokemon_name

        self.currentTextChanged.connect(self.text_changed)

    def text_changed(self, new_text):
        """
        Sets the current item of the combo box to the one containing the user's text.
        :param new_text: The text in the combo box.
        """
        self.setCurrentIndex(self.findText(new_text))
