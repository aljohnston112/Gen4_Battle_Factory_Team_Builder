from data_class.Pokemon import Pokemon


class PokemonUseCase:

    def __init__(self):
        self.__pokemon__ = []

    def set_pokemon(self, pokemon: list[Pokemon]):
        self.__pokemon__ = pokemon

    def get_pokemon(self):
        return self.__pokemon__
