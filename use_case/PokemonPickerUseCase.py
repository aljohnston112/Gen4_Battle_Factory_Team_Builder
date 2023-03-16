from typing import List

from data_class.Pokemon import Pokemon
from view.PokemonPickerDialog import PokemonPickerDialog


class PokemonPickerUseCase:
    def __init__(self):
        self.pokemon_picked = None

    def picked(self, pokemon):
        self.pokemon_picked = pokemon

    def got_pokemon_choices_from_user(
            self,
            num_pokemon: int,
            pokemon: List[Pokemon]
    ):
        pokemon_names = [poke.name for poke in pokemon]
        chosen = []
        if len(pokemon_names) != 0:
            while num_pokemon > 0:
                picker = PokemonPickerDialog(pokemon_names, self.picked)
                picker.exec()
                if self.pokemon_picked is not None:
                    pokemon_names.remove(self.pokemon_picked)
                    chosen.append(self.pokemon_picked)
                    num_pokemon = num_pokemon - 1
                    self.pokemon_picked = None

        return chosen
