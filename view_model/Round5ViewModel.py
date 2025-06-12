from data_class.Pokemon import Pokemon
from data_class.Type import get_type
from repository.PokemonRepository import find_pokemon_with_type
from use_case.PrintUseCase import PrintUseCase
from use_case.RoundUseCase import RoundUseCase
from use_case.TeamUseCase import TeamUseCase, RoundStage
from view_model.Round1And2ViewModel import do_round_two


def do_round_five(
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        opponent_pokemon: list[Pokemon],
        is_first_battle: bool,
        is_last_battle: bool,
        current_round: int,
        print_use_case: PrintUseCase
):
    do_round_two(
        player_pokemon=player_pokemon,
        choice_pokemon=choice_pokemon,
        opponent_pokemon=opponent_pokemon,
        is_first_battle=is_first_battle,
        is_last_battle=is_last_battle,
        set_number=current_round,
        print_use_case=print_use_case
    )


class Round5ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            print_use_case: PrintUseCase,
            current_round_use_case: RoundUseCase,
            level
    ) -> None:
        self.__team_use_case__ = team_use_case
        self.__print_use_case__ = print_use_case
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
            player_pokemon=self.__team_use_case__.get_team_pokemon(),
            choice_pokemon=self.__team_use_case__.get_choice_pokemon(),
            opponent_pokemon=self.__opponent_pokemon__,
            is_first_battle=self.__team_use_case__.get_round_stage() == RoundStage.FIRST_BATTLE,
            is_last_battle=self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE,
            current_round=self.__current_round_use_case__.get_current_round().value,
            print_use_case=self.__print_use_case__
        )
