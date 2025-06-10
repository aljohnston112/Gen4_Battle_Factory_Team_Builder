from repository.PokemonRepository import find_pokemon_with_move
from use_case.TeamUseCase import TeamUseCase


def do_round_four(team_pokemon, choice_pokemon, opponent_pokemon, level):
    pass


class Round4ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            level=50
    ) -> None:
        self.__team_use_case__ = team_use_case
        self.__opponent_pokemon__ = None
        self.__level__ = level

    def set_pokemon_move(self, move):
        self.__opponent_pokemon__ = find_pokemon_with_move(move)

    def confirm_clicked(self) -> None:
        do_round_four(
            self.__team_use_case__.get_team_pokemon(),
            self.__team_use_case__.get_choice_pokemon(),
            self.__opponent_pokemon__,
            self.__level__
        )
