from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon
from use_case.TeamUseCase import TeamUseCase, RoundStage
from view_model.Round1And2ViewModel import do_round_two


def do_round_three(
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        opponent_pokemon_in: list[Pokemon],
        level: int,
        is_first_battle: bool,
        is_last_battle: bool
):
    do_round_two(
        player_pokemon,
        choice_pokemon,
        opponent_pokemon_in,
        level,
        is_first_battle,
        is_last_battle,
        2
    )


class Round3ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            level
    ) -> None:
        self.__team_use_case__ = team_use_case
        self.__opponent_pokemon__ = None
        self.__level__ = level

    def set_pokemon_name_and_move(self, name, move):
        self.__opponent_pokemon__ = find_pokemon([name], [move])

    def confirm_clicked(self) -> None:
        do_round_three(
            self.__team_use_case__.get_team_pokemon(),
            self.__team_use_case__.get_choice_pokemon(),
            self.__opponent_pokemon__,
            self.__level__,
            self.__team_use_case__.get_round_stage() == RoundStage.FIRST_BATTLE,
            self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE
        )
