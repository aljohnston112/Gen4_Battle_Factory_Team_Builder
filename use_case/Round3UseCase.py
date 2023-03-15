

class RoundThreeUseCase:
    def __init__(self):
        self.pokemon = ""
        self.move = ""

    def set_pokemon_name_and_move(self, pokemon, move):
        self.pokemon = pokemon
        self.move = move

    def get_pokemon_name_and_move(self):
        return self.pokemon, self.move
