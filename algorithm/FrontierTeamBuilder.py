from collections import defaultdict

from data_class.Category import Category
from data_class.Move import LearnableMove
from data_class.Pokemon import Pokemon, get_defense_multipliers_for_type
from data_class.Stat import StatEnum, get_stat_for_battle_frontier_pokemon, get_non_health_stat, NatureEnum, \
    get_health_stat
from data_class.Type import pokemon_types, PokemonType
from data_source.BattleFrontierSetDataSource import get_battle_frontier_sets
from data_source.MoveSetDataSource import get_move_sets
from data_source.PokemonTypeDataSource import get_pokemon_types
from repository.BaseStatRepository import all_pokemon_stats
from repository.MoveRepository import get_all_moves
from repository.PokemonMoveSetRepository import get_all_move_sets
from repository.PokemonTypeRepository import all_pokemon_types
from repository.TypeChartRepository import type_chart_defend


type_to_defense_multipliers: dict[frozenset[PokemonType], [dict[PokemonType], float]] = {}


def get_defense_multipliers_for_types(defender_types: frozenset[PokemonType]):
    defense_multipliers = type_to_defense_multipliers.get(defender_types)
    if defense_multipliers is None:
        if len(defender_types) == 1:
            defense_multipliers = None
        else:
            defense_multipliers = defaultdict(lambda: 1.0)
        for defender_type in defender_types:
            defense_multipliers = get_defense_multipliers_for_type(defender_type, defense_multipliers)
        type_to_defense_multipliers[defender_types] = defense_multipliers
    return defense_multipliers


def get_max_damage_frontier_pokemon_can_do_to_defender(
        set_number: int,
        attacker: Pokemon,
        defender: str,
        level: int
) -> float:
    defender_types = all_pokemon_types[defender]
    defender_defense_multipliers = get_defense_multipliers_for_types(frozenset(defender_types))
    max_damage = 0
    for pokemon_move in attacker.moves:
        is_special = pokemon_move.category is Category.SPECIAL
        if not is_special:
            attack_stat = get_stat_for_battle_frontier_pokemon(
                set_number,
                attacker,
                level,
                StatEnum.ATTACK
            )
            base_defense = all_pokemon_stats[defender].defense
            defense_stat = get_non_health_stat(
                base=base_defense,
                iv=0,
                ev=0,
                nature="lonely",
                level=level,
                stat_type=StatEnum.DEFENSE
            )
        else:
            attack_stat = get_stat_for_battle_frontier_pokemon(
                set_number,
                attacker,
                level,
                StatEnum.SPECIAL_ATTACK
            )
            base_defense = all_pokemon_stats[defender].special_defense
            defense_stat = get_non_health_stat(
                base=base_defense,
                iv=0,
                ev=0,
                nature="naughty",
                level=level,
                stat_type=StatEnum.SPECIAL_DEFENSE
            )
        damage = (
                         (
                                 (((2.0 * level) / 5.0) + 2.0) *
                                 pokemon_move.power *
                                 (attack_stat / defense_stat)
                         ) / 50.0 + 2
                 ) * defender_defense_multipliers[pokemon_move.move_type]

        if pokemon_move.move_type in attacker.types:
            damage = damage * 1.5

        if pokemon_move.power == 0:
            damage = 0

        max_damage = max(damage, max_damage)

    return max_damage


def get_best_player_moves(attacker_moves):
    category_and_type_to_move = dict()
    all_moves = get_all_moves
    for learnable_move in attacker_moves:
        move = all_moves[learnable_move["name"]]
        if move.accuracy == 100 and move.category != Category.STATUS and learnable_move["level"] <= 50:
            key = (move.category, move.move_type)
            current_best = category_and_type_to_move.get(key)
            if current_best is None or move.power > current_best.power:
                category_and_type_to_move[key] = move
    return list(category_and_type_to_move.values())


name_to_best_moves = defaultdict(lambda: list())


def get_max_damage_attacker_can_do_to_frontier_pokemon(
        set_number: int,
        attacker_name: str,
        defender: Pokemon,
        level: int
):
    pokemon_to_moves = get_all_move_sets
    defender_types = all_pokemon_types[defender.name]
    defender_defense_multipliers = get_defense_multipliers_for_types(frozenset(defender_types))
    max_damage = 0
    best_moves = name_to_best_moves[attacker_name]
    if len(best_moves) == 0:
        attacker_moves = pokemon_to_moves[attacker_name]
        best_moves = get_best_player_moves(attacker_moves)

    attacker_types = all_pokemon_types[attacker_name]
    for pokemon_move in best_moves:
        is_special = pokemon_move.category is Category.SPECIAL
        if not is_special:
            base_attack = all_pokemon_stats[attacker_name].attack
            attack_stat = get_non_health_stat(
                base=base_attack,
                iv=0,
                ev=0,
                nature="lonely",
                level=level,
                stat_type=StatEnum.ATTACK
            )
            defense_stat = get_stat_for_battle_frontier_pokemon(
                set_number,
                defender,
                level,
                StatEnum.DEFENSE
            )
        else:
            base_attack = all_pokemon_stats[attacker_name].special_attack
            attack_stat = get_non_health_stat(
                base=base_attack,
                iv=0,
                ev=0,
                nature="lonely",
                level=level,
                stat_type=StatEnum.SPECIAL_ATTACK
            )
            defense_stat = get_stat_for_battle_frontier_pokemon(
                set_number,
                defender,
                level,
                StatEnum.SPECIAL_DEFENSE
            )
        damage = (
                         (
                                 (((2.0 * level) / 5.0) + 2.0) *
                                 pokemon_move.power *
                                 (attack_stat / defense_stat)
                         ) / 50.0 + 2
                 ) * defender_defense_multipliers[pokemon_move.move_type]

        if pokemon_move.move_type in attacker_types:
            damage = damage * 1.5

        if pokemon_move.power == 0:
            damage = 0

        max_damage = max(damage, max_damage)
    return max_damage


def get_pokemon_that_can_beat_set(set_number, level):
    frontier_pokemon = get_battle_frontier_sets()[set_number]
    winner_to_number_of_wins = defaultdict(lambda: 0)
    for opponent_pokemon in frontier_pokemon:
        winners_against_single = set()
        for player_pokemon in all_pokemon_stats.keys():
            # Who is faster?
            base_speed = all_pokemon_stats[player_pokemon].speed
            player_speed_stat = get_non_health_stat(
                base=base_speed,
                iv=0,
                ev=0,
                nature="brave",
                level=level,
                stat_type=StatEnum.SPEED
            )
            opponent_speed_stat = get_stat_for_battle_frontier_pokemon(
                set_number,
                opponent_pokemon,
                level,
                StatEnum.SPEED
            )
            player_first = player_speed_stat > opponent_speed_stat
            base_health = all_pokemon_stats[player_pokemon].health
            player_health_stat = get_health_stat(
                base=base_health,
                iv=0,
                ev=0,
                level=level
            )
            opponent_health_stat = get_stat_for_battle_frontier_pokemon(
                set_number,
                opponent_pokemon,
                level,
                StatEnum.HEALTH
            )
            opponent_attack_damage = get_max_damage_frontier_pokemon_can_do_to_defender(
                set_number=set_number,
                attacker=opponent_pokemon,
                defender=player_pokemon,
                level=level
            )
            player_attack_damage = get_max_damage_attacker_can_do_to_frontier_pokemon(
                set_number=set_number,
                attacker_name=player_pokemon,
                defender=opponent_pokemon,
                level=level
            )
            if opponent_attack_damage != 0 or player_attack_damage != 0:
                while player_health_stat > 0 and opponent_health_stat > 0:
                    player_health_stat = player_health_stat - opponent_attack_damage
                    opponent_health_stat = opponent_health_stat - player_attack_damage
            else:
                player_health_stat = 0
            if player_health_stat > 0 or \
                    (
                            player_health_stat == 0 and
                            opponent_health_stat == 0 and
                            player_speed_stat > opponent_speed_stat
                    ):
                winners_against_single.add(player_pokemon)
        for winner in winners_against_single:
            winner_to_number_of_wins[winner] += 1
    return winner_to_number_of_wins


def __get_equation__(level, set_number, pokemon, move):
    if move.category == Category.PHYSICAL:
        attack_stat = get_stat_for_battle_frontier_pokemon(set_number, pokemon, level, StatEnum.ATTACK)
    else:
        attack_stat = get_stat_for_battle_frontier_pokemon(set_number, pokemon, level, StatEnum.SPECIAL_ATTACK)
    return (((2.0 * level) / 5.0) + 2.0) * move.power * attack_stat


def __get_base_health__(level, hp_stat):
    return (((hp_stat - 10 - level) * 100.0) / level) / 2.0


def __get_base_defense_to_base_health__(level, set_number, pokemon):
    base_defense_to_base_health = defaultdict(lambda: -9999)
    base_special_defense_to_base_health = defaultdict(lambda: -9999)
    for move in pokemon.moves:
        # defense_stat * ((50 * health_stat) - 400)
        equation = __get_equation__(level, set_number, pokemon, move)
        if move.category == Category.PHYSICAL:
            lowest_base_defense = 5
            highest_base_defense = 230
            for base_defense in range(lowest_base_defense, highest_base_defense + 1):
                defense_stat = get_non_health_stat(
                    base=base_defense,
                    iv=0,
                    ev=0,
                    nature="lonely",
                    level=level,
                    stat_type=StatEnum.DEFENSE
                )
                # defense_stat * ((50 * health_stat) - 400)
                hp_stat = ((equation / defense_stat) + 400.0) / 50.0
                base_defense_to_base_health[base_defense] = \
                    max(__get_base_health__(level, hp_stat), base_defense_to_base_health[base_defense])
        elif move.category == Category.SPECIAL:
            lowest_base_special_defense = 20
            highest_base_special_defense = 230
            for base_special_defense in range(lowest_base_special_defense, highest_base_special_defense + 1):
                special_defense_stat = get_non_health_stat(
                    base=base_special_defense,
                    iv=0,
                    ev=0,
                    nature="naughty",
                    level=level,
                    stat_type=StatEnum.SPECIAL_DEFENSE
                )
                # defense_stat * ((50 * health_stat) - 400)
                hp_stat = ((equation / special_defense_stat) + 400.0) / 50.0
                base_special_defense_to_base_health[base_special_defense] = \
                    max(__get_base_health__(level, hp_stat), base_special_defense_to_base_health[base_special_defense])
    return base_defense_to_base_health, base_special_defense_to_base_health


def __get_pokemon_with_greater_base_stats__(base_defense_to_base_health, special):
    best = set()
    for pokemon, base_stats in all_pokemon_stats.items():
        for defense, health in base_defense_to_base_health.items():
            if not special:
                if base_stats.defense > defense and base_stats.health > health:
                    best.add(pokemon)
            else:
                if base_stats.special_defense > defense and base_stats.health > health:
                    best.add(pokemon)

    best = [b for b in sorted(best)]
    return best


def get_base_defense_to_base_health_charts(level, set_number):
    assert 0 <= set_number < 8
    frontier_pokemon_to_base_defense_to_base_health = defaultdict(lambda: list())
    frontier_pokemon = get_battle_frontier_sets()[set_number]
    for pokemon in frontier_pokemon:
        frontier_pokemon_to_base_defense_to_base_health[pokemon].append(
            __get_base_defense_to_base_health__(level, set_number, pokemon)
        )

    base_defense_to_base_health = defaultdict(lambda: -9999)
    base_special_defense_to_base_health = defaultdict(lambda: -9999)
    for frontier_base_defense_to_base_health in frontier_pokemon_to_base_defense_to_base_health.values():
        for base_defense, base_health in frontier_base_defense_to_base_health[0][0].items():
            base_defense_to_base_health[base_defense] = max(
                base_defense_to_base_health[base_defense],
                base_health
            )
        for base_special_defense, base_health in frontier_base_defense_to_base_health[0][1].items():
            base_special_defense_to_base_health[base_special_defense] = max(
                base_special_defense_to_base_health[base_special_defense],
                base_health
            )

    print("Base Defense to Base Health")
    for defense, health in base_defense_to_base_health.items():
        print("Defense: " + str(defense) + " - Health: " + str(health))
    print()

    print("Base Special Defense to Base Health")
    for defense, health in base_special_defense_to_base_health.items():
        print("Special Defense: " + str(defense) + " - Health: " + str(health))
    print()

    # best1 = __get_pokemon_with_greater_base_stats__(base_defense_to_base_health, False)
    # best2 = __get_pokemon_with_greater_base_stats__(base_special_defense_to_base_health, True)
    # best = sorted(set(best1).intersection(set(best2)))
    # for i, b in enumerate(best):
    #     print(str(i) + ": " + b)


def __get_defense_to_health__(level, set_number, pokemon):
    defense_to_health = defaultdict(lambda: -9999)
    special_defense_to_health = defaultdict(lambda: -9999)
    for move in pokemon.moves:
        # defense_stat * ((50 * health_stat) - 400)
        equation = __get_equation__(level, set_number, pokemon, move)
        if move.category == Category.PHYSICAL:
            lowest_base_defense = 5
            highest_base_defense = 230
            for base_defense in range(lowest_base_defense, highest_base_defense + 1):
                defense_stat = get_non_health_stat(
                    base=base_defense,
                    iv=0,
                    ev=0,
                    nature="lonely",
                    level=level,
                    stat_type=StatEnum.DEFENSE
                )
                # defense_stat * ((50 * health_stat) - 400)
                hp_stat = ((equation / defense_stat) + 400.0) / 50.0
                defense_to_health[defense_stat] = \
                    max(hp_stat, defense_to_health[defense_stat])
        elif move.category == Category.SPECIAL:
            lowest_base_special_defense = 20
            highest_base_special_defense = 230
            for base_special_defense in range(lowest_base_special_defense, highest_base_special_defense + 1):
                special_defense_stat = get_non_health_stat(
                    base=base_special_defense,
                    iv=0,
                    ev=0,
                    nature="naughty",
                    level=level,
                    stat_type=StatEnum.SPECIAL_DEFENSE
                )
                # defense_stat * ((50 * health_stat) - 400)
                hp_stat = ((equation / special_defense_stat) + 400.0) / 50.0
                special_defense_to_health[special_defense_stat] = \
                    max(hp_stat, special_defense_to_health[special_defense_stat])
    return defense_to_health, special_defense_to_health


def __get_pokemon_with_greater_stats__(level, defense_to_health, special):
    best = set()
    for pokemon, base_stats in all_pokemon_stats.items():
        for defense, health in defense_to_health.items():
            if not special:
                defense_stat = get_non_health_stat(
                    base=base_stats.defense,
                    iv=0,
                    ev=0,
                    nature="lonely",
                    level=level,
                    stat_type=StatEnum.DEFENSE
                )
            else:
                defense_stat = get_non_health_stat(
                    base=base_stats.special_defense,
                    iv=0,
                    ev=0,
                    nature="naughty",
                    level=level,
                    stat_type=StatEnum.SPECIAL_DEFENSE
                )
            health_stat = get_health_stat(
                base=base_stats.health,
                iv=0,
                ev=0,
                level=level
            )
            if defense_stat > defense and health_stat > health:
                best.add(pokemon)

    best = [b for b in sorted(best)]
    return best


def get_defense_to_health_charts(level, set_number):
    assert 0 <= set_number < 8
    frontier_pokemon_to_damage_tables = defaultdict(lambda: list())
    frontier_pokemon = get_battle_frontier_sets()[set_number]
    for pokemon in frontier_pokemon:
        frontier_pokemon_to_damage_tables[pokemon].append(
            __get_defense_to_health__(level, set_number, pokemon)
        )

    defense_to_health = defaultdict(lambda: -9999)
    special_defense_to_health = defaultdict(lambda: -9999)
    for damage_tables in frontier_pokemon_to_damage_tables.values():
        for defense, health in damage_tables[0][0].items():
            defense_to_health[defense] = max(
                defense_to_health[defense],
                health
            )
        for defense, health in damage_tables[0][1].items():
            special_defense_to_health[defense] = max(
                special_defense_to_health[defense],
                health
            )
    print("Defense to Health")
    for defense, health in defense_to_health.items():
        print("Defense: " + str(defense) + " - Health: " + str(health))
    print()

    print("Special Defense to Health")
    for defense, health in defense_to_health.items():
        print("Special Defense: " + str(defense) + " - Health: " + str(health))
    print()

    # best1 = __get_pokemon_with_greater_stats__(level, defense_to_health, False)
    # best2 = __get_pokemon_with_greater_stats__(level, special_defense_to_health, True)
    # best = sorted(set(best1).intersection(set(best2)))
    # for i, b in enumerate(best):
    #     print(str(i) + ": " + b)


if __name__ == "__main__":
    top_level = 50
    winners = get_pokemon_that_can_beat_set(set_number=7, level=top_level)
    for i in range(0, 8):
        print("Set " + str(i) + ":")
        # get_base_defense_to_base_health_charts(top_level, i)
        # get_defense_to_health_charts(top_level, i)
        winners = get_pokemon_that_can_beat_set(set_number=i, level=top_level)
        print({k: v for k, v in sorted(winners.items(), reverse=True, key=lambda e: e[1])})
