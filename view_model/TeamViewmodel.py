from itertools import combinations
from math import inf
from typing import Callable

from algorithm.FrontierTeamBuilder import load_pokemon_ranks_accuracy, \
    load_pokemon_ranks
from data_class.BattleResult import BattleResult
from data_class.Pokemon import Pokemon
from use_case.PokemonPickerUseCase import PokemonPickerUseCase
from use_case.PokemonUseCase import PokemonUseCase
from use_case.PrintUseCase import PrintUseCase
from use_case.TeamUseCase import RoundStage, TeamUseCase


def print_top_result(results, sorted_by: str, key_func, print_func: callable):
    results.sort(key=key_func)
    if results:
        print_func(f"Top result by {sorted_by}:")
        for triple, union_count, union_list, intersect_count, intersect_list \
                in results:
            names = [p.unique_id for p in triple]
            print_func(f"{names}")
            print_func(f"  Opponents not covered (union):     {union_count}")
            print_func(
                f"  Opponents not covered (intersect): {intersect_count}"
            )


def print_coverage(
        opponent_pokemon: list[Pokemon],
        chosen_pokemon: list[Pokemon],
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        set_numbers: list[int],
        print_use_case: PrintUseCase,
        use_accuracy: bool
):
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
                    union_wins |= \
                        set(
                            results for results in
                            battle_result.win_results
                        )

            # Intersection of wins
            for poke in triple:
                poke: Pokemon
                battle_result: BattleResult = set_ranks.get(poke.unique_id)
                if battle_result:
                    intersect_wins &= set(
                        results for results in
                        battle_result.win_results
                    )

        union_remaining = [
            op_id for op_id in all_opponent_ids
            if op_id not in union_wins
        ]
        intersect_remaining = [
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

    print_func: Callable[[str], None] = \
        print_use_case.print_1 if use_accuracy else print_use_case.print_2
    print_top_result(
        results,
        "Union",
        key_func=lambda x: x[1],
        print_func=print_func
    )


def print_win_rate_results(total_counts, win_counts, print_func: callable):
    print_func(f"{'Pokémon':<15} {'Win Rate (%)':>15}")
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
        print_func(f"{poke_id:<15} {rate:>15.2f}")


def print_win_rates_over_threats(
        pokemon: list[Pokemon],
        potential_threats: set[str],
        set_numbers: list[int],
        print_use_case: PrintUseCase,
        use_accuracy: bool
):
    # Get the battle results for the given sets
    set_to_battle_results: dict[int, dict[str, BattleResult]] = {}
    ranks = load_pokemon_ranks_accuracy() if use_accuracy else load_pokemon_ranks()
    for set_number in set_numbers:
        set_to_battle_results[set_number] = ranks[set_number]

    # Count the number of wins for each Pokémon
    total_counts: dict[str, int] = {}
    win_counts: dict[str, int] = {}
    for poke in pokemon:
        beatable_ids: list[str] = []
        beatable_ids_accuracy: list[str] = []
        poke_id: str = poke.unique_id
        total_counts[poke_id] = 0
        win_counts[poke_id] = 0
        for set_number in set_numbers:
            set_number: int

            battle_result: BattleResult = \
                set_to_battle_results[set_number].get(poke_id, None)
            if battle_result:
                beatable_ids += \
                    [threat_id for threat_id in
                     battle_result.win_results.keys()]

        for threat_in in potential_threats:
            threat_in: str
            if threat_in in beatable_ids:
                win_counts[poke_id] += 1
            total_counts[poke_id] += 1

    print_func: Callable[[str], None] = \
        print_use_case.print_1 if use_accuracy else print_use_case.print_2
    if use_accuracy:
        print_func(
            "===== Win Rate Over Potential Threats - 100% accuracy moves ====="
        )
    else:
        print_func("===== Win Rate Over Potential Threats - All Moves =====")

    print_win_rate_results(
        total_counts,
        win_counts,
        print_func
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


def get_potential_threats_and_print_win_rates_and_coverage(
        set_numbers: list[int],
        factory_pokemon: list[Pokemon],
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        chosen_pokemon: list[Pokemon],
        is_first_battle: bool,
        print_use_case: PrintUseCase,
        use_accuracy: bool

):
    potential_threats: set[str] = get_potential_threats(
        set_numbers=set_numbers,
        chosen_pokemon=chosen_pokemon,
        opponent_pokemon=factory_pokemon
    )
    pokemon_left = choice_pokemon + \
                   [p for p in player_pokemon if p not in chosen_pokemon]
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
    if is_first_battle:
        print_coverage(
            opponent_pokemon=factory_pokemon,
            chosen_pokemon=chosen_pokemon,
            choice_pokemon=choice_pokemon,
            player_pokemon=player_pokemon,
            set_numbers=set_numbers,
            print_use_case=print_use_case,
            use_accuracy=use_accuracy
        )
    else:
        print_coverage(
            opponent_pokemon=factory_pokemon,
            chosen_pokemon=chosen_pokemon,
            player_pokemon=player_pokemon,
            choice_pokemon=choice_pokemon,
            set_numbers=set_numbers,
            print_use_case=print_use_case,
            use_accuracy=use_accuracy

        )


def ask_user_to_pick_pokemon(
        num_pokemon: int,
        team_pokemon: list[Pokemon]
):
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


class TeamViewModel:
    def __init__(
            self,
            team_use_case: TeamUseCase,
            pokemon_use_cases: list[PokemonUseCase],
    ) -> None:
        self.__team_use_case__: TeamUseCase = team_use_case
        self.__pokemon_use_cases__: list[PokemonUseCase] = pokemon_use_cases

    def on_new_data(self) -> None:
        round_stage: RoundStage = self.__team_use_case__.get_round_stage()

        # All Pokémon are considered team Pokémon for the first round
        # It makes the logic in the rest of the program easier
        if round_stage == RoundStage.FIRST_BATTLE:
            choice_pokemon: list[Pokemon] = []
            team_pokemon: list[Pokemon] = [
                poke for pokemon_use_case in self.__pokemon_use_cases__
                for poke in pokemon_use_case.get_pokemon()
            ]
        else:
            team_pokemon: list[Pokemon] = [
                poke for pokemon_use_case in self.__pokemon_use_cases__[0:3]
                for poke in pokemon_use_case.get_pokemon()
            ]
            choice_pokemon: list[Pokemon] = [
                poke for pokemon_use_case in self.__pokemon_use_cases__[3:]
                for poke in pokemon_use_case.get_pokemon()
            ]
        self.__team_use_case__.set_pokemon(
            team_pokemon=team_pokemon,
            choice_pokemon=choice_pokemon
        )

    def set_round_stage(self, battle_type: RoundStage):
        self.__team_use_case__.set_round_stage(battle_type)
        self.on_new_data()
