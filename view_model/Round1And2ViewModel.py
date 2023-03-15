from repository.PokemonRepository import find_pokemon


class Round1And2ViewModel:

    def __init__(self, round_1_and_2_use_case):
        self.__round_1_and_2_use_case__ = round_1_and_2_use_case

    def set_pokemon_names(self, pokemon_names):
        self.__round_1_and_2_use_case__.set_opponent_pokemon(
            find_pokemon(pokemon_names)
        )
