from collections import defaultdict
from itertools import combinations
from math import ceil
from typing import List

from algorithm.FrontierTeamBuilder import print_sorted_winners_from_list, \
    load_pokemon_ranks
from data_class.Hits import Hits
from data_class.Pokemon import Pokemon, get_stat_for_battle_factory_pokemon, \
    get_num_hits_attackers_need_do_to_defenders
from data_class.Stat import StatEnum
from use_case.PokemonPickerUseCase import PokemonPickerUseCase


def print_coverage(opponent_pokemon, player_pokemon, set_numbers):
    results = []
    for triple in combinations(player_pokemon, 3):
        for set_number in set_numbers:
            all_opponents = set(op.unique_key for op in opponent_pokemon)

            # Union of wins
            union_wins = set()
            for poke in triple:
                union_wins |= set(
                    load_pokemon_ranks()[set_number].get(poke.unique_key, []))
            union_remaining = [op.unique_key for op in opponent_pokemon if
                               op.unique_key not in union_wins]

            # Intersection of wins
            intersect_wins = all_opponents
            for poke in triple:
                intersect_wins &= set(
                    load_pokemon_ranks()[set_number].get(poke.unique_key, []))
            intersect_remaining = [op.unique_key for op in opponent_pokemon if
                                   op.unique_key not in intersect_wins]

            results.append(
                (triple, len(union_remaining), union_remaining,
                 len(intersect_remaining), intersect_remaining))
    # Sort by fewest union misses
    results.sort(key=lambda x: x[1])
    # Print
    for triple, union_count, union_list, intersect_count, intersect_list in results:
        names = [p.unique_key for p in triple]
        print(f"{names}")
        print(f"  Opponents not covered (union):     {union_count}")
        print(f"  Remaining (union):     {union_list}")
        print(f"  Opponents not covered (intersect): {intersect_count}")
        print(f"  Remaining (intersect): {intersect_list}\n")


def get_potential_threats(
        chosen_pokemon: list[Pokemon],
        level: int,
        opponent_pokemon: list[Pokemon]
):
    opponent_to_pokemon_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            attackers=opponent_pokemon,
            defenders=chosen_pokemon,
            level=level,
            is_opponent=True
        )
    pokemon_to_opponent_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            attackers=chosen_pokemon,
            defenders=opponent_pokemon,
            level=level,
            is_opponent=False
        )
    potential_threats: set[Pokemon] = set()
    for opponent, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        opponent: Pokemon
        pokemon_to_hits: dict[Pokemon, float]
        for player_pokemon, hits_taken in pokemon_to_hits.items():
            player_pokemon: Pokemon
            hits_taken: float
            hits_given: float = \
                pokemon_to_opponent_to_hits[player_pokemon][opponent]

            player_speed: int = get_stat_for_battle_factory_pokemon(
                player_pokemon,
                level,
                StatEnum.SPEED
            )
            opponent_speed: int = get_stat_for_battle_factory_pokemon(
                opponent,
                level,
                StatEnum.SPEED
            )
            if ceil(hits_given - 1) >= ceil(hits_taken) or \
                    (ceil(hits_taken) == ceil(hits_given) and
                     player_speed > opponent_speed):
                potential_threats.add(opponent)
    return list(potential_threats)


def get_potential_threats_and_print_win_rates(
        chosen_pokemon: list[Pokemon],
        level: int,
        opponent_pokemon: list[Pokemon],
        remaining_pokemon: list[Pokemon]
):
    potential_threats = get_potential_threats(
        chosen_pokemon,
        level,
        opponent_pokemon
    )
    opponent_to_pokemon_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            potential_threats,
            remaining_pokemon,
            level,
            True
        )
    pokemon_to_opponent_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            remaining_pokemon,
            potential_threats,
            level,
            False
        )
    aggregate_and_print_win_rates(
        opponent_to_pokemon_to_hits,
        pokemon_to_opponent_to_hits,
        level
    )
    print_sorted_winners_from_list(chosen_pokemon + remaining_pokemon)


def aggregate_hit_info(
        opponent_to_pokemon_to_hits: defaultdict[Pokemon, dict[Pokemon, float]],
        pokemon_to_opponent_to_hits: defaultdict[Pokemon, dict[Pokemon, float]]
):
    opponent_to_pokemon_to_hit_tuple: \
        defaultdict[Pokemon, dict[Pokemon, Hits]] = defaultdict(lambda: dict())
    for opponent_pokemon, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        opponent_pokemon: Pokemon
        pokemon_to_hits: dict[Pokemon, float]
        for player_pokemon, hits_taken in pokemon_to_hits.items():
            player_pokemon: Pokemon
            hits_taken: float
            hits_given: float = \
                pokemon_to_opponent_to_hits[player_pokemon][opponent_pokemon]
            opponent_to_pokemon_to_hit_tuple[opponent_pokemon][player_pokemon]: \
                Hits = Hits(hits_given=hits_given, hits_taken=hits_taken)
    sorted_opponent_to_pokemon_to_rank: \
        dict[Pokemon, dict[Pokemon, Hits]] = {
        opponent: dict(sorted(pokemon_to_rank.items(), key=lambda x: x[1].hits_given / x[1].hits_given))
        for opponent, pokemon_to_rank in opponent_to_pokemon_to_hit_tuple.items()
    }
    return sorted_opponent_to_pokemon_to_rank


def aggregate_and_print_win_rates(
        opponent_to_pokemon_to_hits,
        pokemon_to_opponent_to_hits,
        level: int
):
    sorted_opponent_to_pokemon_to_rank = aggregate_hit_info(
        opponent_to_pokemon_to_hits,
        pokemon_to_opponent_to_hits
    )
    win_counts: dict[Pokemon, int] = defaultdict(int)
    total_counts: dict[Pokemon, int] = defaultdict(int)

    for opponent, pokemon_to_hits in \
            sorted_opponent_to_pokemon_to_rank.items():
        for poke, hits in pokemon_to_hits.items():
            hits_given = hits.hits_given
            hits_taken = hits.hits_taken
            total_counts[poke] += 1
            player_speed: int = get_stat_for_battle_factory_pokemon(
                poke,
                level,
                StatEnum.SPEED
            )
            opponent_speed: int = get_stat_for_battle_factory_pokemon(
                opponent,
                level,
                StatEnum.SPEED
            )
            if ceil(hits_given - 1) >= ceil(hits_taken) or \
                    (ceil(hits_taken) == ceil(hits_given) and
                     player_speed > opponent_speed):
                win_counts[poke] += 1

    print("\n=== Win Rate Summary ===")
    print(f"{'Pokémon':<20} {'Win Rate (%)':>15}")
    for poke in sorted(
            total_counts.keys(), key=lambda x: win_counts[x] / total_counts[x],
            reverse=True
    ):
        wins = win_counts[poke]
        total = total_counts[poke]
        rate = (wins / total) * 100 if total > 0 else 0
        print(f"{poke.unique_key:<20} {rate:>15.2f}")


def ask_user_to_pick_pokemon(
        num_pokemon: int,
        team_pokemon: List[Pokemon]
):
    pokemon_picker_use_case = PokemonPickerUseCase()
    chosen_pokemon_names = pokemon_picker_use_case.got_pokemon_choices_from_user(
        num_pokemon,
        team_pokemon
    )
    chosen_pokemon = [
        team_poke
        for team_poke in team_pokemon
        if team_poke.name in chosen_pokemon_names
    ]
    return chosen_pokemon


class TeamViewModel:
    def __init__(self, team_use_case, pokemon_use_cases):
        self.__team_use_case__ = team_use_case
        self.__pokemon_use_cases__ = pokemon_use_cases

    def on_new_data(self):
        team_pokemon = [
            poke for pokemon_use_case in self.__pokemon_use_cases__[0:3]
            for poke in pokemon_use_case.get_pokemon()
        ]
        choice_pokemon = [
            poke for pokemon_use_case in self.__pokemon_use_cases__[3:]
            for poke in pokemon_use_case.get_pokemon()
        ]
        team_pokemon.extend(choice_pokemon)
        self.__team_use_case__.set_pokemon(team_pokemon, [])

    def is_last_battle(self, is_last_battle):
        self.__team_use_case__.set_is_last_battle(is_last_battle)
