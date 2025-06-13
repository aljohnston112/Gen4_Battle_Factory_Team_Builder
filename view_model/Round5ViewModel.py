from data_class.Pokemon import Pokemon
from data_class.Type import get_type
from repository.PokemonRepository import find_pokemon_with_type
from use_case.PrintUseCase import PrintUseCase
from use_case.RoundUseCase import RoundUseCase
from use_case.TeamUseCase import TeamUseCase, RoundStage
from view_model.Round1And2ViewModel import do_round_one


def do_round_five(
        team_use_case: TeamUseCase,
        opponent_pokemon: list[Pokemon],
        current_round: int,
        print_use_case: PrintUseCase
):
    do_round_one(
        team_use_case=team_use_case,
        opponent_pokemon_in=opponent_pokemon,
        set_number=current_round,
        print_use_case=print_use_case
    )


class Round5ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            print_use_case: PrintUseCase,
            current_round_use_case: RoundUseCase,
            level: int
    ) -> None:
        self.__team_use_case__: TeamUseCase = team_use_case
        self.__print_use_case__: PrintUseCase = print_use_case
        self.__current_round_use_case__: RoundUseCase = current_round_use_case
        self.__opponent_pokemon__: list[Pokemon] = []
        self.__level__: int = level
        self.__type__: str = ""

    def set_pokemon_type(self, pokemon_type: str) -> None:
        self.__type__: str = pokemon_type
        poke_type = None
        if pokemon_type != "": poke_type = get_type(pokemon_type)
        self.__opponent_pokemon__: list[Pokemon] = find_pokemon_with_type(
            pokemon_type=poke_type,
            round_number=self.__current_round_use_case__.get_current_round(),
            is_last_battle=self.__team_use_case__.get_round_stage() ==
                           RoundStage.LAST_BATTLE
        )

    def confirm_clicked(self) -> None:
        self.set_pokemon_type(self.__type__)
        do_round_five(
            team_use_case=self.__team_use_case__,
            opponent_pokemon=self.__opponent_pokemon__,
            current_round=
            self.__current_round_use_case__.get_current_round().value,
            print_use_case=self.__print_use_case__
        )
