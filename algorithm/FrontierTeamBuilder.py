import json
from collections import defaultdict
from os.path import exists

import cattr

from config import FRESH_POKEMON_RANK_FILE, FRESH_POKEMON_RANK_FILE_ACCURACY
from data_class.Pokemon import Pokemon, get_stat_for_battle_factory_pokemon, \
    get_max_damage_frontier_pokemon_can_do_to_defender
from data_class.Stat import StatEnum
from data_source.PokemonDataSource import get_battle_factory_pokemon, get_number_of_pokemon_in_set


def print_sorted_winners_from_list(pokemon_list: list[Pokemon]):
    if len(all_sets_winners) == 0:
        load_pokemon_ranks()
    if len(all_sets_winners_accuracy) == 0:
        load_pokemon_ranks_accuracy()
    filtered_scores: dict[str, list[str]] = {}
    filtered_scores_accuracy: dict[str, list[str]] = {}
    for pokemon in pokemon_list:
        pokemon: Pokemon
        pokemon_id: str = pokemon.unique_key
        parts: list[str] = pokemon_id.split('_')
        set_number: int = int(parts[1])
        winners: dict[str, list[str]] = all_sets_winners[set_number]
        winners_accuracy: dict[str, list[str]] = all_sets_winners_accuracy[set_number]
        filtered_scores[pokemon_id]: list[str] = winners.get(pokemon_id, [])
        filtered_scores_accuracy[pokemon_id]: list[str] = winners_accuracy.get(pokemon_id, [])
    sorted_scores: dict[str, float] = dict(
        sorted(
            ((k, len(v) / get_number_of_pokemon_in_set(int(k.split('_')[1]))) for k, v in filtered_scores.items()),
            key=lambda e: e[1],
            reverse=True
        )
    )
    sorted_scores_accuracy: dict[str, float] = dict(
        sorted(
            ((k, len(v) / get_number_of_pokemon_in_set(int(k.split('_')[1]))) for k, v in
             filtered_scores_accuracy.items()),
            key=lambda e: e[1],
            reverse=True
        )
    )

    print(sorted_scores)
    print(sorted_scores_accuracy)


def get_pokemon_to_pokemon_they_can_beat(
        set_number: int,
        level: int,
        worst_case: bool
) -> dict[str, list[str]]:
    frontier_pokemon: dict[str, Pokemon] = get_battle_factory_pokemon()
    winner_to_defeated: dict[str, list[str]] = defaultdict(lambda: [])
    set_pokemon = {k: v for k, v in frontier_pokemon.items() if v.set_number == set_number}
    for opponent_pokemon_id, opponent_pokemon in set_pokemon.items():
        opponent_pokemon_id: str
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
        for player_pokemon_id, player_pokemon in set_pokemon.items():
            player_pokemon_id: str
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
            opponent_health: int = opponent_max_health
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
                winner_to_defeated[player_pokemon_id].append(opponent_pokemon_id)
    return winner_to_defeated


all_sets_winners: dict[int, dict[str, list[str]]] = {}


def load_pokemon_ranks() -> dict[int, dict[str, list[str]]]:
    global all_sets_winners
    if len(all_sets_winners) != 0:
        return all_sets_winners
    if not exists(FRESH_POKEMON_RANK_FILE):
        level: int = 50
        data: dict[int, dict[str, list[str]]] = {}
        for set_number in range(8):
            winners: dict[str, list[str]] = get_pokemon_to_pokemon_they_can_beat(
                set_number=set_number,
                level=level,
                worst_case=False
            )
            sorted_winners: dict[str, list[str]] = \
                {k: v for k, v in sorted(winners.items(), key=lambda e: e[1], reverse=True)}
            data[set_number]: dict[str, list[str]] = sorted_winners
        with open(FRESH_POKEMON_RANK_FILE, 'w') as f:
            json.dump(cattr.unstructure(data), f, indent=2)
        all_sets_winners = data
    else:
        with open(FRESH_POKEMON_RANK_FILE, "r") as f:
            all_sets_winners = cattr.structure(json.load(f), dict[int, dict[str, list[str]]])
    return all_sets_winners


all_sets_winners_accuracy: dict[int, dict[str, list[str]]] = {}


def load_pokemon_ranks_accuracy() -> dict[int, dict[str, list[str]]]:
    global all_sets_winners_accuracy
    if len(all_sets_winners_accuracy) != 0:
        return all_sets_winners_accuracy

    if not exists(FRESH_POKEMON_RANK_FILE_ACCURACY):
        level: int = 50
        data: dict[int, dict[str, list[str]]] = {}
        for set_number in range(8):
            winners: dict[str, list[str]] = get_pokemon_to_pokemon_they_can_beat(
                set_number=set_number,
                level=level,
                worst_case=True
            )
            sorted_winners: dict[str, list[str]] = \
                {k: v for k, v in sorted(winners.items(), key=lambda e: e[1], reverse=True)}
            data[set_number]: dict[str, list[str]] = sorted_winners
        with open(FRESH_POKEMON_RANK_FILE_ACCURACY, 'w') as f:
            json.dump(cattr.unstructure(data), f, indent=2)
        all_sets_winners_accuracy = data
    else:
        with open(FRESH_POKEMON_RANK_FILE_ACCURACY, "r") as f:
            all_sets_winners_accuracy = cattr.structure(json.load(f), dict[int, dict[str, list[str]]])
    return all_sets_winners_accuracy


if __name__ == "__main__":
    all_winners = load_pokemon_ranks()
    all_winners_accuracy = load_pokemon_ranks_accuracy()
    for g_set_number in range(0, 8):
        print("Set " + str(g_set_number) + ":")
        g_winners = all_winners[g_set_number]
        g_winners_accuracy = all_winners_accuracy[g_set_number]
        print({k: v for k, v in sorted(g_winners.items(), reverse=True, key=lambda e: e[1])})
        print({k: v for k, v in sorted(g_winners_accuracy.items(), reverse=True, key=lambda e: e[1])})
