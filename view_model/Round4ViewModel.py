from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon_with_move
from use_case.PrintUseCase import PrintUseCase
from use_case.RoundUseCase import RoundStage, RoundUseCase
from use_case.TeamUseCase import TeamUseCase
from view_model.Round1And2ViewModel import do_round_one


class Round4ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            round_use_case: RoundUseCase,
            print_use_case: PrintUseCase,
            level: int
    ) -> None:
        self.__team_use_case__: TeamUseCase = team_use_case
        self.__round_use_case__: RoundUseCase = round_use_case
        self.__print_use_case__: PrintUseCase = print_use_case
        self.__opponent_pokemon__: list[Pokemon] = []
        self.__level__: int = level

    def set_pokemon_move(self, move) -> None:
        self.__opponent_pokemon__: list[Pokemon] = find_pokemon_with_move(
            move_name=move,
            is_last_battle=
            self.__round_use_case__.get_round_stage() == RoundStage.LAST_BATTLE,
        )

    def confirm_clicked(self) -> None:
        do_round_one(
            team_use_case=self.__team_use_case__,
            round_use_case=self.__round_use_case__,
            opponent_pokemon_in=self.__opponent_pokemon__,
            print_use_case=self.__print_use_case__
        )
