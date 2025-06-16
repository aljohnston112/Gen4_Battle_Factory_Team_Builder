from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon
from use_case.PrintUseCase import PrintUseCase
from use_case.RoundUseCase import RoundUseCase, RoundStage
from use_case.TeamUseCase import TeamUseCase
from view_model.Round1And2ViewModel import do_round_one


class Round3ViewModel:

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

    def set_pokemon_name_and_move(self, name: str, move: str) -> None:
        set_number: int = self.__round_use_case__.get_current_round().value
        if self.__round_use_case__.get_round_stage() == RoundStage.LAST_BATTLE:
            set_numbers: list[int] = [set_number + 1]
        else:
            set_numbers: list[int] = [set_number - 1, set_number]
        self.__opponent_pokemon__ = find_pokemon(
            set_numbers=set_numbers,
            pokemon_names=[name],
            move_names=[move]
        )

    def confirm_clicked(self) -> None:
        user_finished: bool = do_round_one(
            team_use_case=self.__team_use_case__,
            round_use_case=self.__round_use_case__,
            opponent_pokemon_in=self.__opponent_pokemon__,
            print_use_case=self.__print_use_case__
        )

        if user_finished:
            self.__team_use_case__.user_finished_round(
                self.__opponent_pokemon__
            )
