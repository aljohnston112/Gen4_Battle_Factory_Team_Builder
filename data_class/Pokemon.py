from __future__ import annotations

from collections import defaultdict
from typing import List

import attr

from data_class.Move import Move
from data_class.Stat import Stat
from data_class.Type import PokemonType
from repository.MoveRepository import get_all_moves
from repository.TypeChartRepository import type_chart_defend, type_chart_attack


@attr.define
class Pokemon:
    name: str
    nature: str
    types: list[PokemonType]
    item: str
    moves: list[Move]
    set_number: int
    effort_values: list[Stat]

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name


pokemon_to_defense_multipliers = {}


def get_defense_multipliers_for_pokemon(defender: Pokemon):
    attacker_type_to_multiplier = pokemon_to_defense_multipliers[defender]
    if len(attacker_type_to_multiplier) != 0:
        attacker_type_to_multiplier = defaultdict(lambda: 1.0)
        defender_types = defender.types
        for defender_type in defender_types:
            new_type_multipliers = get_defense_multipliers_for_type(defender_type)
            attacker_type_to_multiplier = {
                key: attacker_type_to_multiplier[key] * new_type_multipliers[key]
                for key in new_type_multipliers.keys()
            }
        pokemon_to_defense_multipliers[defender] = attacker_type_to_multiplier
    return attacker_type_to_multiplier


type_to_defense_multipliers = {}


def get_defense_multipliers_for_type(
        pokemon_type: PokemonType,
        current_defense_multipliers=None
):
    cached_defense_multipliers = type_to_defense_multipliers.get(pokemon_type)
    if (current_defense_multipliers is None or len(current_defense_multipliers) == 0) and cached_defense_multipliers is not None:
        current_defense_multipliers = cached_defense_multipliers
    else:
        cache = False
        if current_defense_multipliers is None or len(current_defense_multipliers) == 0:
            cache = True
            current_defense_multipliers = defaultdict(lambda: 1.0)
        # [no_eff, not_eff, normal_eff, super_eff]
        no_effect_types = type_chart_defend[0].get(pokemon_type, [])
        not_effective_types = type_chart_defend[1].get(pokemon_type, [])
        normal_effective_types = type_chart_defend[2].get(pokemon_type, [])
        super_effective_types = type_chart_defend[3].get(pokemon_type, [])
        for no_effect_type in no_effect_types:
            current_defense_multipliers[no_effect_type] *= 0.0
        for not_effective_type in not_effective_types:
            current_defense_multipliers[not_effective_type] *= 0.5
        for normal_effective_type in normal_effective_types:
            current_defense_multipliers[normal_effective_type] *= 1.0
        for super_effective_type in super_effective_types:
            current_defense_multipliers[super_effective_type] *= 2.0
        if cache:
            type_to_defense_multipliers[pokemon_type] = current_defense_multipliers
    return current_defense_multipliers


def get_defense_multipliers_for_list(
        defending_pokemon: List[Pokemon]
) -> defaultdict[Pokemon, defaultdict[PokemonType, float]]:
    defense_multipliers = defaultdict(lambda: defaultdict(lambda: 1.0))
    for defender in defending_pokemon:
        defense_multipliers[defender] = get_defense_multipliers_for_pokemon(defender)
    return defense_multipliers


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
