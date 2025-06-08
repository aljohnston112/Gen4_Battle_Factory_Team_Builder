from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from math import floor
from typing import List

import attr

from data_class.Category import Category
from data_class.Move import Move
from data_class.Stat import Stat, StatEnum, get_health_stat, get_iv_for_battle_factory, get_non_health_stat, NatureEnum
from data_class.Type import PokemonType
from repository.BaseStatRepository import all_pokemon_stats
from repository.MoveRepository import all_moves
from repository.PokemonTypeRepository import all_pokemon_types
from repository.TypeChartRepository import type_chart_defend, type_chart_attack


@attr.define
class Pokemon:
    name: str
    unique_key: str
    nature: NatureEnum
    types: list[PokemonType]
    item: str
    moves: list[Move]
    set_number: int
    effort_values: list[Stat]

    def __hash__(self) -> int:
        return hash(self.name)

    def repr(self) -> str:
        return self.name


type_to_defense_multipliers: dict[PokemonType, defaultdict[PokemonType, float]] = {}


def get_defense_multipliers_for_type(
        pokemon_type: PokemonType,
        current_defense_multipliers: defaultdict[PokemonType, float]
) -> defaultdict[PokemonType, float]:
    cached_defense_multipliers: defaultdict[PokemonType, float] = type_to_defense_multipliers.get(pokemon_type)
    caller_provided_multipliers: bool = len(current_defense_multipliers) != 0
    if not caller_provided_multipliers and cached_defense_multipliers is not None:
        current_defense_multipliers: defaultdict[PokemonType, float] = cached_defense_multipliers
    else:
        should_cache: bool = False
        if not caller_provided_multipliers:
            should_cache: bool = True
            current_defense_multipliers: defaultdict[PokemonType, float] = defaultdict(lambda: 1.0)
        # [no_eff, not_eff, normal_eff, super_eff]
        no_effect_types: list[PokemonType] = type_chart_defend[0].get(pokemon_type, [])
        not_effective_types: list[PokemonType] = type_chart_defend[1].get(pokemon_type, [])
        normal_effective_types: list[PokemonType] = type_chart_defend[2].get(pokemon_type, [])
        super_effective_types: list[PokemonType] = type_chart_defend[3].get(pokemon_type, [])
        for no_effect_type in no_effect_types:
            no_effect_type: PokemonType
            current_defense_multipliers[no_effect_type] *= 0.0
        for not_effective_type in not_effective_types:
            not_effective_type: PokemonType
            current_defense_multipliers[not_effective_type] *= 0.5
        for normal_effective_type in normal_effective_types:
            normal_effective_type: PokemonType
            current_defense_multipliers[normal_effective_type] *= 1.0
        for super_effective_type in super_effective_types:
            super_effective_type: PokemonType
            current_defense_multipliers[super_effective_type] *= 2.0
        if should_cache:
            type_to_defense_multipliers[pokemon_type]: defaultdict[PokemonType, float] = current_defense_multipliers
    return deepcopy(current_defense_multipliers)


_pokemon_to_defense_multipliers: dict[str, defaultdict[PokemonType, float]] = {}


def get_defense_multipliers_for_pokemon(defender: Pokemon) -> defaultdict[PokemonType, float]:
    if defender.name in _pokemon_to_defense_multipliers:
        return deepcopy(_pokemon_to_defense_multipliers[defender.name])
    else:
        attacker_type_to_multiplier: defaultdict[PokemonType, float] = defaultdict(lambda: 1.0)
        defender_types: List[PokemonType] = defender.types
        for defender_type in defender_types:
            defender_type: PokemonType
            new_type_multipliers: defaultdict[PokemonType, float] = defaultdict(lambda: 1.0)
            new_type_multipliers: defaultdict[PokemonType, float] = get_defense_multipliers_for_type(defender_type, new_type_multipliers)
            attacker_type_to_multiplier: defaultdict[PokemonType, float] = defaultdict(
                lambda: 1.0,
                {
                    key: attacker_type_to_multiplier[key] * new_type_multipliers[key]
                    for key in new_type_multipliers.keys()
                }
            )
        _pokemon_to_defense_multipliers[defender.name]: defaultdict[PokemonType, float] = attacker_type_to_multiplier
    return deepcopy(attacker_type_to_multiplier)


def get_defense_multipliers_for_list(
        defending_pokemon: List[Pokemon]
) -> defaultdict[Pokemon, defaultdict[PokemonType, float]]:
    defense_multipliers: defaultdict[Pokemon, defaultdict[PokemonType, float]] = defaultdict(
        lambda: defaultdict(lambda: 1.0))
    for defender in defending_pokemon:
        defender: Pokemon
        defense_multipliers[defender]: defaultdict[PokemonType, float] = get_defense_multipliers_for_pokemon(defender)
    return defense_multipliers


def get_max_attack_power(attacker: Pokemon) -> defaultdict[PokemonType, float]:
    max_attacker_powers: defaultdict[PokemonType, float] = defaultdict(lambda: 0.0)
    for move in attacker.moves:
        move: Move
        attack_type: PokemonType = move.move_type
        detailed_move: Move = all_moves[move.name]
        # [no_eff, not_eff, normal_eff, super_eff]
        no_effect_types: list[PokemonType] = type_chart_attack[0].get(attack_type, [])
        not_effective_types: list[PokemonType] = type_chart_attack[1].get(attack_type, [])
        normal_effective_types: list[PokemonType] = type_chart_attack[2].get(attack_type, [])
        super_effective_types: list[PokemonType] = type_chart_attack[3].get(attack_type, [])
        for no_effect_type in no_effect_types:
            no_effect_type: PokemonType
            max_attacker_powers[no_effect_type] = 0.0
        move_power: int = detailed_move.power
        for not_effective_type in not_effective_types:
            not_effective_type: PokemonType
            max_attacker_powers[not_effective_type]: float = \
                max(
                    max_attacker_powers[not_effective_type],
                    0.5 * move_power
                )
        for normal_effective_type in normal_effective_types:
            max_attacker_powers[normal_effective_type]: float = \
                max(
                    max_attacker_powers[normal_effective_type],
                    move_power
                )
        for super_effective_type in super_effective_types:
            max_attacker_powers[super_effective_type]: float = \
                max(
                    max_attacker_powers[super_effective_type],
                    2.0 * move_power
                )
    return max_attacker_powers


# TODO Pokemon name instead as the key?
def get_max_attack_power_for_list(attackers: List[Pokemon]) -> defaultdict[Pokemon, defaultdict[PokemonType, float]]:
    max_attack_powers: defaultdict[Pokemon, defaultdict[PokemonType, float]] = \
        defaultdict(lambda: defaultdict(lambda: 1.0))
    for attacker in attackers:
        attacker: Pokemon
        max_attack_powers[attacker]: defaultdict[PokemonType, float] = get_max_attack_power(attacker)
    return max_attack_powers


def get_ev(pokemon: Pokemon, stat_type: StatEnum) -> int:
    ev: int = 0
    for stat in pokemon.effort_values:
        stat: Stat
        if stat.stat_type == stat_type:
            ev = stat.value
    return ev


def get_stat_for_battle_factory_pokemon(pokemon: Pokemon, level: int, stat_type: StatEnum) -> int:
    if stat_type == StatEnum.HEALTH:
        stat = get_health_stat(
            base=get_base_stat(pokemon, stat_type),
            iv=get_iv_for_battle_factory(pokemon.set_number),
            ev=get_ev(pokemon, stat_type),
            level=level
        )
    else:
        stat = get_non_health_stat(
            base=get_base_stat(pokemon, stat_type),
            iv=get_iv_for_battle_factory(pokemon.set_number),
            ev=get_ev(pokemon, stat_type),
            nature=pokemon.nature,
            level=level,
            stat_type=stat_type
        )
    return stat


_base_stat_cache: dict[tuple[str, StatEnum], int] = {}


def get_base_stat(pokemon: Pokemon, stat_type: StatEnum) -> int:
    key = (pokemon.name, stat_type)
    if key in _base_stat_cache:
        return _base_stat_cache[key]

    base_stats = all_pokemon_stats[pokemon.name]
    stat = (
        base_stats.health if stat_type == StatEnum.HEALTH else
        base_stats.attack if stat_type == StatEnum.ATTACK else
        base_stats.defense if stat_type == StatEnum.DEFENSE else
        base_stats.special_attack if stat_type == StatEnum.SPECIAL_ATTACK else
        base_stats.special_defense if stat_type == StatEnum.SPECIAL_DEFENSE else
        base_stats.speed
    )
    _base_stat_cache[key] = stat
    return stat


types_to_defense_multipliers: dict[tuple[PokemonType, ...], dict[PokemonType, float]] = {}


def get_defense_multipliers_for_types(defender_types: set[PokemonType]) -> dict[PokemonType, float]:
    key = tuple(sorted(defender_types, key=lambda t: t.name))
    if key in types_to_defense_multipliers:
        return types_to_defense_multipliers[key]

    multipliers = defaultdict(lambda: 1.0)
    for defender_type in defender_types:
        multipliers = get_defense_multipliers_for_type(defender_type, multipliers)

    result = dict(multipliers)
    types_to_defense_multipliers[key] = result
    return result


def calculate_gen4_damage(
        level: int,
        power: int,
        atk: int,
        defense: int,
        is_stab: bool,
        type_multiplier: float,
        random: float
) -> int:
    stab: float = 1.5 if is_stab else 1.0
    step1 = floor((2 * level) / 5) + 2
    step2 = floor(step1 * power * atk / defense)
    step3 = floor(step2 / 50) + 2
    damage = floor(floor(floor(step3 * random) * stab) * type_multiplier)
    return damage


def get_max_damage_frontier_pokemon_can_do_to_defender(
        attacker: Pokemon,
        defender: Pokemon,
        level: int,
        random: float,
        accuracy: int
) -> int:
    defender_types: set[PokemonType] = all_pokemon_types[defender.name]
    defender_defense_multipliers: dict[PokemonType, float] = get_defense_multipliers_for_types(defender_types)
    max_damage: int = 0

    attack_stat: int = get_stat_for_battle_factory_pokemon(
        attacker,
        level,
        StatEnum.ATTACK
    )
    defense_stat: int = get_stat_for_battle_factory_pokemon(
        defender,
        level,
        StatEnum.DEFENSE
    )
    special_attack_stat: int = get_stat_for_battle_factory_pokemon(
        attacker,
        level,
        StatEnum.SPECIAL_ATTACK
    )
    special_defense_stat: int = get_stat_for_battle_factory_pokemon(
        defender,
        level,
        StatEnum.SPECIAL_DEFENSE
    )

    for pokemon_move in attacker.moves:
        pokemon_move: Move

        if pokemon_move.accuracy < accuracy:
            continue

        if pokemon_move.power == 0:
            damage: int = 0
        else:
            is_special = pokemon_move.category is Category.SPECIAL
            attack_stat_used = special_attack_stat if is_special else attack_stat
            defense_stat_used = special_defense_stat if is_special else defense_stat
            is_stab: bool = pokemon_move.move_type in attacker.types
            type_multiplier: float = defender_defense_multipliers[pokemon_move.move_type]
            damage: int = calculate_gen4_damage(
                level,
                pokemon_move.power,
                attack_stat_used,
                defense_stat_used,
                is_stab,
                type_multiplier,
                random
            )

        max_damage: int = max(damage, max_damage)

    return max_damage
