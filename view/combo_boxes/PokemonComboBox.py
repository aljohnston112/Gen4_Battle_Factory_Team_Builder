from PyQt5.QtWidgets import QComboBox

from data_class.Pokemon import Pokemon
from repository.PokemonRepository import all_battle_factory_pokemon, \
    get_set_number
from use_case.RoundUseCase import RoundUseCase, RoundStage
from view.combo_boxes.MoveComboBox import MoveComboBox


class PokemonComboBox(QComboBox):
    """
    A combo box with a list of all Pokémon.
    """

    def text_changed(self, new_text: str) -> None:
        """
        Sets the current item of the combo box
        to the one containing the user's text.
        :param new_text: The text in the combo box.
        """
        self.setCurrentIndex(self.findText(new_text))

    def __add_all_pokemon_names__(self, round_use_case: RoundUseCase) -> None:
        poke_backup = self.currentText()
        move_backup = self.__connected_move_layout__.currentText() \
            if self.__connected_move_layout__ else ""
        self.clear()
        current_set: int = round_use_case.get_current_round().value
        if self.__is_player__:
            set_numbers: list[int] = [
                current_set - 1,
                current_set,
                current_set + 1
            ]
            if current_set >= 7:
                set_numbers.append(current_set - 2)
                set_numbers.append(current_set - 3)
                set_numbers.append(current_set - 4)
        else:
            if round_use_case.get_round_stage() == RoundStage.LAST_BATTLE:
                set_numbers: list[int] = [current_set + 1]
            else:
                set_numbers: list[int] = [
                    current_set - 1,
                    current_set
                ]

        pokemon_list: list[Pokemon] = [
            p for p in all_battle_factory_pokemon.values()
            if get_set_number(p) in set_numbers
        ]

        name_set: set[str] = set()
        for pokemon in pokemon_list:
            pokemon: Pokemon
            name_set.add(pokemon.name)
        self.addItem("")
        for name in sorted(name_set):
            name: str
            self.addItem(name)
        self.text_changed(poke_backup)
        if self.__connected_move_layout__:
            self.__connected_move_layout__.setCurrentText(move_backup)

    def __init__(
            self,
            round_use_case: RoundUseCase,
            is_player: bool,
            connected_move_layout: MoveComboBox | None
    ) -> None:
        super().__init__()
        self.__is_player__: bool = is_player
        self.__connected_move_layout__: MoveComboBox | None = \
            connected_move_layout
        self.__add_all_pokemon_names__(round_use_case=round_use_case)
        self.currentTextChanged.connect(self.text_changed)
        round_use_case.add_listener(self.__add_all_pokemon_names__)
