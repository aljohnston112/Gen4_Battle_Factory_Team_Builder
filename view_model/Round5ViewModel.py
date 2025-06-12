from data_class.Type import get_type
from repository.PokemonRepository import find_pokemon_with_type
from use_case.RoundUseCase import RoundUseCase
from use_case.TeamUseCase import TeamUseCase, RoundStage
from view_model.Round1And2ViewModel import do_round_two


def do_round_five(player_pokemon, choice_pokemon, opponent_pokemon, level, is_first_battle, is_last_battle, current_round):
    do_round_two(
        player_pokemon,
        choice_pokemon,
        opponent_pokemon,
        level,
        is_first_battle,
        is_last_battle,
        current_round
    )


class Round5ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            current_round_use_case: RoundUseCase,
            level
    ) -> None:
        self.__team_use_case__ = team_use_case
        self.__current_round_use_case__ = current_round_use_case
        self.__opponent_pokemon__ = None
        self.__level__ = level
        self.__type__ = ""

    def set_pokemon_type(self, pokemon_type: str):
        self.__type__ = pokemon_type
        pt = None
        is_last_battle = self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE

        if pokemon_type != "":
            pt = get_type(pokemon_type)
        self.__opponent_pokemon__ = find_pokemon_with_type(
            pt,
            self.__current_round_use_case__.get_current_round(),
            is_last_battle
        )

    def confirm_clicked(self) -> None:
        self.set_pokemon_type(self.__type__)
        do_round_five(
            self.__team_use_case__.get_team_pokemon(),
            self.__team_use_case__.get_choice_pokemon(),
            self.__opponent_pokemon__,
            self.__level__,
            self.__team_use_case__.get_round_stage() == RoundStage.FIRST_BATTLE,
            self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE,
            self.__current_round_use_case__.get_current_round().value
        )
