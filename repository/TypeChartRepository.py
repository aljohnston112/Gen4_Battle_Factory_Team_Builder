from collections import defaultdict
from typing import List

from data_class.Pokemon import Pokemon
from data_class.Type import PokemonType
from data_source.TypeChartDataSource import get_attack_type_dict, get_defend_type_dict

type_chart_attack = get_attack_type_dict()
type_chart_defend = get_defend_type_dict()


def get_defense_multipliers(defender):
    defense_multipliers = defaultdict(lambda: 1.0)
    defender_types = defender.types
    for defender_type in defender_types:
        # [no_eff, not_eff, normal_eff, super_eff]
        no_effect_types = type_chart_defend[0].get(defender_type, [])
        not_effective_types = type_chart_defend[1].get(defender_type, [])
        super_effective_types = type_chart_defend[3].get(defender_type, [])
        for no_effect_type in no_effect_types:
            defense_multipliers[no_effect_type] *= 0.0
        for not_effective_type in not_effective_types:
            defense_multipliers[not_effective_type] *= 0.5
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
