from collections import defaultdict
from math import ceil
from typing import List

from algorithm.FrontierTeamBuilder import print_sorted_winners_from_list
from data_class.Pokemon import Pokemon, get_max_damage_frontier_pokemon_can_do_to_defender, \
    get_stat_for_battle_factory_pokemon
from data_class.Stat import StatEnum
from use_case.PokemonPickerUseCase import PokemonPickerUseCase


def get_pokemon_health(pokemon: list[Pokemon], level: int) -> dict[Pokemon, int]:
    pokemon_to_health: dict[Pokemon, int] = dict()
    for poke in pokemon:
        poke: Pokemon
        pokemon_to_health[poke]: int = get_stat_for_battle_factory_pokemon(
            poke,
            level,
            StatEnum.HEALTH
        )
    return pokemon_to_health

def aggregate_hit_info(
        opponent_to_pokemon_to_hits,
        pokemon_to_opponent_to_hits
):
    opponent_to_pokemon_to_hit_tuple: defaultdict[Pokemon, dict[Pokemon, tuple[float, float]]] = defaultdict(
        lambda: dict())
    for opponent, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        opponent: Pokemon
        pokemon_to_hits: dict[Pokemon, tuple[float, float]]
        for player_pokemon, hits in pokemon_to_hits.items():
            player_pokemon: Pokemon
            hits: float
            hits_against_opponent: float = pokemon_to_opponent_to_hits[player_pokemon][opponent]
            # Store both hits values as a tuple (pokemon hits opponent, opponent hits pokemon)
            opponent_to_pokemon_to_hit_tuple[opponent][player_pokemon]: tuple[float, float] = \
                (hits_against_opponent, hits)
    sorted_opponent_to_pokemon_to_rank: dict[Pokemon, dict[Pokemon, tuple[float, float]]] = {
        opponent: dict(sorted(pokemon_to_rank.items(), key=lambda x: x[1]))
        for opponent, pokemon_to_rank in opponent_to_pokemon_to_hit_tuple.items()
    }
    return sorted_opponent_to_pokemon_to_rank


def aggregate_and_print_win_rates(
        opponent_pokemon,
        opponent_to_pokemon_to_hits,
        pokemon,
        pokemon_to_opponent_to_hits
):
    sorted_opponent_to_pokemon_to_rank = aggregate_hit_info(opponent_to_pokemon_to_hits, pokemon_to_opponent_to_hits)
    win_counts: dict[Pokemon, int] = defaultdict(int)
    total_counts: dict[Pokemon, int] = defaultdict(int)

    for opponent, pokemon_to_hits in sorted_opponent_to_pokemon_to_rank.items():
        for poke, (hits_to_ko_opponent, hits_to_get_koed) in pokemon_to_hits.items():
            total_counts[poke] += 1
            # TODO speed test?
            if ceil(hits_to_ko_opponent - 1) < ceil(hits_to_get_koed):
                win_counts[poke] += 1

    print("\n=== Win Rate Summary ===")
    print(f"{'Pokémon':<20} {'Win Rate (%)':>15}")
    for poke in sorted(total_counts.keys(), key=lambda x: win_counts[x] / total_counts[x], reverse=True):
        wins = win_counts[poke]
        total = total_counts[poke]
        rate = (wins / total) * 100 if total > 0 else 0
        print(f"{poke.unique_key:<20} {rate:>15.2f}")
    print_sorted_winners_from_list(pokemon + opponent_pokemon)


def get_max_damage_attackers_can_do_to_defenders(
        attacking_pokemon: list[Pokemon],
        defending_pokemon: list[Pokemon],
        level: int,
        is_opponent: bool,
) -> defaultdict[Pokemon, defaultdict[Pokemon, float]]:
    attacker_to_defender_to_max_damage: defaultdict[Pokemon, defaultdict[Pokemon, float]] = defaultdict(
        lambda: defaultdict(lambda: 0.0)
    )
    for attacker in attacking_pokemon:
        attacker: Pokemon
        for defender in defending_pokemon:
            defender: Pokemon
            max_damage: int = get_max_damage_frontier_pokemon_can_do_to_defender(
                attacker,
                defender,
                level,
                1.0 if is_opponent else 0.85,
                0 if is_opponent else 100,
            )
            attacker_to_defender_to_max_damage[attacker][defender]: int = max_damage
    return attacker_to_defender_to_max_damage


def get_num_hits_attackers_need_do_to_defenders(
        attackers: list[Pokemon],
        defenders: list[Pokemon],
        level: int,
        is_opponent: bool
) -> defaultdict[Pokemon, dict[Pokemon, float]]:
    attacker_to_defender_to_max_damage: defaultdict[Pokemon, defaultdict[Pokemon, float]] = \
        get_max_damage_attackers_can_do_to_defenders(
            attackers,
            defenders,
            level,
            is_opponent
        )
    pokemon_to_health: dict[Pokemon, int] = get_pokemon_health(attackers + defenders, level)
    attacker_to_defender_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = defaultdict(lambda: dict())
    for attacker, defender_to_max_damage in attacker_to_defender_to_max_damage.items():
        attacker: Pokemon
        defender_to_max_damage: defaultdict[Pokemon, float]
        for defender, max_damage in defender_to_max_damage.items():
            defender: Pokemon
            max_damage: int
            if max_damage != 0:
                hits: float = pokemon_to_health[defender] / max_damage
                if hits < 1:
                    hits: float = 1
            else:
                hits = 9999
            attacker_to_defender_to_hits[attacker][defender]: float = hits
    return attacker_to_defender_to_hits


def get_potential_threats(chosen_pokemon, level, opponent_pokemon):
    opponent_to_pokemon_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            opponent_pokemon,
            chosen_pokemon,
            level,
            True
        )
    pokemon_to_opponent_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            chosen_pokemon,
            opponent_pokemon,
            level,
            False
        )
    potential_threats: set[Pokemon] = set()
    for opponent, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        opponent: Pokemon
        pokemon_to_hits: dict[Pokemon, tuple[float, float]]
        for player_pokemon, hits in pokemon_to_hits.items():
            player_pokemon: Pokemon
            hits: float
            hits_against_opponent: float = pokemon_to_opponent_to_hits[player_pokemon][opponent]
            # TODO speed test maybe?
            if ceil(hits_against_opponent - 1) >= ceil(hits):
                potential_threats.add(opponent)
    return list(potential_threats)


def is_valid_round(pokemon: Pokemon, round_number: int) -> bool:
    parts = pokemon.unique_key.split('_')
    return int(parts[1]) == round_number


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
