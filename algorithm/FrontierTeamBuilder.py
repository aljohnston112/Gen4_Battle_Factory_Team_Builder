import json
from collections import defaultdict
from os.path import exists

import cattr

from config import FRESH_POKEMON_RANK_FILE, FRESH_POKEMON_RANK_FILE_ACCURACY
from data_class.Pokemon import Pokemon, get_stat_for_battle_factory_pokemon, \
    get_max_damage_frontier_pokemon_can_do_to_defender
from data_class.Stat import StatEnum
from data_source.PokemonDataSource import get_battle_factory_pokemon


def print_sorted_winners_from_list(pokemon_list: list[Pokemon]):
    if len(all_sets_winners) == 0:
        load_pokemon_ranks()
    filtered_scores: dict[str, int] = {}
    for pokemon in pokemon_list:
        parts = pokemon.unique_key.split('_')
        set_number = int(parts[1])
        winners: dict[str, int] = all_sets_winners[set_number]
        if pokemon.unique_key in winners:
            filtered_scores[pokemon.unique_key] = winners[pokemon.unique_key]

    sorted_scores: dict[str, int] = dict(sorted(filtered_scores.items(), key=lambda e: e[1], reverse=True))
    print(sorted_scores)


def get_pokemon_that_can_beat_set(
        set_number: int,
        level: int,
        worst_case: bool
):
    frontier_pokemon: dict[str, Pokemon] = get_battle_factory_pokemon()
    winner_to_number_of_wins: dict[str, int] = defaultdict(lambda: 0)
    set_pokemon = {k: v for k, v in frontier_pokemon.items() if v.set_number == set_number}
    for opponent_name, opponent_pokemon in set_pokemon.items():
        opponent_pokemon: Pokemon
        opponent_speed_stat: int = get_stat_for_battle_factory_pokemon(
            opponent_pokemon,
            level,
            StatEnum.SPEED
        )
        opponent_max_health: int = get_stat_for_battle_factory_pokemon(
            opponent_pokemon,
            level,
            StatEnum.HEALTH
        )
        for player_name, player_pokemon in set_pokemon.items():
            player_pokemon: Pokemon
            # Who is faster?
            player_speed_stat: int = get_stat_for_battle_factory_pokemon(
                player_pokemon,
                level,
                StatEnum.SPEED,
            )
            player_first: bool = player_speed_stat > opponent_speed_stat
            player_health: int = get_stat_for_battle_factory_pokemon(
                player_pokemon,
                level,
                StatEnum.HEALTH,
            )
            opponent_attack_damage: int = get_max_damage_frontier_pokemon_can_do_to_defender(
                attacker=opponent_pokemon,
                defender=player_pokemon,
                level=level,
                random=1.0,
                accuracy=0
            )
            player_attack_damage: int = get_max_damage_frontier_pokemon_can_do_to_defender(
                attacker=player_pokemon,
                defender=opponent_pokemon,
                level=level,
                random=0.85 if worst_case else 1.0,
                accuracy=100 if worst_case else 0
            )
            opponent_health = opponent_max_health
            if opponent_attack_damage != 0 or player_attack_damage != 0:
                while player_health > 0 and opponent_health > 0:
                    player_health: int = player_health - opponent_attack_damage
                    opponent_health: int = opponent_health - player_attack_damage
            else:
                player_health: int = 0
            if player_health > 0 or \
                    (
                            player_health == 0 and
                            opponent_max_health == 0 and
                            player_first
                    ):
                winner_to_number_of_wins[player_name] += 1

    return winner_to_number_of_wins


all_sets_winners: dict[int, dict[str, int]] = {}


def load_pokemon_ranks() -> dict[int, dict[str, int]]:
    global all_sets_winners
    if not exists(FRESH_POKEMON_RANK_FILE):
        level: int = 50
        data: dict[int, dict[str, int]] = {}
        for set_number in range(8):
            winners: dict[str, int] = get_pokemon_that_can_beat_set(set_number=set_number, level=level, worst_case=False)
            sorted_winners: dict[str, int] = {k: v for k, v in
                                              sorted(winners.items(), key=lambda e: e[1], reverse=True)}
            data[set_number]: dict[str, int] = sorted_winners
        with open(FRESH_POKEMON_RANK_FILE, 'w') as f:
            json.dump(cattr.unstructure(data), f, indent=2)
        all_sets_winners = data
    else:
        with open(FRESH_POKEMON_RANK_FILE, "r") as f:
            all_sets_winners = cattr.structure(json.load(f), dict[int, dict[str, int]])
    return all_sets_winners


all_sets_winners_accuracy: dict[int, dict[str, int]] = {}


def load_pokemon_ranks_accuracy() -> dict[int, dict[str, int]]:
    global all_sets_winners
    if not exists(FRESH_POKEMON_RANK_FILE_ACCURACY):
        level: int = 50
        data: dict[int, dict[str, int]] = {}
        for set_number in range(8):
            winners: dict[str, int] = get_pokemon_that_can_beat_set(set_number=set_number, level=level, worst_case=True)
            sorted_winners: dict[str, int] = {k: v for k, v in
                                              sorted(winners.items(), key=lambda e: e[1], reverse=True)}
            data[set_number]: dict[str, int] = sorted_winners
        with open(FRESH_POKEMON_RANK_FILE_ACCURACY, 'w') as f:
            json.dump(cattr.unstructure(data), f, indent=2)
        all_sets_winners = data
    else:
        with open(FRESH_POKEMON_RANK_FILE_ACCURACY, "r") as f:
            all_sets_winners = cattr.structure(json.load(f), dict[int, dict[str, int]])
    return all_sets_winners


if __name__ == "__main__":
    all_winners = load_pokemon_ranks()
    all_winners_accuracy = load_pokemon_ranks_accuracy()
    for g_set_number in range(0, 8):
        print("Set " + str(g_set_number) + ":")
        g_winners = all_winners[g_set_number]
        g_winners_accuracy = all_winners_accuracy[g_set_number]
        print({k: v for k, v in sorted(g_winners.items(), reverse=True, key=lambda e: e[1])})
        print({k: v for k, v in sorted(g_winners_accuracy.items(), reverse=True, key=lambda e: e[1])})
