from typing import Callable

from data_class.Hits import Hits
from data_class.Pokemon import Pokemon
from use_case.PokemonUseCase import PokemonUseCase
from use_case.PrintUseCase import PrintUseCase
from use_case.RoundUseCase import RoundUseCase, RoundStage
from use_case.TeamUseCase import TeamUseCase
from view_model.Round1And2ViewModel import filter_opponents, \
    get_battle_results, print_hit_results


class OpponentBattleResultViewModel:

    def __init__(
            self,
            round_use_case: RoundUseCase,
            team_use_case: TeamUseCase,
            pokemon_use_cases: list[PokemonUseCase],
            print_use_case: PrintUseCase
    ) -> None:
        self.__round_use_case__: RoundUseCase = round_use_case
        self.__team_use_case__: TeamUseCase = team_use_case
        self.__pokemon_use_cases__: list[PokemonUseCase] = pokemon_use_cases
        self.__print_use_case__: PrintUseCase = print_use_case

    def confirm_clicked(self) -> None:
        opponent_pokemon_in: list[Pokemon] = [
            poke for pokemon_use_case in self.__pokemon_use_cases__
            for poke in pokemon_use_case.get_pokemon()
        ]
        set_number: int = self.__round_use_case__.get_current_round().value
        team_use_case: TeamUseCase = self.__team_use_case__
        opponent_pokemon: list[Pokemon] = filter_opponents(
            opponent_pokemon_in=opponent_pokemon_in,
            set_number=set_number,
            is_last_battle
            =self.__round_use_case__.get_round_stage() == RoundStage.LAST_BATTLE,
        )
        set_numbers = [set_number]
        if set_number > 0:
            set_numbers.append(set_number - 1)
        if set_number < 7:
            set_numbers.append(set_number + 1)
        for use_accuracy in [True, False]:
            opponent_to_pokemon_to_hits: dict[str, dict[str, tuple[Hits, bool]]] = \
                get_battle_results(
                    team_use_case=team_use_case,
                    opponent_pokemon=opponent_pokemon,
                    set_numbers=set_numbers,
                    use_accuracy=use_accuracy
                )
            print_use_case: PrintUseCase = self.__print_use_case__
            print_function: Callable[[str], None] = \
                print_use_case.print_1 if use_accuracy \
                    else print_use_case.print_2
            if use_accuracy:
                print_function(
                    "##### 100% accuracy moves results #####"
                )
            else:
                print_function("##### All moves results #####")
            print_hit_results(
                opponent_to_pokemon_to_hits=opponent_to_pokemon_to_hits,
                print_function=print_function
            )
