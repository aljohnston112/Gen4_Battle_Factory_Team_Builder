import os
from collections import defaultdict
from itertools import combinations
from typing import List

from algorithm.FrontierTeamBuilder import print_sorted_winners_from_list, load_pokemon_ranks_accuracy, \
    load_pokemon_ranks
from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon, all_battle_factory_pokemon
from use_case.TeamUseCase import TeamUseCase
from view_model.TeamViewmodel import ask_user_to_pick_pokemon, is_valid_round, \
    get_num_hits_attackers_need_do_to_defenders, aggregate_hit_info, \
    get_potential_threats_and_print_win_rates


def do_round_two(
        pokemon: list[Pokemon],
        opponent_pokemon: list[Pokemon],
        level: int,
        is_last_battle: bool,
):
    do_round_one(pokemon, opponent_pokemon, level, 1, is_last_battle)

    chosen_pokemon: list[Pokemon] = ask_user_to_pick_pokemon(2, pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(pokemon)
        .difference(set(chosen_pokemon))
    )

    pokemon_list: list[Pokemon] = [p for p in all_battle_factory_pokemon.values() if is_valid_round(p, 1)]
    if is_last_battle:
        pokemon_list += [poke for poke in all_battle_factory_pokemon.values() if is_valid_round(poke, 2)]
    else:
        pokemon_list += [poke for poke in all_battle_factory_pokemon.values() if is_valid_round(poke, 0)]

    get_potential_threats_and_print_win_rates(chosen_pokemon, level, pokemon_list, remaining_pokemon)


def do_round_one(
        pokemon: List[Pokemon],
        opponent_pokemon_in: List[Pokemon],
        level,
        set_number: int,
        is_last_battle: bool
) -> None:
    """
    Given a list of Pokémon, a list of opponents, and their level,
    Pokémon are ranked by how likely they are to beat each opponent.
    :param pokemon:
    :param opponent_pokemon_in:
    :param level:
    :param set_number:
    :param is_last_battle:
    :return:
    """

    opponent_pokemon = [poke for poke in opponent_pokemon_in if is_valid_round(poke, set_number)]
    if is_last_battle:
        opponent_pokemon += [poke for poke in opponent_pokemon_in if is_valid_round(poke, set_number + 1)]
    elif set_number > 0:
        opponent_pokemon += [poke for poke in opponent_pokemon_in if is_valid_round(poke, set_number - 1)]

    opponent_to_pokemon_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            opponent_pokemon,
            pokemon,
            level,
            True
        )

    pokemon_to_opponent_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            pokemon,
            opponent_pokemon,
            level,
            False
        )

    sorted_opponent_to_pokemon_to_rank = aggregate_hit_info(opponent_to_pokemon_to_hits, pokemon_to_opponent_to_hits)

    print("Team pokemon ranks")
    for opponent, pokemon_to_hits in sorted_opponent_to_pokemon_to_rank.items():
        print(f"\n--- Against {opponent.unique_key} ---")
        print(f"{'Pokémon':<20} {'Hits to KO':>12} {'Hits to be KOed':>18}")
        for poke, (hits_to_ko_opponent, hits_to_get_koed) in pokemon_to_hits.items():
            print(f"{poke.unique_key:<20} {hits_to_ko_opponent:>12.2f} {hits_to_get_koed:>18.2f}")
    print()

    print_sorted_winners_from_list(pokemon + opponent_pokemon)
    print()

    set_numbers = [set_number]
    opponent_pokemon = [poke for poke in all_battle_factory_pokemon.values() if is_valid_round(poke, set_number)]
    if is_last_battle:
        opponent_pokemon += [poke for poke in all_battle_factory_pokemon.values() if is_valid_round(poke, set_number + 1)]
        set_numbers.append(set_number + 1)
    elif set_number > 0:
        opponent_pokemon += [poke for poke in all_battle_factory_pokemon.values() if is_valid_round(poke, set_number - 1)]
        set_numbers.append(set_number - 1)

    results = []
    for triple in combinations(pokemon, 3):
        for set_number in set_numbers:
            all_opponents = set(op.unique_key for op in opponent_pokemon)

            # Union of wins
            union_wins = set()
            for poke in triple:
                union_wins |= set(load_pokemon_ranks()[set_number].get(poke.unique_key, []))
            union_remaining = [op.unique_key for op in opponent_pokemon if op.unique_key not in union_wins]

            # Intersection of wins
            intersect_wins = all_opponents
            for poke in triple:
                intersect_wins &= set(load_pokemon_ranks()[set_number].get(poke.unique_key, []))
            intersect_remaining = [op.unique_key for op in opponent_pokemon if op.unique_key not in intersect_wins]

            results.append(
                (triple, len(union_remaining), union_remaining, len(intersect_remaining), intersect_remaining))

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


class Round1And2ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            is_round_2=False,
            level=50
    ) -> None:
        self.__is_round_2 = is_round_2
        self.__team_use_case__ = team_use_case
        self.__opponent_pokemon__ = []
        self.__level__ = level

    def set_opponent_pokemon_names(
            self,
            opponent_pokemon_names: List[str]
    ) -> None:
        self.__opponent_pokemon__ = find_pokemon(opponent_pokemon_names)

    def confirm_clicked(self) -> None:
        pokemon = self.__team_use_case__.get_team_pokemon() + \
                  self.__team_use_case__.get_choice_pokemon()
        if not self.__is_round_2:
            do_round_one(
                pokemon,
                self.__opponent_pokemon__,
                self.__level__,
                0,
                self.__team_use_case__.is_last_battle()
            )
        else:
            do_round_two(
                pokemon,
                self.__opponent_pokemon__,
                self.__level__,
                self.__team_use_case__.is_last_battle()
            )
