from typing import List

from data_class.Pokemon import Pokemon


class TeamViewModel:
    def __init__(self, team_use_case, pokemon_use_cases):
        self.__is_first_battle__ = True
        self.__team_use_case__ = team_use_case
        self.__pokemon_use_cases__ = pokemon_use_cases

    def is_first_battle(self, is_first_battle):
        self.__is_first_battle__ = is_first_battle
        self.on_new_data()

    def on_new_data(self):
        team_pokemon = [
            poke for pokemon_use_case in self.__pokemon_use_cases__[0:3]
            for poke in pokemon_use_case.get_pokemon()
        ]
        choice_pokemon = [
            poke for pokemon_use_case in self.__pokemon_use_cases__[3:]
            for poke in pokemon_use_case.get_pokemon()
        ]
        if not self.__is_first_battle__:
            self.__team_use_case__.set_pokemon(
                team_pokemon,
                choice_pokemon
            )
        else:
            team_pokemon.extend(choice_pokemon)
            self.__team_use_case__.set_pokemon(team_pokemon, [])
