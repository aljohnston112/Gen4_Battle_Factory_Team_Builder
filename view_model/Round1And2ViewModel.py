from typing import Callable

from algorithm.FrontierTeamBuilder import load_pokemon_ranks_accuracy, \
    load_pokemon_ranks
from data_class.BattleResult import BattleResult
from data_class.Hits import Hits
from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon, \
    get_pokemon_from_set, is_valid_round
from use_case.PrintUseCase import PrintUseCase
from use_case.TeamUseCase import TeamUseCase, RoundStage
from view_model.TeamViewmodel import ask_user_to_pick_pokemon, \
    get_potential_threats_and_print_win_rates_and_coverage


def do_round_two(
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        opponent_pokemon: list[Pokemon],
        is_first_battle: bool,
        is_last_battle: bool,
        set_number: int,
        print_use_case: PrintUseCase
):
    do_round_one(
        player_pokemon=player_pokemon,
        choice_pokemon=choice_pokemon,
        opponent_pokemon_in=opponent_pokemon,
        set_number=set_number,
        is_first_battle=is_first_battle,
        is_last_battle=is_last_battle,
        print_use_case=print_use_case
    )


def print_hit_results(opponent_to_pokemon_to_hits: dict[str, dict[str, Hits]],
                      print_func: callable):
    for opponent, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        opponent: str
        pokemon_to_hits: dict[str, Hits]
        print_func(f"----- Against {opponent} -----")
        print_func(
            f"{'Pokémon':<20} {'Hits to KO':>12} {'Hits to be KOed':>18}")
        for poke, hits in sorted(
                pokemon_to_hits.items(),
                key=lambda item: 9999
                if item[1].hits_taken == 0 or item[1].hits_given == 0
                else item[1].hits_given / item[1].hits_taken
        ):
            poke: str
            hits: Hits
            hits_to_ko_opponent: float = hits.hits_given
            hits_to_get_koed: float = hits.hits_taken
            print_func(
                f"{poke:<20} "
                f"{hits_to_ko_opponent:>12.2f} "
                f"{hits_to_get_koed:>18.2f}"
            )
        print_func()


def do_round_one(
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        opponent_pokemon_in: list[Pokemon],
        set_number: int,
        is_first_battle: bool,
        is_last_battle: bool,
        print_use_case: PrintUseCase
) -> None:
    if set_number < 7:
        if is_last_battle:
            opponent_pokemon = \
                [p for p in opponent_pokemon_in if
                 is_valid_round(p, set_number + 1)]
        else:
            opponent_pokemon = \
                [p for p in opponent_pokemon_in if
                 is_valid_round(p, set_number)]
            if set_number > 0:
                opponent_pokemon += \
                    [p for p in opponent_pokemon_in if
                     is_valid_round(p, set_number - 1)]
    else:
        opponent_pokemon = \
            [p for p in opponent_pokemon_in if is_valid_round(p, 3)]
        opponent_pokemon += [poke for poke in
                             opponent_pokemon_in if
                             is_valid_round(poke, 4)]
        opponent_pokemon += [poke for poke in
                             opponent_pokemon_in if
                             is_valid_round(poke, 5)]
        opponent_pokemon += [poke for poke in
                             opponent_pokemon_in if
                             is_valid_round(poke, 6)]
        opponent_pokemon += [poke for poke in
                             opponent_pokemon_in if
                             is_valid_round(poke, 7)]
    factory_pokemon = get_pokemon_from_set(set_number, is_last_battle)
    for use_accuracy in [True, False]:
        do_round(
            player_pokemon=player_pokemon,
            choice_pokemon=choice_pokemon,
            opponent_pokemon=opponent_pokemon,
            factory_pokemon=factory_pokemon,
            set_number=set_number,
            print_use_case=print_use_case,
            use_accuracy=use_accuracy
        )
    chosen_pokemon: list[Pokemon] = ask_user_to_pick_pokemon(1, player_pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(player_pokemon)
        .difference(set(chosen_pokemon))
    )

    set_numbers = [set_number]
    if set_number > 0:
        set_numbers.append(set_number - 1)
    if set_number < 7:
        set_numbers.append(set_number + 1)
    for use_accuracy in [True, False]:
        get_potential_threats_and_print_win_rates_and_coverage(
            set_numbers,
            factory_pokemon,
            [p for p in choice_pokemon if p not in chosen_pokemon],
            remaining_pokemon,
            chosen_pokemon,
            is_first_battle,
            print_use_case,
            use_accuracy
        )
    chosen_pokemon += ask_user_to_pick_pokemon(1, remaining_pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(player_pokemon)
        .difference(set(chosen_pokemon))
    )
    for use_accuracy in [True, False]:
        get_potential_threats_and_print_win_rates_and_coverage(
            set_numbers,
            factory_pokemon,
            [p for p in choice_pokemon if p not in chosen_pokemon],
            remaining_pokemon,
            chosen_pokemon,
            is_first_battle,
            print_use_case,
            use_accuracy
        )


def do_round(
        player_pokemon,
        choice_pokemon,
        opponent_pokemon,
        factory_pokemon,
        set_number,
        print_use_case,
        use_accuracy
):
    set_numbers = [set_number]
    if set_number > 0:
        set_numbers.append(set_number - 1)
    if set_number < 7:
        set_numbers.append(set_number + 1)
    opponent_to_pokemon_to_hits: dict[str, dict[str, Hits]] = {}
    all_ranks = load_pokemon_ranks_accuracy() if use_accuracy else load_pokemon_ranks()
    for opponent in opponent_pokemon:
        pokemon_to_hits: dict[str, Hits] = {}
        opponent_id: str = opponent.unique_id
        for set_number in set_numbers:
            ranks = all_ranks[set_number]
            for poke in player_pokemon + choice_pokemon:
                poke_id = poke.unique_id
                battle_result: BattleResult = ranks.get(poke_id)
                if battle_result:
                    win_results: dict[str, Hits] = battle_result.win_results
                    if opponent_id in win_results:
                        pokemon_to_hits[poke_id] = win_results[opponent_id]
                    else:
                        lose_results: dict[str, Hits] = \
                            battle_result.lose_results
                        if battle_result and opponent_id in lose_results:
                            pokemon_to_hits[poke_id] = lose_results[opponent_id]
                        else:
                            raise Exception("Missing battle results")
        opponent_to_pokemon_to_hits[opponent_id] = {
            k: v for k, v in sorted(
                pokemon_to_hits.items(),
                key=lambda item: item[1].hits_given / item[1].hits_taken
            )
        }
    print_func: Callable[[str], None] = \
        print_use_case.print_1 if use_accuracy else print_use_case.print_2
    if use_accuracy:
        print_func("########## 100% accuracy moves results ##########")
    else:
        print_func("########## All moves results ##########")
    print_hit_results(opponent_to_pokemon_to_hits, print_func)
    get_potential_threats_and_print_win_rates_and_coverage(
        set_numbers,
        factory_pokemon,
        player_pokemon,
        choice_pokemon,
        [],
        False,
        print_use_case,
        use_accuracy
    )


class Round1And2ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            print_use_case: PrintUseCase,
            is_round_2: bool,
            level: int
    ) -> None:
        self.__is_round_2: bool = is_round_2
        self.__team_use_case__: TeamUseCase = team_use_case
        self.__print_use_case__: PrintUseCase = print_use_case
        self.__opponent_pokemon__: list[Pokemon] = []
        self.__level__: int = level

    def set_opponent_pokemon_names(
            self,
            opponent_pokemon_names: list[str]
    ) -> None:
        self.__opponent_pokemon__ = find_pokemon(
            pokemon_names=opponent_pokemon_names,
            move_names=None
        )

    def confirm_clicked(self) -> None:
        if not self.__is_round_2:
            do_round_one(
                self.__team_use_case__.get_team_pokemon(),
                self.__team_use_case__.get_choice_pokemon(),
                self.__opponent_pokemon__,
                0,
                self.__team_use_case__.get_round_stage() == RoundStage.FIRST_BATTLE,
                self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE,
                self.__print_use_case__
            )
        else:
            do_round_two(
                self.__team_use_case__.get_team_pokemon(),
                self.__team_use_case__.get_choice_pokemon(),
                self.__opponent_pokemon__,
                self.__team_use_case__.get_round_stage() == RoundStage.FIRST_BATTLE,
                self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE,
                1,
                self.__print_use_case__
            )
