import json
from math import inf
from os.path import exists

import cattr

from config import FRESH_POKEMON_RANK_FILE, FRESH_POKEMON_RANK_FILE_ACCURACY
from data_class.BattleResult import BattleResult
from data_class.Category import Category
from data_class.Hits import Hits
from data_class.Move import Move
from data_class.Pokemon import Pokemon, get_stat_for_battle_factory_pokemon, \
    get_max_damage_attacker_can_do_to_defender, implemented_items, \
    get_defense_multipliers_for_types
from data_class.Stat import StatEnum
from data_class.Type import PokemonType
from data_source.PokemonDataSource import get_battle_factory_pokemon
from repository.PokemonTypeRepository import all_pokemon_types


def get_health_gained(
        player_pokemon,
        player_attack,
        player_attack_damage,
        player_first,
        player_max_health,
        player_health,
        player_item,
        is_player,
        player_turns_poisoned
):
    player_health_gained = 0
    if player_item == "Black Sludge":
        if player_pokemon.name not in ["Clefairy", "Clefable", "Kadabra",
                                       "Alakazam"]:
            if ((
                    PokemonType.POISON in player_pokemon.types and not is_player) or
                    (player_item == "Leftovers")
            ):
                player_health_gained += player_max_health / 16
            elif is_player:
                player_health_gained -= player_max_health / 8
    if player_item == "Life Orb":
        player_health_gained -= player_max_health / 10
    if player_turns_poisoned > 0:
        player_health_gained -= player_turns_poisoned * (player_max_health / 16)

    if ((player_item == "Shell Bell") and
            (player_health != 0 or player_first)
    ):
        player_health_gained += player_attack_damage / 8
    if ((player_attack in ["Drain Punch", "Giga Drain", "Mega Drain"]) and
            (player_health != 0 or player_first)
    ):
        player_health_gained += player_attack_damage / 2
    if player_item == "Big Root":
        player_health_gained *= 1.3
    if player_item == "Sitrus Berry" and player_health < player_max_health / 2:
        player_health_gained += player_max_health / 4
        player_pokemon.item = ""


    return player_health_gained


def apply_damage_modifiers(
        defender: Pokemon,
        defender_item: str,
        attacker_attack: Move | None,
        damage: int
):
    if attacker_attack is None:
        return damage
    defender_types: set[PokemonType] = all_pokemon_types[defender.name]
    defender_defense_multipliers: dict[PokemonType, float] = \
        get_defense_multipliers_for_types(defender_types)
    type_multiplier: float = \
        defender_defense_multipliers.get(attacker_attack.move_type, 1.0)
    if (type_multiplier >= 2.0 and
            (attacker_attack.move_type == PokemonType.FIGHTING and
             defender_item == "Chople Berry") or
            (attacker_attack.move_type == PokemonType.FLYING and
             defender_item == "Coba Berry") or
            (attacker_attack.move_type == PokemonType.DARK and
             defender_item == "Colbur Berry") or
            (attacker_attack.move_type == PokemonType.DRAGON and
             defender_item == "Haban Berry") or
            (attacker_attack.move_type == PokemonType.GHOST and
             defender_item == "Kasib Berry") or
            (attacker_attack.move_type == PokemonType.FIRE and
             defender_item == "Occa Berry") or
            (attacker_attack.move_type == PokemonType.WATER and
             defender_item == "Passho Berry") or
            (attacker_attack.move_type == PokemonType.PSYCHIC and
             defender_item == "Payapa Berry") or
            (attacker_attack.move_type == PokemonType.GRASS and
             defender_item == "Rindo Berry") or
            (attacker_attack.move_type == PokemonType.GROUND and
             defender_item == "Shuca Berry") or
            (attacker_attack.move_type == PokemonType.ELECTRIC and
             defender_item == "Wacan Berry") or
            (attacker_attack.move_type == PokemonType.ICE and
             defender_item == "Yache Berry") or
            (attacker_attack.move_type == PokemonType.ROCK and
             defender_item == "Charti Berry")
    ):
        damage *= 0.5
    return damage


def get_pokemon_to_pokemon_they_can_beat(
        set_number: int,
        level: int,
        worst_case: bool
) -> dict[str, BattleResult]:
    frontier_pokemon: dict[str, Pokemon] = get_battle_factory_pokemon()
    winner_to_defeated: dict[str, BattleResult] = dict()
    set_numbers: list[int] = [set_number - 2, set_number - 1, set_number,
                              set_number + 1]
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
        if player_pokemon.item == "Choice Scarf":
            player_speed_stat *= 1.5
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
            if opponent_pokemon.item == "Choice Scarf":
                opponent_speed_stat *= 1.5
            player_first: bool = player_speed_stat > opponent_speed_stat
            if opponent_pokemon.item == "Quick Claw":
                player_first = False
            opponent_max_health: int = get_stat_for_battle_factory_pokemon(
                opponent_pokemon,
                level,
                StatEnum.HEALTH,
            )
            opponent_health = opponent_max_health
            if player_pokemon.item not in implemented_items or \
                    opponent_pokemon.item not in implemented_items:
                raise Exception(
                    f"Item {player_pokemon.item} or {opponent_pokemon.item} not implemented")
            opponent_attack_damage, opponent_attack = \
                get_max_damage_attacker_can_do_to_defender(
                    attacker=opponent_pokemon,
                    defender=player_pokemon,
                    level=level,
                    random=1.0,
                    accuracy=0,
                    is_poisoned=False
                )
            player_attack_damage, player_attack = \
                get_max_damage_attacker_can_do_to_defender(
                    attacker=player_pokemon,
                    defender=opponent_pokemon,
                    level=level,
                    random=0.85 if worst_case else 1.0,
                    accuracy=100 if worst_case else 0,
                    is_poisoned=False
                )
            hits_taken: float = inf
            if opponent_attack_damage != 0:
                hits_taken: float = player_max_health / opponent_attack_damage

            hits_given = inf
            if player_attack_damage != 0:
                hits_given: float = opponent_health / player_attack_damage
            hits: Hits = Hits(hits_taken=hits_taken, hits_given=hits_given)

            player_health: int = player_max_health

            if player_pokemon.item == "Focus Sash" and opponent_attack_damage > player_max_health:
                player_health = opponent_attack_damage + 1
            if opponent_pokemon.item == "Focus Sash" and player_attack_damage > opponent_max_health:
                opponent_health = player_attack_damage + 1
            # TODO pluck and bug bite will eat berries
            if opponent_attack_damage != 0 or player_attack_damage != 0:
                opponent_turns_poisoned = -1
                player_turns_poisoned = -1
                while player_health > 0 and opponent_health > 0:
                    actual_player_damage = player_attack_damage
                    actual_opponent_damage = opponent_attack_damage
                    if not player_pokemon.item == "":
                        actual_opponent_damage = apply_damage_modifiers(
                            defender=player_pokemon,
                            defender_item=player_pokemon.item,
                            attacker_attack=opponent_attack,
                            damage=opponent_attack_damage
                        )
                        if actual_opponent_damage != opponent_attack_damage:
                            player_pokemon.item = ""


                        if player_health <= player_max_health / 4:
                            if player_attack:
                                player_move_is_special = player_attack.category == Category.SPECIAL
                                if ((player_pokemon.item == "Liechi Berry" and
                                     not player_move_is_special) or
                                        (player_pokemon.item == "Petaya Berry" and
                                         player_move_is_special)
                                ):
                                    actual_player_damage *= 1.5
                                    player_pokemon.item = ""
                            if player_pokemon.item == "Salac Berry":
                                player_speed_stat *= 1.5
                                player_first = player_speed_stat > opponent_speed_stat
                                player_pokemon.item = ""

                        if player_attack and player_attack.name in ["Sky Attack", "Solarbeam"]:
                            player_pokemon.item = ""
                            player_attack_damage, player_attack = \
                                get_max_damage_attacker_can_do_to_defender(
                                    attacker=player_pokemon,
                                    defender=opponent_pokemon,
                                    level=level,
                                    random=0.85 if worst_case else 1.0,
                                    accuracy=100 if worst_case else 0,
                                    is_poisoned=player_turns_poisoned > -1
                                )

                    if not opponent_pokemon.item == "":
                        actual_player_damage = apply_damage_modifiers(
                            defender=opponent_pokemon,
                            defender_item=opponent_pokemon.item,
                            attacker_attack=player_attack,
                            damage=player_attack_damage
                        )
                        if actual_player_damage != player_attack_damage:
                            opponent_pokemon.item = ""

                        if (((opponent_health <= opponent_max_health / 4) or
                             (opponent_health <= opponent_health / 2 and
                              (opponent_pokemon.name in
                               ["Shuckle", "Zigzagoon", "Linoone"])))
                        ):
                            if opponent_attack:
                                opponent_move_is_special = opponent_attack.category == Category.SPECIAL
                                if ((opponent_pokemon.item == "Liechi Berry" and
                                     not opponent_move_is_special) or
                                        (opponent_pokemon.item == "Petaya Berry" and
                                         opponent_move_is_special)
                                ):
                                    actual_opponent_damage *= 1.5
                                    opponent_pokemon.item = ""
                            if opponent_pokemon.item == "Salac Berry":
                                opponent_speed_stat *= 1.5
                                player_first = player_speed_stat > opponent_speed_stat
                                opponent_pokemon.item = ""
                        if opponent_attack and opponent_attack.name in ["Sky Attack", "Solarbeam"]:
                            opponent_pokemon.item = ""
                            opponent_attack_damage, opponent_attack = \
                                get_max_damage_attacker_can_do_to_defender(
                                    attacker=opponent_pokemon,
                                    defender=player_pokemon,
                                    level=level,
                                    random=1.0,
                                    accuracy=0,
                                    is_poisoned=opponent_turns_poisoned > -1
                                )

                    player_health: int = player_health - actual_opponent_damage
                    opponent_health: int = opponent_health - actual_player_damage

                    if player_pokemon.item == "Metronome":
                        actual_player_damage *= 1.1
                    if opponent_pokemon.item == "Metronome":
                        actual_player_damage *= 1.1

                    if (player_pokemon.item == "Toxic Orb" and
                            PokemonType.POISON not in player_pokemon.types
                    ):
                        player_turns_poisoned += 1

                    if (opponent_pokemon.item == "Toxic Orb" and
                            PokemonType.POISON not in opponent_pokemon.types
                    ):
                        opponent_turns_poisoned += 1

                    player_health_gained = get_health_gained(
                        player_pokemon=player_pokemon,
                        player_attack=player_attack,
                        player_attack_damage=player_attack_damage,
                        player_first=player_first,
                        player_max_health=player_max_health,
                        player_health=player_health,
                        player_item=player_pokemon.item,
                        is_player=True,
                        player_turns_poisoned=player_turns_poisoned
                    )
                    player_health += player_health_gained
                    if player_health > player_max_health:
                        player_health = player_max_health
                    opponent_health_gained = get_health_gained(
                        player_pokemon=opponent_pokemon,
                        player_attack=opponent_attack,
                        player_attack_damage=opponent_attack_damage,
                        player_max_health=opponent_max_health,
                        player_first=not player_first,
                        player_health=opponent_health,
                        player_item=opponent_pokemon.item,
                        is_player=False,
                        player_turns_poisoned=player_turns_poisoned
                    )
                    opponent_health += opponent_health_gained
                    if opponent_health > opponent_max_health:
                        opponent_health = opponent_max_health
                    # End the battle if no progress is being made
                    if (actual_opponent_damage <= player_health_gained and
                        actual_player_damage <= opponent_health_gained
                    ):
                        player_health = 0

                    if player_pokemon.item == "Iron Ball":
                        player_pokemon.item = ""
                        opponent_attack_damage, opponent_attack = \
                            get_max_damage_attacker_can_do_to_defender(
                                attacker=player_pokemon,
                                defender=opponent_pokemon,
                                level=level,
                                random=1.0,
                                accuracy=0,
                                is_poisoned=player_turns_poisoned > -1
                            )
                    if opponent_pokemon.item == "Iron Ball":
                        opponent_pokemon.item = ""
                        opponent_attack_damage, opponent_attack = \
                            get_max_damage_attacker_can_do_to_defender(
                                attacker=opponent_pokemon,
                                defender=player_pokemon,
                                level=level,
                                random=1.0,
                                accuracy=0,
                                is_poisoned=opponent_turns_poisoned > -1
                            )


            else:
                player_health: int = 0
            if player_health > 0 or \
                    (
                            player_health <= 0 and
                            opponent_health <= 0 and
                            player_first
                    ):
                win_results[opponent_pokemon_id] = hits
            else:
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
            all_sets_winners_accuracy = cattr.structure(
                json.load(f),
                dict[int, dict[str, BattleResult]]
            )
    return all_sets_winners_accuracy


if __name__ == "__main__":
    all_winners = load_pokemon_ranks()
    all_winners_accuracy = load_pokemon_ranks_accuracy()
    for g_set_number in range(0, 8):
        print("Set " + str(g_set_number) + ":")
        g_winners = all_winners[g_set_number]
        g_winners_accuracy = all_winners_accuracy[g_set_number]
        print(
            {
                k: v for k, v in
                sorted(
                    g_winners.items(),
                    reverse=True,
                    key=lambda e: e[0]
                )
            }
        )
        print(
            {
                k: v for k, v in
                sorted(
                    g_winners_accuracy.items(),
                    reverse=True,
                    key=lambda e: e[1]
                )
            }
        )
