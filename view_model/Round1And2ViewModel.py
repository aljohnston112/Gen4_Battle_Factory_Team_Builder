from collections import defaultdict
from itertools import groupby
from pprint import pp
from typing import List, Dict, DefaultDict

from data_class.Category import Category
from data_class.Pokemon import Pokemon, get_defense_multipliers_for_list, get_max_attack_power_for_list, \
    get_defense_multipliers_for_pokemon, get_defense_multipliers_for_type
from data_class.Stat import get_iv_for_battle_factory, Stat, get_non_health_stat, get_health_stat, StatEnum, \
    get_stat_for_battle_factory_pokemon
from data_class.Type import PokemonType
from repository.MoveRepository import get_all_moves
from repository.PokemonRepository import find_pokemon, all_battle_factory_pokemon
from use_case.PokemonPickerUseCase import PokemonPickerUseCase
from use_case.TeamUseCase import TeamUseCase


def get_max_damage_attacker_can_do_to_defender(
        attacker: Pokemon,
        defender: Pokemon,
        level: int
) -> float:
    defender_defense_multipliers = get_defense_multipliers_for_pokemon(defender)
    max_damage = 0
    for pokemon_move in attacker.moves:
        is_special = pokemon_move.category is Category.SPECIAL
        if not is_special:
            attack_stat = get_stat_for_battle_factory_pokemon(attacker, level, StatEnum.ATTACK)
            defense_stat = get_stat_for_battle_factory_pokemon(defender, level, StatEnum.DEFENSE)
        else:
            attack_stat = get_stat_for_battle_factory_pokemon(attacker, level, StatEnum.SPECIAL_ATTACK)
            defense_stat = get_stat_for_battle_factory_pokemon(defender, level, StatEnum.SPECIAL_DEFENSE)
        damage = (
                         (
                                 (((2.0 * level) / 5.0) + 2.0) *
                                 get_all_moves[pokemon_move.name].power *
                                 (attack_stat / defense_stat)
                         ) / 50.0 + 2
                 ) * 2.0 * defender_defense_multipliers[pokemon_move.move_type]

        if pokemon_move.move_type in attacker.types:
            damage = damage * 1.5

        if pokemon_move.power == 0:
            damage = 0

        max_damage = max(damage, max_damage)

    return max_damage


def get_max_damage_attackers_can_do_to_defenders(
        attacking_pokemon: List[Pokemon],
        defending_pokemon: List[Pokemon],
        level
) -> defaultdict[Pokemon, defaultdict[Pokemon, float]]:
    attacker_to_defender_to_max_damage = defaultdict(
        lambda: defaultdict(lambda: 0.0)
    )
    for attacker in attacking_pokemon:
        for defender in defending_pokemon:
            max_damage = get_max_damage_attacker_can_do_to_defender(
                attacker,
                defender,
                level
            )
            attacker_to_defender_to_max_damage[attacker][defender] = max_damage
    return attacker_to_defender_to_max_damage


def get_pokemon_health(pokemon, level):
    pokemon_to_health = dict()
    for poke in pokemon:
        pokemon_to_health[poke] = get_stat_for_battle_factory_pokemon(
            poke,
            level,
            StatEnum.HEALTH
        )
    return pokemon_to_health


def get_num_hits_attackers_need_do_to_defenders(attackers, defenders, level):
    attacker_to_defender_to_max_damage = get_max_damage_attackers_can_do_to_defenders(
        attackers,
        defenders,
        level
    )
    pokemon_to_health = get_pokemon_health(attackers + defenders, level)
    attacker_to_defender_to_hits = defaultdict(lambda: dict())
    for attacker, defender_to_max_damage in attacker_to_defender_to_max_damage.items():
        for defender, max_damage in defender_to_max_damage.items():
            if max_damage != 0:
                hits = pokemon_to_health[defender] / max_damage
                if hits < 1:
                    hits = 1
            else:
                hits = 9999
            attacker_to_defender_to_hits[attacker][defender] = hits
    return attacker_to_defender_to_hits


def do_round_one(
        pokemon: List[Pokemon],
        opponent_pokemon: List[Pokemon],
        level
) -> None:
    """
    Given a list of pokemon a list of opponents, and their level,
    pokemon are ranked by how likely they are to beat each opponent.
    :param pokemon:
    :param opponent_pokemon:
    :param level:
    :return:
    """
    opponent_to_pokemon_to_hits = get_num_hits_attackers_need_do_to_defenders(
        opponent_pokemon,
        pokemon,
        level
    )

    pokemon_to_opponent_to_hits = get_num_hits_attackers_need_do_to_defenders(
        pokemon,
        opponent_pokemon,
        level
    )

    opponent_to_pokemon_to_rank = defaultdict(lambda: dict())
    for opponent, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        for poke, hits in pokemon_to_hits.items():
            opponent_to_pokemon_to_rank[opponent][poke] = \
                pokemon_to_opponent_to_hits[poke][opponent] / hits

    sorted_opponent_to_pokemon_to_rank = {
        opponent: dict(sorted(pokemon_to_rank.items(), key=lambda x: x[1]))
        for opponent, pokemon_to_rank in opponent_to_pokemon_to_rank.items()
    }

    pp("Team pokemon ranks", sort_dicts=False)
    pp(sorted_opponent_to_pokemon_to_rank)


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


def do_round_two(
        pokemon: List[Pokemon],
        opponent_pokemon: List[Pokemon],
        level
):
    do_round_one(pokemon, opponent_pokemon, level)

    chosen_pokemon = ask_user_to_pick_pokemon(2, pokemon)
    remaining_pokemon = list(
        set(pokemon)
        .difference(set(chosen_pokemon))
    )

    pokemon_list = list(all_battle_factory_pokemon.values())
    uncovered = []
    for poke in pokemon_list:
        for opponent in opponent_pokemon:
            covered = False
            for poke_type in poke.types:
                if poke_type in opponent.types:
                    covered = True
            for opponent_move in opponent.moves:
                for move in poke.moves:
                    if opponent_move.move_type == move.move_type and opponent_move.power > 0:
                        covered = True
            if not covered:
                uncovered.append(poke)

    opponent_to_pokemon_to_hits = get_num_hits_attackers_need_do_to_defenders(
        uncovered,
        remaining_pokemon,
        level
    )

    pokemon_to_opponent_to_hits = get_num_hits_attackers_need_do_to_defenders(
        remaining_pokemon,
        uncovered,
        level
    )

    opponent_to_pokemon_to_rank = defaultdict(lambda: dict())
    for opponent, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        for poke, hits in pokemon_to_hits.items():
            opponent_to_pokemon_to_rank[opponent][poke] = \
                pokemon_to_opponent_to_hits[poke][opponent] / hits

    pokemon_to_rank = defaultdict(lambda: 0)
    for opponent, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        for poke, hits in pokemon_to_hits.items():
            if hits == 9999:
                hits = pokemon_to_rank[poke]
            pokemon_to_rank[poke] = max(pokemon_to_rank[poke], hits)

    sorted_pokemon_to_rank = sorted(pokemon_to_rank.items(), key=lambda x: x[1])

    pp("Team pokemon ranks", sort_dicts=False)
    pp(sorted_pokemon_to_rank)



# def do_round_one(
#         pokemon: List[Pokemon],
#         opponent_pokemon: List[Pokemon],
#         level
# ) -> None:
#     # Remove all duplicates but the lowest set
#     sorted_opponent_pokemon = sorted(opponent_pokemon, key=lambda op: (op.name, op.set_number))
#     grouped_opponent_pokemon = groupby(sorted_opponent_pokemon, key=lambda op: op.name)
#     opponent_pokemon = [
#         min(
#             group,
#             key=lambda op: op.set_number
#         ) for _, group in grouped_opponent_pokemon
#     ]
#
#     print_pokemon_ranks(
#         pokemon,
#         opponent_pokemon,
#         level
#     )


# def print_pokemon_ranks(
#         team_pokemon: List[Pokemon],
#         opponent_pokemon: List[Pokemon],
#         level
# ) -> None:
#     team_pokemon_ranks = rank_team_pokemon_against_opponents(
#         team_pokemon,
#         opponent_pokemon,
#         level
#     )
#     pp("Team pokemon ranks", sort_dicts=False)
#     pp(team_pokemon_ranks)
#
#
# def rank_team_pokemon_against_opponents(
#         team_pokemon,
#         opponent_pokemon,
#         level
# ) -> Dict[str, Dict[Pokemon, int]]:
#     opponent_to_pokemon_attack_rank = rank_attack_of_attackers_against_defenders(
#         team_pokemon,
#         opponent_pokemon,
#         level
#     )
#
#     opponent_to_pokemon_defense_rank = rank_defense_of_defenders_against_attackers(
#         team_pokemon,
#         opponent_pokemon,
#         level
#     )
#
#     pokemon_ranks = rank_based_on_attack_and_defense_rank(
#         opponent_to_pokemon_attack_rank,
#         opponent_to_pokemon_defense_rank,
#         level
#     )
#     return pokemon_ranks
#
#
# def rank_attack_of_attackers_against_defenders(
#         attackers: List[Pokemon],
#         defenders: List[Pokemon],
#         level
# ) -> DefaultDict[Pokemon, Dict[Pokemon, float]]:
#     """
#     Ranks pokemon by how much attackers can do to the defenders.
#     :param level:
#     :param attackers: The attacking pokemon.
#     :param defenders: The defending pokemon.
#     :return:
#     A dictionary of defending pokemon
#     to a rank to list of attacking pokemon dictionary.
#     The lower the rank, the more damage the attacker can do to the defender.
#     """
#     defender_to_attacker_to_max_damage = get_max_damage_attackers_can_do_to_defenders(
#         attackers,
#         defenders,
#         level
#     )
#     pokemon_ranks = rank_by_max_damage(defender_to_attacker_to_max_damage)
#     return pokemon_ranks
#
#
# def rank_defense_of_defenders_against_attackers(
#         defenders: List[Pokemon],
#         attackers: List[Pokemon],
#         level
# ) -> defaultdict[Pokemon, dict[Pokemon, float]]:
#     defender_to_attacker_to_max_damage = get_max_damage_attackers_can_do_to_defenders(
#         attackers,
#         defenders,
#         level
#     )
#
#     # Map from opponent to pokemon to max damage
#     attacker_to_defender_to_max_damage = defaultdict(lambda: defaultdict(lambda: 0.0))
#     for attacker in attackers:
#         for pokemon in defender_to_attacker_to_max_damage.keys():
#             attacker_to_defender_to_max_damage[attacker][pokemon] = \
#                 defender_to_attacker_to_max_damage[pokemon][attacker]
#
#     pokemon_ranks = rank_by_max_damage(
#         attacker_to_defender_to_max_damage,
#         descending=False
#     )
#     return pokemon_ranks
#
#
# def get_max_damage_attackers_can_do_to_defenders(
#         attacking_pokemon: List[Pokemon],
#         defending_pokemon: List[Pokemon],
#         level
# ) -> defaultdict[Pokemon, defaultdict[Pokemon, float]]:
#     defender_to_attacker_to_max_damage = defaultdict(
#         lambda: defaultdict(lambda: 0.0)
#     )
#     for defender in defending_pokemon:
#         attacker_to_max_damage = defaultdict(lambda: 0.0)
#         for attacker in attacking_pokemon:
#             attacker_to_max_damage[attacker] = max_damage_attacker_can_do_to_defender(
#                 attacker,
#                 defender,
#                 level
#             )
#         defender_to_attacker_to_max_damage[defender] = attacker_to_max_damage
#     return defender_to_attacker_to_max_damage
#
#
# def get_max_damage_attackers_can_do_to_type(
#         attacking_pokemon: List[Pokemon],
#         defending_type: PokemonType
# ) -> defaultdict[Pokemon, float]:
#     attacker_to_max_damage = defaultdict(lambda: 0.0)
#     for attacker in attacking_pokemon:
#         attacker_to_max_damage[attacker] = max_damage_attacker_can_do_to_type(
#             attacker,
#             defending_type
#         )
#     return attacker_to_max_damage
#
#
# def max_damage_attacker_can_do_to_type(
#         attacker: Pokemon,
#         defender_type: PokemonType
# ) -> float:
#     opponent_defense_multipliers = get_defense_multipliers_for_type(defender_type)
#     max_damage = 0
#     for pokemon_move in attacker.moves:
#         max_damage = max(
#             opponent_defense_multipliers[pokemon_move.move_type] *
#             get_all_moves[pokemon_move.name].power,
#             max_damage
#         )
#     return max_damage
#
#
# def rank_attackers_by_damage_to_type(
#         defender_type: PokemonType,
#         attackers: List[Pokemon]
# ) -> DefaultDict[int, List[Pokemon]]:
#     attacker_to_max_damage = get_max_damage_attackers_can_do_to_type(
#         attackers,
#         defender_type
#     )
#
#     # Sort by max damage
#     sorted_attacker_to_max_damage = {
#         poke: damage
#         for poke, damage in sorted(
#             (item for item in attacker_to_max_damage.items()),
#             key=lambda item: item[1],
#             reverse=True
#         )
#     }
#
#     # Rank by max damage
#     rank = 1
#     last_damage = next(iter(sorted_attacker_to_max_damage.values()))
#
#     pokemon_ranks = defaultdict(lambda: [])
#     for poke, damage in sorted_attacker_to_max_damage.items():
#         if damage != last_damage:
#             rank = rank + 1
#         pokemon_ranks[rank].append(poke)
#         last_damage = damage
#     return pokemon_ranks
#
#
# def rank_by_max_damage(
#         pokemon_to_pokemon_to_max_damage: defaultdict[Pokemon, defaultdict[Pokemon, float]],
#         descending=True
# ) -> DefaultDict[Pokemon, Dict[Pokemon, float]]:
#     pokemon_ranks = defaultdict(lambda: dict())
#     for pokemon in pokemon_to_pokemon_to_max_damage.keys():
#         # Sort by max damage
#         pokemon_ranks[pokemon] = {
#             poke: pokemon_to_pokemon_to_max_damage[pokemon][poke]
#             for poke in sorted(
#                 pokemon_to_pokemon_to_max_damage[pokemon].keys(),
#                 key=lambda poke: pokemon_to_pokemon_to_max_damage[pokemon][poke],
#                 reverse=descending
#             )
#         }
#
#     return pokemon_ranks
#
#
# def rank_based_on_attack_and_defense_rank(
#         opponent_to_pokemon_attack_rank: DefaultDict[Pokemon, Dict[Pokemon, float]],
#         opponent_to_pokemon_defense_rank: DefaultDict[Pokemon, Dict[Pokemon, float]],
#         level: int
# ) -> dict[str, dict[Pokemon, int]]:
#     """
#     Ranks pokemon by the combining the attack and defense ranks.
#     The rank number of each pokemon is added for both ranks.
#     The pokemon with the lower rank is better.
#     :param level:
#     :param opponent_to_pokemon_attack_rank:
#     :param opponent_to_pokemon_defense_rank:
#     :return:
#     """
#
#     pokemon_health = defaultdict(lambda: 0)
#     for opponent in opponent_to_pokemon_defense_rank.keys():
#         health_ev = (512.0 / len(opponent.effort_values)) \
#             if Stat.HEALTH in opponent.effort_values else 0
#         pokemon_health[opponent] = get_health_stat(
#             all_pokemon_stats[opponent.name].health,
#             get_iv(opponent.set_number),
#             health_ev,
#             level
#         )
#     if len(opponent_to_pokemon_defense_rank) > 0:
#         for poke in list(opponent_to_pokemon_defense_rank.items())[0][1]:
#             health_ev = (512.0 / len(poke.effort_values)) \
#                 if Stat.HEALTH in poke.effort_values else 0
#             pokemon_health[poke] = get_health_stat(
#                 all_pokemon_stats[poke.name].health,
#                 get_iv(poke.set_number),
#                 health_ev,
#                 level
#             )
#
#     pokemon_ranks = defaultdict(lambda: defaultdict(lambda: 0))
#     for opponent in opponent_to_pokemon_defense_rank.keys():
#         for poke, damage in opponent_to_pokemon_defense_rank[opponent].items():
#             pokemon_ranks[opponent][poke.name + "_defense"] += damage
#
#     for opponent in opponent_to_pokemon_attack_rank.keys():
#         for poke, damage in opponent_to_pokemon_attack_rank[opponent].items():
#             pokemon_ranks[opponent][poke.name + "_offense"] += damage
#
#     opponent_to_pokemon_ranks = {}
#     for opponent in pokemon_ranks.keys():
#         opponent_to_pokemon_ranks[opponent] = {
#             pokemon: i
#             for pokemon, i in sorted(
#                 (poke for poke in pokemon_ranks[opponent].items()),
#                 key=lambda item: item[1],
#             )
#         }
#     return opponent_to_pokemon_ranks
#
#
# def do_round_two(
#         team_pokemon: List[Pokemon],
#         choice_pokemon: List[Pokemon],
#         opponent_pokemon: List[Pokemon],
#         level
# ):
#     print_pokemon_ranks(team_pokemon, opponent_pokemon, level)
#     chosen_pokemon = ask_user_to_pick_pokemon(2, team_pokemon)
#
#     # Rank the types by which need to be covered
#     weaknesses = get_weaknesses(chosen_pokemon)
#     resistances = get_resistances(chosen_pokemon)
#     remaining_pokemon = list(
#         set(team_pokemon)
#         .difference(set(chosen_pokemon))
#         .union(choice_pokemon)
#     )
#     rank_from_weaknesses_and_resistances(remaining_pokemon, weaknesses, resistances)
#
#
# def ask_user_to_pick_pokemon(
#         num_pokemon: int,
#         team_pokemon: List[Pokemon]
# ):
#     pokemon_picker_use_case = PokemonPickerUseCase()
#     chosen_pokemon_names = pokemon_picker_use_case.got_pokemon_choices_from_user(
#         num_pokemon,
#         team_pokemon
#     )
#     chosen_pokemon = [
#         team_poke
#         for team_poke in team_pokemon
#         if team_poke.name in chosen_pokemon_names
#     ]
#     return chosen_pokemon
#
#
# def get_weaknesses(
#         pokemon: List[Pokemon]
# ) -> dict[PokemonType, float]:
#     defense_multipliers = get_defense_multipliers_for_list(pokemon)
#
#     all_defense_multipliers = defaultdict(lambda: [])
#     for poke in pokemon:
#         assert (poke in defense_multipliers.keys())
#         for poke_type in defense_multipliers[poke]:
#             all_defense_multipliers[poke_type].append(
#                 defense_multipliers[poke][poke_type]
#             )
#
#     average_defense_multipliers = {
#         poke_type: sum(multipliers) / len(multipliers)
#         for poke_type, multipliers in all_defense_multipliers.items()
#     }
#
#     weaknesses_of_team = {
#         poke_type: multiplier
#         for poke_type, multiplier in sorted(
#             average_defense_multipliers.items(),
#             key=lambda item: item[1],
#             reverse=True
#         )
#     }
#     return weaknesses_of_team
#
#
# def get_resistances(
#         choice_pokemon: list[Pokemon]
# ) -> dict[PokemonType, float]:
#     pokemon_to_max_attack_powers = get_max_attack_power_for_list(choice_pokemon)
#     team_max_attack_powers = defaultdict(lambda: 0.0)
#     for pokemon in pokemon_to_max_attack_powers.keys():
#         for poke_type in pokemon_to_max_attack_powers[pokemon].keys():
#             team_max_attack_powers[poke_type] = max(
#                 team_max_attack_powers[poke_type],
#                 pokemon_to_max_attack_powers[pokemon][poke_type]
#             )
#     sorted_team_max_attack_powers = {
#         poke_type: power
#         for poke_type, power in sorted(team_max_attack_powers.items(), key=lambda item: item[1])
#     }
#     return sorted_team_max_attack_powers
#
#
# def rank_types_by_weakness_and_resistance(
#         weaknesses: dict[PokemonType, float],
#         resistances: dict[PokemonType, float]
# ) -> DefaultDict[int, set[PokemonType]]:
#     weakness_ranks = defaultdict(lambda: [])
#     rank = 1
#     last_weakness = next(iter(weaknesses.values()))
#     for poke_type, weakness in weaknesses.items():
#         if weakness != last_weakness:
#             rank = rank + 1
#         weakness_ranks[rank].append(poke_type)
#         last_weakness = weakness
#
#     resistance_ranks = defaultdict(lambda: [])
#     rank = 0
#     last_resistance = next(iter(resistances.items()))[1]
#     for poke_type, resistance in resistances.items():
#         if resistance != last_resistance:
#             rank = rank + 1
#         resistance_ranks[rank].append(poke_type)
#         last_resistance = resistance
#
#     # Average ranks
#     type_ranks = defaultdict(lambda: 0.0)
#     for rank, poke_types in weakness_ranks.items():
#         for poke_type in poke_types:
#             type_ranks[poke_type] += rank
#     for rank, poke_types in resistance_ranks.items():
#         for poke_type in poke_types:
#             type_ranks[poke_type] += rank
#             type_ranks[poke_type] = type_ranks[poke_type] / 2.0
#
#     ordered_type_ranks = defaultdict(lambda: set())
#     for poke_type, rank in sorted(
#             type_ranks.items(),
#             key=lambda item: item[1]
#     ):
#         ordered_type_ranks[rank].add(poke_type)
#
#     return ordered_type_ranks
#
#
# def rank_from_weaknesses_and_resistances(
#         pokemon: List[Pokemon],
#         weaknesses: dict[PokemonType, float],
#         resistances: dict[PokemonType, float]
# ):
#     # These are ranks that the team is bad against both offensively and defensively
#     type_ranks = rank_types_by_weakness_and_resistance(weaknesses, resistances)
#
#     pokemon_to_offense_rank = rank_pokemon_by_damage_to_type(pokemon, type_ranks)
#     pokemon_to_defense_rank = rank_pokemon_by_resistance_to_type(pokemon, type_ranks)
#
#     pokemon_to_rank = defaultdict(lambda: 0.0)
#     for pokemon in pokemon_to_defense_rank.keys():
#         pokemon_to_rank[pokemon] = pokemon_to_defense_rank[pokemon] + \
#                                    (pokemon_to_offense_rank[pokemon] / 4.0) / \
#                                    2.0
#     sorted_pokemon_ranks = {
#         pokemon: rank
#         for pokemon, rank in sorted(
#             pokemon_to_rank.items(),
#             key=lambda item: item[1]
#         )
#     }
#
#     pp(sorted_pokemon_ranks)
#
#
# def rank_pokemon_by_damage_to_type(
#         pokemon: List[Pokemon],
#         type_ranks: DefaultDict[int, set[PokemonType]]
# ) -> dict[Pokemon, float]:
#     rank_to_type_to_rank_to_pokemon = defaultdict(lambda: {})
#     for rank, poke_type_set in type_ranks.items():
#         for poke_type in poke_type_set:
#             rank_to_type_to_rank_to_pokemon[rank][poke_type] = (
#                 rank_attackers_by_damage_to_type(
#                     poke_type,
#                     pokemon
#                 )
#             )
#
#     # Average the ranks of the pokemon for each type rank
#     rank_to_pokemon_to_rank_list = defaultdict(lambda: defaultdict(lambda: [])
#                                                )
#     for type_rank, type_to_rank_to_pokemon in rank_to_type_to_rank_to_pokemon.items():
#         for poke_type, rank_to_pokemon in type_to_rank_to_pokemon.items():
#             for poke_rank, pokemon_list in rank_to_pokemon.items():
#                 for pokemon in pokemon_list:
#                     rank_to_pokemon_to_rank_list[type_rank][pokemon].append(poke_rank)
#
#     rank_to_pokemon_to_average_rank = defaultdict(lambda: {})
#
#     for rank, pokemon_to_rank_list in rank_to_pokemon_to_rank_list.items():
#         for pokemon, rank_list in pokemon_to_rank_list.items():
#             rank_to_pokemon_to_average_rank[rank][pokemon] = \
#                 sum(rank_list) / len(rank_list)
#
#     # Average the ranks of the pokemon for all the types
#     pokemon_to_rank_list = defaultdict(lambda: [])
#     for rank, pokemon_to_average_rank in rank_to_pokemon_to_average_rank.items():
#         for pokemon, average_rank in pokemon_to_average_rank.items():
#             pokemon_to_rank_list[pokemon].append(rank * average_rank)
#
#     rank_to_pokemon = {}
#     for pokemon, rank_list in pokemon_to_rank_list.items():
#         rank_to_pokemon[pokemon] = sum(rank_list) / len(rank_list)
#
#     # Sort
#     sorted_pokemon_to_rank = {
#         pokemon: rank
#         for pokemon, rank in sorted(
#             rank_to_pokemon.items(),
#             key=lambda item: item[1]
#         )
#     }
#
#     return sorted_pokemon_to_rank
#
#
# def rank_pokemon_by_resistance_to_type(pokemon, type_ranks):
#     rank_to_type_to_rank_to_pokemon = defaultdict(lambda: {})
#     for rank, poke_type_set in type_ranks.items():
#         for poke_type in poke_type_set:
#             rank_to_type_to_rank_to_pokemon[rank][poke_type] = (
#                 rank_defenders_by_resistance_to_type(
#                     poke_type,
#                     pokemon
#                 )
#             )
#
#     # Average the ranks of the pokemon for each type rank
#     rank_to_pokemon_to_rank_list = defaultdict(lambda: defaultdict(lambda: [])
#                                                )
#     for type_rank, type_to_rank_to_pokemon in rank_to_type_to_rank_to_pokemon.items():
#         for poke_type, rank_to_pokemon in type_to_rank_to_pokemon.items():
#             for poke_rank, pokemon_list in rank_to_pokemon.items():
#                 for pokemon in pokemon_list:
#                     rank_to_pokemon_to_rank_list[type_rank][pokemon].append(poke_rank)
#
#     rank_to_pokemon_to_average_rank = defaultdict(lambda: {})
#
#     for rank, pokemon_to_rank_list in rank_to_pokemon_to_rank_list.items():
#         for pokemon, rank_list in pokemon_to_rank_list.items():
#             rank_to_pokemon_to_average_rank[rank][pokemon] = \
#                 sum(rank_list) / len(rank_list)
#
#     # Average the ranks of the pokemon for all the types
#     pokemon_to_rank_list = defaultdict(lambda: [])
#     for rank, pokemon_to_average_rank in rank_to_pokemon_to_average_rank.items():
#         for pokemon, average_rank in pokemon_to_average_rank.items():
#             pokemon_to_rank_list[pokemon].append(rank * average_rank)
#
#     rank_to_pokemon = {}
#     for pokemon, rank_list in pokemon_to_rank_list.items():
#         rank_to_pokemon[pokemon] = sum(rank_list) / len(rank_list)
#
#     # Sort
#     sorted_pokemon_to_rank = {
#         pokemon: rank
#         for pokemon, rank in sorted(
#             rank_to_pokemon.items(),
#             key=lambda item: item[1]
#         )
#     }
#
#     return sorted_pokemon_to_rank
#
#
# def rank_defenders_by_resistance_to_type(
#         poke_type: PokemonType,
#         defenders: List[Pokemon]
# ):
#     pokemon_to_defense_multipliers = get_defense_multipliers_for_list(
#         defenders
#     )
#     pokemon_to_defense_multiplier = {
#         pokemon: multiplier_map[poke_type]
#         for pokemon, multiplier_map in pokemon_to_defense_multipliers.items()
#     }
#
#     # Sort by defense multiplier
#     sorted_pokemon_to_defense_multiplier = {
#         poke: multiplier
#         for poke, multiplier in sorted(
#             (item for item in pokemon_to_defense_multiplier.items()),
#             key=lambda item: item[1]
#         )
#     }
#
#     # Rank by defense multiplier
#     rank = 1
#     last_multiplier = next(iter(sorted_pokemon_to_defense_multiplier.values()))
#
#     pokemon_ranks = defaultdict(lambda: [])
#     for poke, multiplier in sorted_pokemon_to_defense_multiplier.items():
#         if multiplier != last_multiplier:
#             rank = rank + 1
#         pokemon_ranks[rank].append(poke)
#         last_multiplier = multiplier
#     return pokemon_ranks


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
                self.__level__
            )
        else:
            do_round_two(
                pokemon,
                self.__opponent_pokemon__,
                self.__level__
            )
