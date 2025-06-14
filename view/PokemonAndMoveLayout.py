from typing import Callable

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox

from data_class.Move import Move
from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon
from use_case.PokemonUseCase import PokemonUseCase
from view.combo_boxes.PokemonComboBox import PokemonComboBox


class PokemonAndMoveLayout(QWidget):
    """
    A QWidget that lets the user pick a Pokémon
    and then a move if there is more than one of that Pokémon.
    The move is used to narrow down what Pokémon the user selects.
    """

    def __move_text_changed__(self) -> None:
        self.__update_state__()

    def __get_pokemon__(self) -> list[Pokemon]:
        return find_pokemon(
            pokemon_names=[self.__pokemon_combo_box__.currentText()],
            move_names=[self.__move_combo_box__.currentText()]
        )

    def __update_state__(self) -> None:
        self.__pokemon_use_case__.set_pokemon(self.__get_pokemon__())
        if self.__on_new_data__:
            self.__on_new_data__()

    def __pokemon_text_changed__(self, pokemon_name: str) -> None:
        """
        Updates the MoveComboBox based on the user's Pokémon choice.
        :param pokemon_name: The Pokémon name the user chose.
        """
        self.__move_combo_box__.clear()
        selected_pokemon: list[Pokemon] = find_pokemon(
            pokemon_names=[pokemon_name],
            move_names=None
        )
        if len(selected_pokemon) > 1:
            # Get the unique moves that each data_class with the name can know
            pokemon_moves: set[Move] = set()
            removed_moves: set[Move] = set()
            for poke in selected_pokemon:
                poke: Pokemon
                move_list: list[Move] = poke.moves
                for move in move_list:
                    move: Move
                    if move in pokemon_moves:
                        removed_moves.add(move)
                        pokemon_moves.remove(move)
                    if move not in removed_moves:
                        pokemon_moves.add(move)

            # Add the moves to the combo box
            for move in pokemon_moves:
                self.__move_combo_box__.addItem(move.name)
            self.__move_combo_box__.setVisible(True)
        else:
            self.__move_combo_box__.setVisible(False)
        self.__update_state__()

    def __init__(
            self,
            pokemon_use_case: PokemonUseCase,
            on_new_data: Callable[[], None] | None
    ) -> None:
        super().__init__()
        self.__on_new_data__: Callable[[], None] | None = on_new_data
        self.__pokemon_use_case__: PokemonUseCase = pokemon_use_case

        layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(layout)

        self.__pokemon_combo_box__: PokemonComboBox = PokemonComboBox()
        self.__pokemon_combo_box__.currentTextChanged.connect(
            self.__pokemon_text_changed__
        )
        layout.addWidget(self.__pokemon_combo_box__)

        self.__move_combo_box__: QComboBox = QComboBox()
        self.__move_combo_box__.setVisible(False)
        self.__move_combo_box__.currentTextChanged.connect(
            self.__move_text_changed__
        )
        layout.addWidget(self.__move_combo_box__)
