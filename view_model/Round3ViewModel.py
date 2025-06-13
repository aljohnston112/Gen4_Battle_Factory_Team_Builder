from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon
from use_case.PrintUseCase import PrintUseCase
from use_case.TeamUseCase import TeamUseCase
from view_model.Round1And2ViewModel import do_round_one


def do_round_three(
        team_use_case: TeamUseCase,
        opponent_pokemon_in: list[Pokemon],
        print_use_case: PrintUseCase
):
    do_round_one(
        team_use_case=team_use_case,
        opponent_pokemon_in=opponent_pokemon_in,
        set_number=2,
        print_use_case=print_use_case
    )


class Round3ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            print_use_case: PrintUseCase,
            level: int
    ) -> None:
        self.__team_use_case__: TeamUseCase = team_use_case
        self.__print_use_case__: PrintUseCase = print_use_case
        self.__opponent_pokemon__: list[Pokemon] = []
        self.__level__: int = level

    def set_pokemon_name_and_move(self, name: str, move: str) -> None:
        self.__opponent_pokemon__ = \
            find_pokemon([name], [move])

    def confirm_clicked(self) -> None:
        do_round_three(
            team_use_case=self.__team_use_case__,
            opponent_pokemon_in=self.__opponent_pokemon__,
            print_use_case=self.__print_use_case__
        )
