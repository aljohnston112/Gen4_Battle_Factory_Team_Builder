from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from math import floor

import attr

from data_class.BaseStats import BaseStats
from data_class.Category import Category
from data_class.Move import Move
from data_class.Stat import Stat, StatEnum, get_health_stat, \
    get_iv_for_battle_factory, get_non_health_stat, NatureEnum
from data_class.Type import PokemonType
from repository.BaseStatRepository import all_pokemon_stats
from repository.MoveRepository import all_moves
from repository.PokemonTypeRepository import all_pokemon_types
from repository.TypeChartRepository import type_chart_attack, type_chart_defend


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
        return hash(self.unique_key)

    def repr(self) -> str:
        return self.unique_key


__defense_matchups__: dict[str, defaultdict[PokemonType, float]] = {}


def get_defense_multipliers_for_pokemon(
        defender: Pokemon
) -> defaultdict[PokemonType, float]:
    defender_name: str = defender.name
    if defender_name in __defense_matchups__:
        return deepcopy(__defense_matchups__[defender_name])
    else:
        attack_type_to_multiplier: \
            defaultdict[PokemonType, float] = defaultdict(lambda: 1.0)
        defender_types: list[PokemonType] = defender.types
        for defender_type in defender_types:
            defender_type: PokemonType
            new_type_multipliers: defaultdict[PokemonType, float] = \
                get_defense_multipliers_for_type(
                    pokemon_type=defender_type,
                    current_defense_multipliers=defaultdict(lambda: 1.0)
                )
            for attack_type, multiplier in new_type_multipliers.items():
                attack_type_to_multiplier[attack_type] *= multiplier
        __defense_matchups__[defender_name]: \
            defaultdict[PokemonType, float] = attack_type_to_multiplier
    return deepcopy(attack_type_to_multiplier)


def get_defense_multipliers_for_list(
        defending_pokemon: list[Pokemon]
) -> dict[Pokemon, defaultdict[PokemonType, float]]:
    defense_multipliers: dict[Pokemon, defaultdict[PokemonType, float]] = {}
    for defender in defending_pokemon:
        defender: Pokemon
        defense_multipliers[defender]: defaultdict[PokemonType, float] = \
            get_defense_multipliers_for_pokemon(defender)
    return defense_multipliers


def get_max_attack_power(attacker: Pokemon) -> defaultdict[PokemonType, float]:
    max_attacker_powers: defaultdict[PokemonType, float] = defaultdict(
        lambda: 0.0)
    for move in attacker.moves:
        move: Move
        attack_type: PokemonType = move.move_type
        detailed_move: Move = all_moves[move.name]
        # [no_eff, not_eff, normal_eff, super_eff]
        no_effect_types: list[PokemonType] = type_chart_attack[0].get(
            attack_type, [])
        not_effective_types: list[PokemonType] = type_chart_attack[1].get(
            attack_type, [])
        normal_effective_types: list[PokemonType] = type_chart_attack[2].get(
            attack_type, [])
        super_effective_types: list[PokemonType] = type_chart_attack[3].get(
            attack_type, [])
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
def get_max_attack_power_for_list(attackers: list[Pokemon]) -> defaultdict[
    Pokemon, defaultdict[PokemonType, float]]:
    max_attack_powers: defaultdict[Pokemon, defaultdict[PokemonType, float]] = \
        defaultdict(lambda: defaultdict(lambda: 1.0))
    for attacker in attackers:
        attacker: Pokemon
        max_attack_powers[attacker]: defaultdict[
            PokemonType, float] = get_max_attack_power(attacker)
    return max_attack_powers




# ==============================================================================

def get_pokemon_health(
        pokemon: list[Pokemon],
        level: int
) -> dict[str, int]:
    pokemon_to_health: dict[str, int] = dict()
    for poke in pokemon:
        poke: Pokemon
        pokemon_to_health[poke.unique_key]: int = get_stat_for_battle_factory_pokemon(
            poke,
            level,
            StatEnum.HEALTH
        )
    return pokemon_to_health


def calculate_gen4_damage(
        level: int,
        power: int,
        attack: int,
        defense: int,
        is_stab: bool,
        type_multiplier: float,
        random: float
) -> int:
    stab: float = 1.5 if is_stab else 1.0
    step1: int = floor((2 * level) / 5) + 2
    step2: int = floor(step1 * power * attack / defense)
    step3: int = floor(step2 / 50) + 2
    damage: int = floor(floor(floor(step3 * random) * stab) * type_multiplier)
    return damage


def get_ev(pokemon: Pokemon, stat_type: StatEnum) -> int:
    ev: int = 0
    for stat in pokemon.effort_values:
        stat: Stat
        if stat.stat_type == stat_type:
            ev = stat.value
            break
    return ev


__base_stat_cache__: dict[tuple[str, StatEnum], int] = {}


def get_base_stat(pokemon: Pokemon, stat_type: StatEnum) -> int:
    key: tuple[str, StatEnum] = (pokemon.name, stat_type)
    if key in __base_stat_cache__:
        key: tuple[str, StatEnum]
        return __base_stat_cache__[key]

    base_stats: BaseStats = all_pokemon_stats[pokemon.name]
    stat: int = (
        base_stats.health if stat_type == StatEnum.HEALTH else
        base_stats.attack if stat_type == StatEnum.ATTACK else
        base_stats.defense if stat_type == StatEnum.DEFENSE else
        base_stats.special_attack if stat_type == StatEnum.SPECIAL_ATTACK else
        base_stats.special_defense if stat_type == StatEnum.SPECIAL_DEFENSE else
        base_stats.speed
    )
    __base_stat_cache__[key]: int = stat
    return stat


def get_stat_for_battle_factory_pokemon(
        pokemon: Pokemon,
        level: int,
        stat_type: StatEnum
) -> int:
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


__type_to_defense_multipliers__: \
    dict[PokemonType, defaultdict[PokemonType, float]] = {}


def get_defense_multipliers_for_type(
        pokemon_type: PokemonType,
        current_defense_multipliers: defaultdict[PokemonType, float]
) -> defaultdict[PokemonType, float]:
    cached_defense_multipliers: defaultdict[PokemonType, float] = \
        __type_to_defense_multipliers__.get(pokemon_type)
    caller_provided_multipliers: bool = len(current_defense_multipliers) != 0

    if (not caller_provided_multipliers and
            cached_defense_multipliers is not None):
        # If the caller did not provide multipliers, attempt to use the cache
        current_defense_multipliers: defaultdict[PokemonType, float] = \
            cached_defense_multipliers
    else:
        should_cache: bool = False
        if not caller_provided_multipliers:
            should_cache: bool = True
            current_defense_multipliers: defaultdict[PokemonType, float] = \
                defaultdict(lambda: 1.0)
        no_effect_types: list[PokemonType] = \
            type_chart_defend.type_to_no_effect.get(pokemon_type, [])
        not_effective_types: list[PokemonType] = \
            type_chart_defend.type_to_not_effective.get(pokemon_type, [])
        super_effective_types: list[PokemonType] = \
            type_chart_defend.type_to_super_effective.get(pokemon_type, [])
        for no_effect_type in no_effect_types:
            no_effect_type: PokemonType
            current_defense_multipliers[no_effect_type] *= 0.0
        for not_effective_type in not_effective_types:
            not_effective_type: PokemonType
            current_defense_multipliers[not_effective_type] *= 0.5
        for super_effective_type in super_effective_types:
            super_effective_type: PokemonType
            current_defense_multipliers[super_effective_type] *= 2.0
        if should_cache:
            __type_to_defense_multipliers__[pokemon_type]: \
                defaultdict[PokemonType, float] = current_defense_multipliers
    return deepcopy(current_defense_multipliers)


__types_to_defense_multipliers__: \
    dict[tuple[PokemonType, ...], dict[PokemonType, float]] = {}


def get_defense_multipliers_for_types(
        defender_types: set[PokemonType]
) -> dict[PokemonType, float]:
    key: tuple[PokemonType, ...] = \
        tuple(sorted(defender_types, key=lambda t: t.name))
    if key in __types_to_defense_multipliers__:
        # use cache if possible
        key: tuple[PokemonType, ...]
        return __types_to_defense_multipliers__[key]

    multipliers: defaultdict[PokemonType, float] = defaultdict(lambda: 1.0)
    for defender_type in defender_types:
        defender_type: PokemonType
        multipliers: defaultdict[PokemonType, float] = \
            get_defense_multipliers_for_type(
                pokemon_type=defender_type,
                current_defense_multipliers=multipliers
            )
    __types_to_defense_multipliers__[key]: dict[PokemonType, float] = \
        multipliers
    return dict(multipliers)


def get_max_damage_attacker_can_do_to_defender(
        attacker: Pokemon,
        defender: Pokemon,
        level: int,
        random: float,
        accuracy: int
) -> int:
    defender_types: set[PokemonType] = all_pokemon_types[defender.name]
    defender_defense_multipliers: dict[PokemonType, float] = \
        get_defense_multipliers_for_types(defender_types)
    max_damage: int = 0

    attack_stat: int = get_stat_for_battle_factory_pokemon(
        pokemon=attacker,
        level=level,
        stat_type=StatEnum.ATTACK
    )
    special_attack_stat: int = get_stat_for_battle_factory_pokemon(
        pokemon=attacker,
        level=level,
        stat_type=StatEnum.SPECIAL_ATTACK
    )

    defense_stat: int = get_stat_for_battle_factory_pokemon(
        pokemon=defender,
        level=level,
        stat_type=StatEnum.DEFENSE
    )
    special_defense_stat: int = get_stat_for_battle_factory_pokemon(
        pokemon=defender,
        level=level,
        stat_type=StatEnum.SPECIAL_DEFENSE
    )

    for pokemon_move in attacker.moves:
        pokemon_move: Move

        if pokemon_move.accuracy < accuracy:
            continue

        if pokemon_move.power == 0:
            damage: int = 0
        else:
            is_special = pokemon_move.category is Category.SPECIAL
            attack_stat_used: int = \
                special_attack_stat if is_special else attack_stat
            defense_stat_used: int = \
                special_defense_stat if is_special else defense_stat
            is_stab: bool = pokemon_move.move_type in attacker.types
            type_multiplier: float = \
                defender_defense_multipliers.get(pokemon_move.move_type, 1.0)
            damage: int = calculate_gen4_damage(
                level=level,
                power=pokemon_move.power,
                attack=attack_stat_used,
                defense=defense_stat_used,
                is_stab=is_stab,
                type_multiplier=type_multiplier,
                random=random
            )
        max_damage: int = max(damage, max_damage)
    return max_damage


__MIN_RANDOM_ROLL__: float = 0.85


def get_max_damage_attackers_can_do_to_defenders(
        attacking_pokemon: list[Pokemon],
        defending_pokemon: list[Pokemon],
        level: int,
        is_opponent: bool,
) -> defaultdict[Pokemon, defaultdict[Pokemon, float]]:
    attacker_to_defender_to_max_damage: \
        defaultdict[Pokemon, defaultdict[Pokemon, float]] = \
        defaultdict(lambda: defaultdict(lambda: 0.0))
    for attacker in attacking_pokemon:
        attacker: Pokemon
        for defender in defending_pokemon:
            defender: Pokemon
            max_damage: int = get_max_damage_attacker_can_do_to_defender(
                attacker=attacker,
                defender=defender,
                level=level,
                random=1.0 if is_opponent else __MIN_RANDOM_ROLL__,
                accuracy=0 if is_opponent else 100,
            )
            attacker_to_defender_to_max_damage[attacker][defender]: int = \
                max_damage
    return attacker_to_defender_to_max_damage


def get_num_hits_attackers_need_do_to_defenders(
        attackers: list[Pokemon],
        defenders: list[Pokemon],
        level: int,
        is_opponent: bool
) -> defaultdict[Pokemon, dict[Pokemon, float]]:
    attacker_to_defender_to_max_damage: \
        defaultdict[Pokemon, defaultdict[Pokemon, float]] = \
        get_max_damage_attackers_can_do_to_defenders(
            attacking_pokemon=attackers,
            defending_pokemon=defenders,
            level=level,
            is_opponent=is_opponent
        )
    pokemon_to_health: dict[str, int] = get_pokemon_health(
        pokemon=attackers + defenders,
        level=level
    )
    attacker_to_defender_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        defaultdict(lambda: dict())
    for attacker, defender_to_max_damage in \
            attacker_to_defender_to_max_damage.items():
        attacker: Pokemon
        defender_to_max_damage: defaultdict[Pokemon, float]
        for defender, max_damage in defender_to_max_damage.items():
            defender: Pokemon
            max_damage: int
            if max_damage != 0:
                hits: float = pokemon_to_health[defender.unique_key] / max_damage
            else:
                hits = 0
            attacker_to_defender_to_hits[attacker][defender]: float = hits
    return attacker_to_defender_to_hits
