from PyQt5.QtCore import QEventLoop

from data_class.Pokemon import Pokemon
from view.PokemonPickerDialog import PokemonPickerDialog


class PokemonPickerUseCase:
    def __init__(self) -> None:
        self.pokemon_picked: str | None = None

    def set_picked_pokemon(
            self,
            pokemon: str
    ) -> None:
        self.pokemon_picked: str  = pokemon

    def got_pokemon_choices_from_user(
            self,
            num_pokemon: int,
            pokemon: list[Pokemon]
    ) -> list[Pokemon]:
        pokemon_names = [poke.name for poke in pokemon]
        chosen = []
        if len(pokemon_names) != 0:
            while num_pokemon > 0:
                picker: PokemonPickerDialog = PokemonPickerDialog(
                    pokemon_names=pokemon_names,
                    callback_picked=self.set_picked_pokemon
                )
                loop: QEventLoop = QEventLoop()

                def on_done():
                    loop.quit()

                picker.finished.connect(on_done)
                picker.show()
                loop.exec_()

                if self.pokemon_picked is not None:
                    pokemon_names.remove(self.pokemon_picked)
                    chosen.append(self.pokemon_picked)
                    num_pokemon: int = num_pokemon - 1
                    self.pokemon_picked: str | None = None
        return chosen
