from collections import defaultdict
from typing import List

from data_class.Pokemon import Pokemon
from data_class.Type import PokemonType
from data_source.TypeChartDataSource import get_attack_type_dict, get_defend_type_dict
from repository.MoveRepository import get_all_moves

type_chart_attack = get_attack_type_dict()
type_chart_defend = get_defend_type_dict()


def get_max_attack_power(attacker: Pokemon):
    max_attacker_powers = defaultdict(lambda: 0.0)
    for move in attacker.moves:
        attack_type = move.move_type
        detailed_move = get_all_moves[move.name]
        # [no_eff, not_eff, normal_eff, super_eff]
        no_effect_types = type_chart_attack[0].get(attack_type, [])
        not_effective_types = type_chart_attack[1].get(attack_type, [])
        normal_effective_types = type_chart_attack[2].get(attack_type, [])
        super_effective_types = type_chart_attack[3].get(attack_type, [])
        for no_effect_type in no_effect_types:
            max_attacker_powers[no_effect_type] = 0.0
        for not_effective_type in not_effective_types:
            max_attacker_powers[not_effective_type] = \
                max(
                    max_attacker_powers[not_effective_type],
                    0.5 * detailed_move.power
                )
        for normal_effective_type in normal_effective_types:
            max_attacker_powers[normal_effective_type] = \
                max(
                    max_attacker_powers[normal_effective_type],
                    detailed_move.power
                )
        for super_effective_type in super_effective_types:
            max_attacker_powers[super_effective_type] = \
                max(
                    max_attacker_powers[super_effective_type],
                    2.0 * detailed_move.power
                )
    return max_attacker_powers


def get_max_attack_power_for_list(attackers: List[Pokemon]):
    max_attack_powers = defaultdict(lambda: defaultdict(lambda: 1.0))
    for attacker in attackers:
        max_attack_powers[attacker] = get_max_attack_power(attacker)
    return max_attack_powers


def get_defense_multipliers(defender: Pokemon):
    defense_multipliers = defaultdict(lambda: 1.0)
    defender_types = defender.types
    for defender_type in defender_types:
        # [no_eff, not_eff, normal_eff, super_eff]
        no_effect_types = type_chart_defend[0].get(defender_type, [])
        not_effective_types = type_chart_defend[1].get(defender_type, [])
        normal_effective_types = type_chart_defend[2].get(defender_type, [])
        super_effective_types = type_chart_defend[3].get(defender_type, [])
        for no_effect_type in no_effect_types:
            defense_multipliers[no_effect_type] *= 0.0
        for not_effective_type in not_effective_types:
            defense_multipliers[not_effective_type] *= 0.5
        for normal_effective_type in normal_effective_types:
            defense_multipliers[normal_effective_type] *= 01.0
        for super_effective_type in super_effective_types:
            defense_multipliers[super_effective_type] *= 2.0
    return defense_multipliers


def get_defense_multipliers_for_list(
    defending_pokemon: List[Pokemon]
) -> defaultdict[str, defaultdict[PokemonType, float]]:
    defense_multipliers = defaultdict(lambda: defaultdict(lambda: 1.0))
    for defender in defending_pokemon:
        defense_multipliers[defender.name] = get_defense_multipliers(defender)
    return defense_multipliers
