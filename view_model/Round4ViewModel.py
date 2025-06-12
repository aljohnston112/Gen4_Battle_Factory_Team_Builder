from repository.PokemonRepository import find_pokemon_with_move
from use_case.TeamUseCase import TeamUseCase, RoundStage
from view_model.Round1And2ViewModel import do_round_two


def do_round_four(player_pokemon, choice_pokemon, opponent_pokemon, level, is_first_battle: bool, is_last_battle):
    do_round_two(
        player_pokemon,
        choice_pokemon,
        opponent_pokemon,
        level,
        is_first_battle,
        is_last_battle,
        3
    )


class Round4ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            level
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
            self.__level__,
            self.__team_use_case__.get_round_stage() == RoundStage.FIRST_BATTLE,
            self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE,
        )
