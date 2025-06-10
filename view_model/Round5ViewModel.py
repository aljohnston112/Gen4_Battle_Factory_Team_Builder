from data_class.Type import get_type
from repository.PokemonRepository import find_pokemon_with_type
from use_case.TeamUseCase import TeamUseCase


def do_round_five(team_pokemon, choice_pokemon, opponent_pokemon, level):
    pass


class Round5ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            level=50
    ) -> None:
        self.__team_use_case__ = team_use_case
        self.__opponent_pokemon__ = None
        self.__level__ = level

    def set_pokemon_type(self, pokemon_type: str):
        pt = None
        if pokemon_type != "":
            get_type(pokemon_type)
        self.__opponent_pokemon__ = find_pokemon_with_type(pt)

    def confirm_clicked(self) -> None:
        do_round_five(
            self.__team_use_case__.get_team_pokemon(),
            self.__team_use_case__.get_choice_pokemon(),
            self.__opponent_pokemon__,
            self.__level__
        )
