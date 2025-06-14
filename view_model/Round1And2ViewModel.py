from itertools import combinations
from math import inf
from typing import Callable

from algorithm.FrontierTeamBuilder import load_pokemon_ranks_accuracy, \
    load_pokemon_ranks
from data_class.BattleResult import BattleResult
from data_class.Hits import Hits
from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon, get_pokemon_from_round, \
    is_from_round
from use_case.PokemonPickerUseCase import PokemonPickerUseCase
from use_case.PrintUseCase import PrintUseCase
from use_case.TeamUseCase import TeamUseCase, RoundStage


def do_round_two(
        team_use_case: TeamUseCase,
        opponent_pokemon: list[Pokemon],
        set_number: int,
        print_use_case: PrintUseCase
) -> None:
    do_round_one(
        team_use_case=team_use_case,
        opponent_pokemon_in=opponent_pokemon,
        set_number=set_number,
        print_use_case=print_use_case
    )


def get_remaining_pokemon_and_print_win_rates_and_coverage(
        set_numbers,
        factory_pokemon,
        player_pokemon,
        choice_pokemon,
        chosen_pokemon,
        print_use_case,
) -> list[Pokemon]:
    remaining_pokemon: list[Pokemon] = list(
        set(player_pokemon).difference(set(chosen_pokemon))
    )
    for use_accuracy in [True, False]:
        print_win_rates_and_coverage_over_potential_threats(
            set_numbers=set_numbers,
            factory_pokemon=factory_pokemon,
            player_pokemon=
            [p for p in choice_pokemon if p not in chosen_pokemon],
            choice_pokemon=remaining_pokemon,
            chosen_pokemon=chosen_pokemon,
            print_use_case=print_use_case,
            use_accuracy=use_accuracy
        )
    return remaining_pokemon


def ask_user_to_pick_pokemon(
        num_pokemon: int,
        team_pokemon: list[Pokemon]
) -> list[Pokemon]:
    pokemon_picker_use_case: PokemonPickerUseCase = PokemonPickerUseCase()
    chosen_pokemon_names: list[Pokemon] = \
        pokemon_picker_use_case.got_pokemon_choices_from_user(
            num_pokemon=num_pokemon,
            pokemon=team_pokemon
        )

    chosen_pokemon: list[Pokemon] = [
        team_poke
        for team_poke in team_pokemon
        if team_poke.name in chosen_pokemon_names
    ]
    return chosen_pokemon


def print_sorted_results(
        results: list[
            tuple[
                tuple[Pokemon, Pokemon, Pokemon],
                int,
                list[str],
                int,
                list[str]
            ]
        ],
        sorted_by: str,
        key_function,
        print_function: callable
) -> None:
    results.sort(key=key_function)
    if results:
        print_function(f"Top result by {sorted_by}:")
        for triple, union_len, union, intersect_len, intersection in results:
            names = [p.unique_id for p in triple]
            print_function(f"{names}")
            print_function(f"  Opponents not covered (union):     {union_len}")
            print_function(
                f"  Opponents not covered (intersect): {intersect_len}")


def print_coverage(
        opponent_pokemon: list[Pokemon],
        chosen_pokemon: list[Pokemon],
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        set_numbers: list[int],
        print_use_case: PrintUseCase,
        use_accuracy: bool
) -> None:
    results: list[
        tuple[
            tuple[Pokemon, Pokemon, Pokemon],
            int,
            list[str],
            int,
            list[str]
        ]
    ] = []
    ranks: dict[int, dict[str, BattleResult]] = \
        load_pokemon_ranks_accuracy() if use_accuracy else load_pokemon_ranks()
    for triple in combinations(
            player_pokemon + chosen_pokemon + choice_pokemon,
            3
    ):
        triple: tuple[Pokemon, Pokemon, Pokemon]

        # Only consider triples with the chosen Pokémon
        is_good: bool = True
        for poke in chosen_pokemon:
            poke: Pokemon
            if poke not in triple:
                is_good = False
        if not is_good:
            continue

        # Only consider triple with a max of 1 choice Pokémon
        is_good: bool = True
        count: int = 0
        for poke in choice_pokemon:
            poke: Pokemon
            if poke in triple:
                count += 1
        if count > 1:
            is_good = False
        if not is_good:
            continue

        union_wins: set[str] = set()
        all_opponent_ids: set[str] = \
            set(opponent.unique_id for opponent in opponent_pokemon)
        intersect_wins = set(all_opponent_ids)
        for set_number in set_numbers:
            set_number: int

            # Union of wins
            set_ranks: dict[str, BattleResult] = ranks[set_number]
            for poke in triple:
                poke: Pokemon
                battle_result: BattleResult = set_ranks.get(poke.unique_id)
                if battle_result:
                    win_results = battle_result.win_results
                    union_wins |= set(results for results in win_results)
                    intersect_wins &= set(results for results in win_results)

        union_remaining: list[str] = [
            op_id for op_id in all_opponent_ids
            if op_id not in union_wins
        ]
        intersect_remaining: list[str] = [
            op_id for op_id in all_opponent_ids if
            op_id not in intersect_wins
        ]
        results.append(
            (
                triple,
                len(union_remaining),
                union_remaining,
                len(intersect_remaining),
                intersect_remaining
            )
        )

    print_function: Callable[[str | None], None] = \
        print_use_case.print_1 if use_accuracy else print_use_case.print_2
    print_sorted_results(
        results=results,
        sorted_by="Union",
        key_function=lambda x: x[1],
        print_function=print_function
    )
    print_function(None)


def print_win_rate_results(
        total_counts,
        win_counts,
        print_function: Callable[[str | None], None]
) -> None:
    print_function(f"{'Pokémon':<15} {'Win Rate (%)':>15}")
    sorted_poke_ids: list[str] = sorted(
        total_counts.keys(),
        key=lambda x: win_counts[x] / float(
            total_counts[x] if total_counts[x] > 0 else inf
        ),
        reverse=True
    )
    for poke_id in sorted_poke_ids:
        poke_id: str
        wins: int = win_counts[poke_id]
        total: int = total_counts[poke_id]
        rate: float = (wins / float(total)) * 100 if total > 0 else 0
        print_function(f"{poke_id:<15} {rate:>15.2f}")


def print_win_rates_over_threats(
        pokemon: list[Pokemon],
        potential_threats: set[str],
        set_numbers: list[int],
        print_use_case: PrintUseCase,
        use_accuracy: bool
) -> None:
    # Count the number of wins for each Pokémon
    ranks: dict[int, dict[str, BattleResult]] = \
        load_pokemon_ranks_accuracy() if use_accuracy else load_pokemon_ranks()
    win_counts: dict[str, int] = {}
    total_counts: dict[str, int] = {}
    for poke in pokemon:
        beatable_ids: list[str] = []
        poke_id: str = poke.unique_id
        win_counts[poke_id]: int = 0
        total_counts[poke_id]: int = 0
        for set_number in set_numbers:
            set_number: int
            battle_result: BattleResult = ranks[set_number].get(poke_id, None)
            if battle_result:
                beatable_ids += [
                    threat_id for threat_id in battle_result.win_results.keys()
                ]
        for threat_id in potential_threats:
            threat_id: str
            if threat_id in beatable_ids:
                win_counts[poke_id] += 1
            total_counts[poke_id] += 1
    print_function: Callable[[str], None] = \
        print_use_case.print_1 if use_accuracy else print_use_case.print_2
    if use_accuracy:
        print_function(
            "===== Win Rate Over Potential Threats - 100% accuracy ====="
        )
    else:
        print_function(
            "===== Win Rate Over Potential Threats - All Moves =====")

    print_win_rate_results(
        win_counts=win_counts,
        total_counts=total_counts,
        print_function=print_function
    )


def get_potential_threats(
        set_numbers: list[int],
        chosen_pokemon: list[Pokemon],
        opponent_pokemon: list[Pokemon]
) -> set[str]:
    if len(chosen_pokemon) == 0:
        return {o.unique_id for o in opponent_pokemon}

    # Get the battle results for the given sets
    set_to_battle_results: dict[int, dict[str, BattleResult]] = {}
    ranks_accuracy = load_pokemon_ranks_accuracy()
    for set_number in set_numbers:
        set_to_battle_results[set_number] = ranks_accuracy[set_number]

    # Count the number of wins for each Pokémon
    threats: set[str] = set([o.unique_id for o in opponent_pokemon])
    for poke in chosen_pokemon:
        poke_id: str = poke.unique_id
        for set_number in set_numbers:
            set_number: int
            battle_result: BattleResult = \
                set_to_battle_results[set_number].get(poke_id, None)
            if battle_result:
                for o_id in battle_result.win_results.keys():
                    threats.discard(o_id)
    return threats


def print_win_rates_and_coverage_over_potential_threats(
        set_numbers: list[int],
        factory_pokemon: list[Pokemon],
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        chosen_pokemon: list[Pokemon],
        print_use_case: PrintUseCase,
        use_accuracy: bool
) -> None:
    potential_threats: set[str] = get_potential_threats(
        set_numbers=set_numbers,
        chosen_pokemon=chosen_pokemon,
        opponent_pokemon=factory_pokemon
    )
    pokemon_left: list[Pokemon] = choice_pokemon + [
        p for p in player_pokemon
        if p not in chosen_pokemon
    ]
    print_win_rates_over_threats(
        pokemon=pokemon_left,
        potential_threats=potential_threats,
        set_numbers=set_numbers,
        print_use_case=print_use_case,
        use_accuracy=use_accuracy
    )
    if use_accuracy:
        print_use_case.print_1()
    else:
        print_use_case.print_2()
    print_coverage(
        opponent_pokemon=factory_pokemon,
        chosen_pokemon=chosen_pokemon,
        player_pokemon=player_pokemon,
        choice_pokemon=choice_pokemon,
        set_numbers=set_numbers,
        print_use_case=print_use_case,
        use_accuracy=use_accuracy
    )


def print_hit_results(
        opponent_to_pokemon_to_hits: dict[str, dict[str, Hits]],
        print_function: Callable[[str | None], None]
) -> None:
    for opponent, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        opponent: str
        pokemon_to_hits: dict[str, Hits]
        print_function(f"----- Against {opponent} -----")
        print_function(
            f"{'Pokémon':<20} {'Hits to KO':>12} {'Hits to be KOed':>18}"
        )
        for poke, hits in sorted(
                pokemon_to_hits.items(),
                key=lambda item: 9999
                if item[1].hits_taken == 0
                else item[1].hits_given / item[1].hits_taken
        ):
            poke: str
            hits: Hits
            hits_given: float = hits.hits_given
            hits_taken: float = hits.hits_taken
            print_function(
                f"{poke:<20} {hits_given:>12.2f} {hits_taken:>18.2f}"
            )
        print_function(None)


def get_battle_results(
        team_use_case: TeamUseCase,
        opponent_pokemon: list[Pokemon],
        set_numbers: list[int],
        use_accuracy: bool
) -> dict[str, dict[str, Hits]]:
    opponent_to_pokemon_to_hits: dict[str, dict[str, Hits]] = {}
    all_battle_results: dict[int, dict[str, BattleResult]] = \
        load_pokemon_ranks_accuracy() if use_accuracy else load_pokemon_ranks()
    player_pokemon: list[Pokemon] = team_use_case.get_team_pokemon()
    choice_pokemon: list[Pokemon] = team_use_case.get_choice_pokemon()
    for opponent in opponent_pokemon:
        opponent: Pokemon
        pokemon_to_hits: dict[str, Hits] = {}
        opponent_id: str = opponent.unique_id
        for set_number in set_numbers:
            set_number: int
            battle_results: dict[str, BattleResult] = \
                all_battle_results[set_number]
            for poke in player_pokemon + choice_pokemon:
                poke: Pokemon
                poke_id: str = poke.unique_id
                battle_result: BattleResult = battle_results.get(poke_id)
                if battle_result:
                    win_results: dict[str, Hits] = battle_result.win_results
                    if win_results and opponent_id in win_results:
                        pokemon_to_hits[poke_id] = win_results[opponent_id]
                    else:
                        lose_results: dict[str, Hits] = \
                            battle_result.lose_results
                        if lose_results and opponent_id in lose_results:
                            pokemon_to_hits[poke_id] = lose_results[opponent_id]
                        else:
                            print("Missing battle results")
                else:
                    print("No battle results")
        opponent_to_pokemon_to_hits[opponent_id] = {
            k: v for k, v in sorted(
                pokemon_to_hits.items(),
                key=lambda item: item[1].hits_given / item[1].hits_taken
            )
        }
    return opponent_to_pokemon_to_hits


def do_round(
        team_use_case: TeamUseCase,
        opponent_pokemon: list[Pokemon],
        factory_pokemon: list[Pokemon],
        set_numbers: list[int],
        print_use_case: PrintUseCase,
        use_accuracy: bool
) -> None:
    player_pokemon: list[Pokemon] = team_use_case.get_team_pokemon()
    choice_pokemon: list[Pokemon] = team_use_case.get_choice_pokemon()
    opponent_to_pokemon_to_hits: dict[str, dict[str, Hits]] = \
        get_battle_results(
            team_use_case=team_use_case,
            opponent_pokemon=opponent_pokemon,
            set_numbers=set_numbers,
            use_accuracy=use_accuracy
        )
    print_function: Callable[[str], None] = \
        print_use_case.print_1 if use_accuracy else print_use_case.print_2
    if use_accuracy:
        print_function("########## 100% accuracy moves results ##########")
    else:
        print_function("########## All moves results ##########")
    print_hit_results(
        opponent_to_pokemon_to_hits=opponent_to_pokemon_to_hits,
        print_function=print_function
    )
    print_win_rates_and_coverage_over_potential_threats(
        set_numbers=set_numbers,
        factory_pokemon=factory_pokemon,
        player_pokemon=player_pokemon,
        choice_pokemon=choice_pokemon,
        chosen_pokemon=[],
        print_use_case=print_use_case,
        use_accuracy=use_accuracy
    )


def filter_opponents(
        opponent_pokemon_in: list[Pokemon],
        set_number: int,
        is_last_battle: bool
) -> list[Pokemon]:
    if set_number < 7:
        if is_last_battle:
            opponent_pokemon: list[Pokemon] = [
                p for p in opponent_pokemon_in
                if is_from_round(p, set_number + 1)
            ]
        else:
            opponent_pokemon: list[Pokemon] = [
                p for p in opponent_pokemon_in
                if is_from_round(p, set_number)
            ]
            if set_number > 0:
                opponent_pokemon += [
                    p for p in opponent_pokemon_in
                    if is_from_round(p, set_number - 1)
                ]
    else:
        # Round 8+ Pokémon can come from any set greater than 2
        opponent_pokemon: list[Pokemon] = []
        for i in range(3, 8):
            opponent_pokemon += [
                p for p in opponent_pokemon_in
                if is_from_round(p, i)
            ]
    return opponent_pokemon


def do_round_one(
        team_use_case: TeamUseCase,
        opponent_pokemon_in: list[Pokemon],
        set_number: int,
        print_use_case: PrintUseCase
) -> None:
    print_use_case.clear_both()
    set_numbers = [set_number]
    if set_number > 0:
        set_numbers.append(set_number - 1)
    if set_number < 7:
        set_numbers.append(set_number + 1)
    round_stage: RoundStage = team_use_case.get_round_stage()
    is_last_battle = round_stage == RoundStage.LAST_BATTLE
    opponent_pokemon: list[Pokemon] = filter_opponents(
        opponent_pokemon_in=opponent_pokemon_in,
        set_number=set_number,
        is_last_battle=is_last_battle,
    )
    factory_pokemon: list[Pokemon] = get_pokemon_from_round(
        round_number=set_number,
        is_last_battle=is_last_battle
    )
    player_pokemon: list[Pokemon] = team_use_case.get_team_pokemon()
    choice_pokemon: list[Pokemon] = team_use_case.get_choice_pokemon()
    for use_accuracy in [True, False]:
        do_round(
            team_use_case=team_use_case,
            opponent_pokemon=opponent_pokemon,
            factory_pokemon=factory_pokemon,
            set_numbers=set_numbers,
            print_use_case=print_use_case,
            use_accuracy=use_accuracy
        )

    chosen_pokemon: list[Pokemon] = \
        ask_user_to_pick_pokemon(
            num_pokemon=1,
            team_pokemon=player_pokemon
        )
    remaining_pokemon: list[Pokemon] = \
        get_remaining_pokemon_and_print_win_rates_and_coverage(
            set_numbers=set_numbers,
            factory_pokemon=factory_pokemon,
            player_pokemon=player_pokemon,
            choice_pokemon=choice_pokemon,
            chosen_pokemon=chosen_pokemon,
            print_use_case=print_use_case,
        )
    chosen_pokemon += ask_user_to_pick_pokemon(
        num_pokemon=1,
        team_pokemon=remaining_pokemon
    )
    get_remaining_pokemon_and_print_win_rates_and_coverage(
        set_numbers=set_numbers,
        factory_pokemon=factory_pokemon,
        player_pokemon=player_pokemon,
        choice_pokemon=choice_pokemon,
        chosen_pokemon=chosen_pokemon,
        print_use_case=print_use_case,
    )


# ==============================================================================


class Round1And2ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            print_use_case: PrintUseCase,
            is_round_2: bool,
            level: int
    ) -> None:
        self.__is_round_2__: bool = is_round_2
        self.__team_use_case__: TeamUseCase = team_use_case
        self.__print_use_case__: PrintUseCase = print_use_case
        self.__opponent_pokemon__: list[Pokemon] = []
        self.__level__: int = level

    def confirm_clicked(self) -> None:
        if not self.__is_round_2__:
            do_round_one(
                team_use_case=self.__team_use_case__,
                opponent_pokemon_in=self.__opponent_pokemon__,
                set_number=0,
                print_use_case=self.__print_use_case__
            )
        else:
            do_round_two(
                team_use_case=self.__team_use_case__,
                opponent_pokemon=self.__opponent_pokemon__,
                set_number=1,
                print_use_case=self.__print_use_case__
            )

    def set_opponent_pokemon_names(
            self,
            opponent_pokemon_names: list[str]
    ) -> None:
        self.__opponent_pokemon__: list[Pokemon] = find_pokemon(
            pokemon_names=opponent_pokemon_names,
            move_names=None
        )
