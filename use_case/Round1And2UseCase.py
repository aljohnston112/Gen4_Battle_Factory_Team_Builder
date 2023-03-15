class Round1And2UseCase:

    def __init__(self):
        self.__opponent_pokemon__ = []

    def set_opponent_pokemon(self, pokemon):
        self.__opponent_pokemon__ = pokemon

    def get_opponent_pokemon(self):
        return self.__opponent_pokemon__
