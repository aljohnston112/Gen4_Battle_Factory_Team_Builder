from data_class.Pokemon import Pokemon


class PokemonUseCase:
    """
    A wrapper for a list of Pokémon
    """

    def __init__(self):
        self.__pokemon__ = []

    def set_pokemon(self, pokemon: list[Pokemon]) -> None:
        self.__pokemon__ = pokemon

    def get_pokemon(self) -> list[Pokemon]:
        return self.__pokemon__
