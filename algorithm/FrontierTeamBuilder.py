import json
from math import inf
from os.path import exists

import cattr

from config import FRESH_POKEMON_RANK_FILE, FRESH_POKEMON_RANK_FILE_ACCURACY
from data_class.BattleResult import BattleResult
from data_class.Hits import Hits
from data_class.Pokemon import Pokemon, get_stat_for_battle_factory_pokemon, \
    get_max_damage_attacker_can_do_to_defender
from data_class.Stat import StatEnum
from data_source.PokemonDataSource import get_battle_factory_pokemon


def print_sorted_win_rates(pokemon_list: list[Pokemon]):
    if len(all_sets_winners) == 0:
        load_pokemon_ranks()
    if len(all_sets_winners_accuracy) == 0:
        load_pokemon_ranks_accuracy()
    filtered_winners: dict[str, BattleResult] = {}
    filtered_winners_accuracy: dict[str, BattleResult] = {}
    for pokemon in pokemon_list:
        pokemon: Pokemon
        pokemon_id: str = pokemon.unique_id
        parts: list[str] = pokemon_id.split('_')
        set_number: int = int(parts[1])
        winners: dict[str, BattleResult] = all_sets_winners[set_number]
        winners_accuracy: dict[str, BattleResult] = all_sets_winners_accuracy[
            set_number]
        filtered_winners[pokemon_id]: BattleResult = winners.get(pokemon_id, [])
        filtered_winners_accuracy[
            pokemon_id]: BattleResult = winners_accuracy.get(pokemon_id, [])
    sorted_scores: dict[str, float] = dict(
        sorted(
            ((unique_key, battle_results.win_rate)
             for unique_key, battle_results in filtered_winners.items()),
            key=lambda e: e[1],
            reverse=True
        )
    )
    sorted_scores_accuracy: dict[str, float] = dict(
        sorted(
            ((unique_key, battle_results.win_rate)
             for unique_key, battle_results in
             filtered_winners_accuracy.items()),
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
) -> dict[str, BattleResult]:

    # TODO Chikorita v Aron does not have a recorded battle result
    frontier_pokemon: dict[str, Pokemon] = get_battle_factory_pokemon()
    winner_to_defeated: dict[str, BattleResult] = dict()
    set_numbers: list[int] = [set_number - 1, set_number, set_number + 1]
    set_pokemon = {k: v for k, v in frontier_pokemon.items() if
                   v.set_number in set_numbers}
    for player_pokemon_id, player_pokemon in set_pokemon.items():
        player_pokemon_id: str
        player_pokemon: Pokemon
        player_speed_stat: int = get_stat_for_battle_factory_pokemon(
            player_pokemon,
            level,
            StatEnum.SPEED
        )
        player_max_health: int = get_stat_for_battle_factory_pokemon(
            player_pokemon,
            level,
            StatEnum.HEALTH
        )
        win_results: dict[str, Hits] = dict()
        lose_results: dict[str, Hits] = dict()
        for opponent_pokemon_id, opponent_pokemon in set_pokemon.items():
            opponent_pokemon_id: str
            opponent_pokemon: Pokemon
            # Who is faster?
            opponent_speed_stat: int = get_stat_for_battle_factory_pokemon(
                opponent_pokemon,
                level,
                StatEnum.SPEED,
            )
            player_first: bool = player_speed_stat > opponent_speed_stat
            opponent_health: int = get_stat_for_battle_factory_pokemon(
                opponent_pokemon,
                level,
                StatEnum.HEALTH,
            )
            opponent_attack_damage: int = get_max_damage_attacker_can_do_to_defender(
                attacker=opponent_pokemon,
                defender=player_pokemon,
                level=level,
                random=1.0,
                accuracy=0
            )
            player_attack_damage: int = get_max_damage_attacker_can_do_to_defender(
                attacker=player_pokemon,
                defender=opponent_pokemon,
                level=level,
                random=0.85 if worst_case else 1.0,
                accuracy=100 if worst_case else 0
            )

            hits_taken: float = inf
            if opponent_attack_damage != 0:
                hits_taken: float = player_max_health / opponent_attack_damage

            hits_given = inf
            if player_attack_damage != 0:
                hits_given: float = opponent_health / player_attack_damage
            hits: Hits = Hits(hits_taken=hits_taken, hits_given=hits_given)

            player_health: int = player_max_health
            if opponent_attack_damage != 0 or player_attack_damage != 0:
                while player_health > 0 and opponent_health > 0:
                    player_health: int = player_health - opponent_attack_damage
                    opponent_health: int = opponent_health - player_attack_damage
            else:
                player_health: int = 0
            if player_health > 0 or \
                    (
                            player_health <= 0 and
                            opponent_health <= 0 and
                            player_first
                    ):
                win_results[opponent_pokemon_id] = hits
            else :
                lose_results[opponent_pokemon_id] = hits
        winner_to_defeated[player_pokemon_id]: BattleResult = \
            BattleResult(
                winner_id=player_pokemon_id,
                win_rate=len(win_results) / len(set_pokemon),
                win_results=win_results,
                lose_results=lose_results,
            )
    return winner_to_defeated


all_sets_winners: dict[int, dict[str, BattleResult]] = {}


def load_pokemon_ranks() -> dict[int, dict[str, BattleResult]]:
    global all_sets_winners
    if len(all_sets_winners) != 0:
        return all_sets_winners
    if not exists(FRESH_POKEMON_RANK_FILE):
        level: int = 50
        data: dict[int, dict[str, BattleResult]] = {}
        for set_number in range(8):
            winners: dict[
                str, BattleResult] = get_pokemon_to_pokemon_they_can_beat(
                set_number=set_number,
                level=level,
                worst_case=False
            )
            for winner, battle_results in winners.items():
                if len(battle_results.win_results) > 0:
                    sorted_battle_result_results = dict(
                        sorted(
                            battle_results.win_results.items(),
                            key=lambda item:
                            item[1].hits_taken / item[1].hits_given
                        )
                    )
                    battle_results.win_results = sorted_battle_result_results

            sorted_winners: dict[str, BattleResult] = \
                {k: v for k, v in
                 sorted(winners.items(), key=lambda e: e[1].win_rate,
                        reverse=True)}
            data[set_number]: dict[str, BattleResult] = sorted_winners
        with open(FRESH_POKEMON_RANK_FILE, 'w') as f:
            json.dump(cattr.unstructure(data), f, indent=4)
        all_sets_winners = data
    else:
        with open(FRESH_POKEMON_RANK_FILE, "r") as f:
            all_sets_winners = cattr.structure(
                json.load(f),
                dict[int, dict[str, BattleResult]]
            )
    return all_sets_winners


all_sets_winners_accuracy: dict[int, dict[str, BattleResult]] = {}


def load_pokemon_ranks_accuracy() -> dict[int, dict[str, BattleResult]]:
    global all_sets_winners_accuracy
    if len(all_sets_winners_accuracy) != 0:
        return all_sets_winners_accuracy

    if not exists(FRESH_POKEMON_RANK_FILE_ACCURACY):
        level: int = 50
        data: dict[int, dict[str, BattleResult]] = {}
        for set_number in range(8):
            winners: dict[
                str, BattleResult] = get_pokemon_to_pokemon_they_can_beat(
                set_number=set_number,
                level=level,
                worst_case=True
            )
            for winner, battle_results in winners.items():
                if len(battle_results.win_results) > 0:
                    sorted_battle_result_results = dict(
                        sorted(
                            battle_results.win_results.items(),
                            key=lambda item:
                            item[1].hits_taken / item[1].hits_given
                        )
                    )
                    battle_results.win_results = sorted_battle_result_results

            sorted_winners: dict[str, BattleResult] = \
                {k: v for k, v in
                 sorted(winners.items(), key=lambda e: e[1].win_rate,
                        reverse=True)}
            data[set_number]: dict[str, BattleResult] = sorted_winners
        with open(FRESH_POKEMON_RANK_FILE_ACCURACY, 'w') as f:
            json.dump(cattr.unstructure(data), f, indent=4)
        all_sets_winners_accuracy = data
    else:
        with open(FRESH_POKEMON_RANK_FILE_ACCURACY, "r") as f:
            all_sets_winners_accuracy = cattr.structure(json.load(f), dict[
                int, dict[str, BattleResult]])
    return all_sets_winners_accuracy


if __name__ == "__main__":
    all_winners = load_pokemon_ranks()
    all_winners_accuracy = load_pokemon_ranks_accuracy()
    for g_set_number in range(0, 8):
        print("Set " + str(g_set_number) + ":")
        g_winners = all_winners[g_set_number]
        g_winners_accuracy = all_winners_accuracy[g_set_number]
        print({k: v for k, v in
               sorted(g_winners.items(), reverse=True, key=lambda e: e[0])})
        print({k: v for k, v in sorted(g_winners_accuracy.items(), reverse=True,
                                       key=lambda e: e[1])})
