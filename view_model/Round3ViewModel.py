from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon
from use_case.PrintUseCase import PrintUseCase
from use_case.TeamUseCase import TeamUseCase, RoundStage
from view_model.Round1And2ViewModel import do_round_two


def do_round_three(
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        opponent_pokemon_in: list[Pokemon],
        is_first_battle: bool,
        is_last_battle: bool,
        print_use_case: PrintUseCase
):
    do_round_two(
        player_pokemon=player_pokemon,
        choice_pokemon=choice_pokemon,
        opponent_pokemon=opponent_pokemon_in,
        is_first_battle=is_first_battle,
        is_last_battle=is_last_battle,
        set_number=2,
        print_use_case=print_use_case
    )


class Round3ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            print_use_case: PrintUseCase,
            level
    ) -> None:
        self.__team_use_case__ = team_use_case
        self.__print_use_case__ = print_use_case
        self.__opponent_pokemon__ = None
        self.__level__ = level

    def set_pokemon_name_and_move(self, name, move):
        self.__opponent_pokemon__ = find_pokemon([name], [move])

    def confirm_clicked(self) -> None:
        do_round_three(
            player_pokemon=self.__team_use_case__.get_team_pokemon(),
            choice_pokemon=self.__team_use_case__.get_choice_pokemon(),
            opponent_pokemon_in=self.__opponent_pokemon__,
            is_first_battle=self.__team_use_case__.get_round_stage() == RoundStage.FIRST_BATTLE,
            is_last_battle=self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE,
            print_use_case=self.__print_use_case__
        )
