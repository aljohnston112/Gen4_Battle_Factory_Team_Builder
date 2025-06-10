from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox

from repository.PokemonRepository import find_pokemon
from view.combo_boxes.PokemonComboBox import PokemonComboBox


class PokemonAndMoveLayout(QWidget):
    """
    A QWidget that lets the user pick a data_class and then a move.
    It is used to narrow down what data_class the user selects.
    """

    def __init__(self, pokemon_use_case, on_new_data):
        super().__init__()

        self.__on_new_data__ = on_new_data
        self.__pokemon_use_case__ = pokemon_use_case

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.pokemon_combo_box = PokemonComboBox()
        self.pokemon_combo_box.currentTextChanged.connect(self.__pokemon_text_changed__)

        self.move_combo_box = QComboBox()
        self.move_combo_box.setVisible(False)
        self.move_combo_box.currentTextChanged.connect(self.__move_text_changed__)

        layout.addWidget(self.pokemon_combo_box)
        layout.addWidget(self.move_combo_box)

    def __pokemon_text_changed__(self, pokemon_name):
        """
        Updates the MoveComboBox based on the user's choice of data_class.
        :param pokemon_name: The data_class name the user chose.
        """
        self.move_combo_box.clear()

        selected_pokemon = find_pokemon(
            pokemon_names=[pokemon_name],
            move_names=None
        )
        if len(selected_pokemon) > 1:

            # Get the unique moves that each data_class with the name can know
            pokemon_moves = set()
            removed_moves = set()
            for poke in selected_pokemon:
                move_list = poke.moves
                for move in move_list:
                    if move in pokemon_moves:
                        removed_moves.add(move)
                        pokemon_moves.remove(move)
                    if move not in removed_moves:
                        pokemon_moves.add(move)

            # Add the moves to the combo box
            for move in pokemon_moves:
                self.move_combo_box.addItem(move.name)
            self.move_combo_box.setVisible(True)
        else:
            self.move_combo_box.setVisible(False)
        self.__update_state__()

    def __move_text_changed__(self):
        self.__update_state__()

    def __update_state__(self):
        self.__pokemon_use_case__.set_pokemon(
            self.__get_pokemon__()
        )
        self.__on_new_data__()

    def __get_pokemon__(self):
        return find_pokemon(
            [self.pokemon_combo_box.currentText()],
            [self.move_combo_box.currentText()]
        )
