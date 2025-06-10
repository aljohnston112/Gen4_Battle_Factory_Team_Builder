from collections import defaultdict
from math import ceil, inf
from typing import List

from algorithm.FrontierTeamBuilder import print_sorted_win_rates, \
    print_coverage, load_pokemon_ranks_accuracy
from data_class.BattleResult import BattleResult
from data_class.Pokemon import Pokemon, get_stat_for_battle_factory_pokemon, \
    get_num_hits_attackers_need_do_to_defenders
from data_class.Stat import StatEnum
from use_case.PokemonPickerUseCase import PokemonPickerUseCase


def get_potential_threats(
        chosen_pokemon: list[Pokemon],
        level: int,
        opponent_pokemon: list[Pokemon]
):
    if len(chosen_pokemon) == 0:
        return list(opponent_pokemon)

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


def get_potential_threats_and_print_win_rates_and_coverage(
        chosen_pokemon: list[Pokemon],
        level: int,
        factory_pokemon: list[Pokemon],
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        set_numbers: list[int]
):
    potential_threats = get_potential_threats(
        chosen_pokemon,
        level,
        factory_pokemon
    )
    print_win_rates(
        choice_pokemon + [p for p in player_pokemon if p not in chosen_pokemon],
        potential_threats,
        set_numbers
    )
    print()
    print_sorted_win_rates(choice_pokemon + [p for p in player_pokemon if p not in chosen_pokemon])
    print()
    print_coverage(factory_pokemon, chosen_pokemon, player_pokemon,
                   choice_pokemon, set_numbers)


def print_win_rates(
        pokemon: list[Pokemon],
        potential_threats: list[Pokemon],
        set_numbers: list[int]
):
    set_to_battle_results = dict()
    ranks_accuracy = load_pokemon_ranks_accuracy()
    for set_number in set_numbers:
        set_to_battle_results[set_number] = ranks_accuracy[set_number]

    total_counts: dict[str, int] = {}
    win_counts: dict[str, int] = {}
    for poke in pokemon:
        total_counts[poke.unique_id] = 0
        win_counts[poke.unique_id] = 0
        for set_number in set_numbers:
            battle_result: BattleResult = \
                set_to_battle_results[set_number].get(poke.unique_id, None)
            if battle_result:
                beatable_ids = {res_tuple for res_tuple in battle_result.results}
                for threat in potential_threats:
                    if threat.unique_id in beatable_ids:
                        win_counts[poke.unique_id] += 1
                    total_counts[poke.unique_id] += 1


    print("=== Win Rate Summary Over Potential Threats ===")
    print(f"{'Pokémon':<20} {'Win Rate (%)':>15}")
    for poke_id in sorted(
            total_counts.keys(), key=lambda x: win_counts[x] / float(total_counts[x] if total_counts[x] > 0 else inf) ,
            reverse=True
    ):
        wins = win_counts[poke_id]
        total = total_counts[poke_id]
        rate = (wins / total) * 100 if total > 0 else 0
        print(f"{poke_id:<20} {rate:>15.2f}")


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
        self.__team_use_case__.set_pokemon(team_pokemon, choice_pokemon)

    def is_last_battle(self, is_last_battle):
        self.__team_use_case__.set_is_last_battle(is_last_battle)
