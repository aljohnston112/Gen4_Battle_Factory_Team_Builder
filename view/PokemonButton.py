from PyQt5.QtWidgets import QPushButton, QDialog


class PokemonButton(QPushButton):
    """
    A QPushButton that can take a callback that returns a String,
    so the registered callback can get the string in this button when it is clicked.
    """

    def __init__(self, pokemon_name: str, clicked_callback):
        super().__init__()
        self.setText(pokemon_name)
        self.clicked_callback = clicked_callback
        self.clicked.connect(self.callback)

    def callback(self):
        self.clicked_callback(self.text())
