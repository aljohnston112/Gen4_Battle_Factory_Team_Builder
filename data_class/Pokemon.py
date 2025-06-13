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
    unique_id: str
    nature: NatureEnum
    types: list[PokemonType]
    item: str
    moves: list[Move]
    set_number: int
    effort_values: list[Stat]

    def __hash__(self) -> int:
        return hash(self.unique_id)

    def repr(self) -> str:
        return self.unique_id


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
        pokemon_to_health[
            poke.unique_id]: int = get_stat_for_battle_factory_pokemon(
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


# TODO Focus Band, King's Rock, Lansat Berry, Lax Incense, Light Clay,
# Lucky Punch, Mental Herb, Razor Claw, Razor Fang,
# Scope Lens, Stick are not implemented;
# not sure if there are good ways to implement
# TODO Liechi Berry is kind of a hack, as attack is multiplied, not damage
# TODO Metronome is also a hack since is boost power, not damage
implemented_items = [
    "", "Aspear Berry", "Big Root", "Black Belt", "Black Sludge", "BlackGlasses",
    "Brightpowder",
    "Charcoal", "Charti Berry", "Cheri Berry", "Chesto Berry", "Choice Band",
    "Choice Scarf", "Choice Specs", "Chople Berry", "Coba Berry",
    "Colbur Berry", "Damp Rock", "DeepSeaScale", "Dragon Fang", "Expert Belt",
    "Focus Band", "Focus Sash", "Grip Claw", "Haban Berry", "Hard Stone", "Heat Rock",
    "Icy Rock", "Iron Ball", "Kasib Berry",
    "King's Rock", "Lansat Berry", "Lax Incense", "Leftovers", "Liechi Berry",
    "Life Orb", "Light Clay", "Lum Berry", "Lucky Punch", "Magnet", "Mental Herb",
    "Metal Coat", "Metronome", "Miracle Seed", "Muscle Band", "Mystic Water",
    "NeverMeltIce", "Occa Berry", "Odd Incense", "Passho Berry", "Payapa Berry",
    "Pecha Berry", "Persim Berry", "Petaya Berry", "Poison Barb", "Power Herb",
    "Quick Claw", "Rawst Berry", "Razor Claw", "Razor Fang", "Rindo Berry",
    "Rock Incense", "Rose Incense", "Salac Berry", "Scope Lens", "Sea Incense", "Sharp Beak",
    "Shell Bell", "Shuca Berry", "Silk Scarf", "SilverPowder", "Sitrus Berry",
    "Soft Sand", "Spell Tag", "Stick", "Thick Club", "Toxic Orb", "Twisted Spoon",
    "Wacan Berry", "Wave Incense", "Wide Lens", "Wise Glasses", "White Herb", "Yache Berry", "Zoom Lens"
]


def get_max_damage_attacker_can_do_to_defender(
        attacker: Pokemon,
        defender: Pokemon,
        level: int,
        random: float,
        accuracy: int,
        is_poisoned: bool
) -> tuple[int, Move]:
    move = None
    defender_types: set[PokemonType] = all_pokemon_types[defender.name]
    defender_defense_multipliers: dict[PokemonType, float] = \
        get_defense_multipliers_for_types(defender_types)
    max_damage: int = 0

    attack_stat: int = get_stat_for_battle_factory_pokemon(
        pokemon=attacker,
        level=level,
        stat_type=StatEnum.ATTACK
    )
    attacker_item = attacker.item
    if attacker_item == "Choice Band":
        attack_stat *= 1.5
    if (attacker_item == "Thick Club" and
            attacker.name in ["Cubone",  "Marowak"]):
        attack_stat *= 2
    special_attack_stat: int = get_stat_for_battle_factory_pokemon(
        pokemon=attacker,
        level=level,
        stat_type=StatEnum.SPECIAL_ATTACK
    )
    if attacker_item == "Choice Specs":
        special_attack_stat *= 1.5

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
    defender_item = defender.item
    if defender.name == "Clamperl" and defender_item == "DeepSeaScale":
        special_defense_stat *= 2

    if attacker_item not in implemented_items or \
            defender_item not in implemented_items:
        raise Exception(
            f"Item {attacker_item} or {defender_item} not implemented")

    for pokemon_move in attacker.moves:
        pokemon_move: Move

        if pokemon_move.accuracy < accuracy:
            continue

        if (pokemon_move.name in ["Sky Attack", "Solarbeam"] and
                (attacker_item != "Power Herb")
        ):
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
            power = pokemon_move.power
            if attacker_item == "Iron Ball" and pokemon_move.name == "Fling":
                power = 130
            if is_poisoned and pokemon_move.name == "Facade":
                power *= 2
            if ((attacker_item == "Black Belt" and
                 pokemon_move.move_type == PokemonType.FIGHTING) or
                    (attacker_item == "BlackGlasses" and
                     pokemon_move.move_type == PokemonType.DARK) or
                    (attacker_item == "Charcoal" and
                     pokemon_move.move_type == PokemonType.FIRE) or
                    (attacker_item == "Dragon Fang" and
                     pokemon_move.move_type == PokemonType.DRAGON) or
                    ((attacker_item in ["Hard Stone", "Rock Incense"]) and
                     pokemon_move.move_type == PokemonType.ROCK) or
                    (attacker_item == "Magnet" and
                     pokemon_move.move_type == PokemonType.ELECTRIC) or
                    (attacker_item == "Metal Coat" and
                     pokemon_move.move_type == PokemonType.STEEL) or
                    (attacker_item in ["Miracle Seed", "Rose Incense"] and
                     pokemon_move.move_type == PokemonType.GRASS) or
                    (attacker_item in ["Mystic Water", "Sea Incense", "Wave Incense"] and
                     pokemon_move.move_type == PokemonType.WATER) or
                    (attacker_item == "NeverMeltIce" and
                     pokemon_move.move_type == PokemonType.ICE) or
                    (attacker_item in ["Odd Incense", "Twisted Spoon"] and
                     pokemon_move.move_type == PokemonType.PSYCHIC) or
                    (attacker_item == "Poison Barb" and
                     pokemon_move.move_type == PokemonType.POISON) or
                    (attacker_item == "Sharp Beak" and
                     pokemon_move.move_type == PokemonType.FLYING) or
                    (attacker_item == "Silk Scarf" and
                     pokemon_move.move_type == PokemonType.NORMAL) or
                    (attacker_item == "SilverPowder" and
                     pokemon_move.move_type == PokemonType.BUG) or
                    (attacker_item == "Soft Sand" and
                     pokemon_move.move_type == PokemonType.GROUND) or
                    (attacker_item == "Spell Tag" and
                     pokemon_move.move_type == PokemonType.GHOST)
            ):
                power *= 1.2
            if not is_special and attacker_item == "Muscle Band":
                power *= 1.1
            if is_special and attacker_item == "Wise Glasses":
                power *= 1.1
            damage: int = calculate_gen4_damage(
                level=level,
                power=pokemon_move.power,
                attack=attack_stat_used,
                defense=defense_stat_used,
                is_stab=is_stab,
                type_multiplier=type_multiplier,
                random=random
            )

            if type_multiplier >= 2.0 and attacker_item == "Expert Belt":
                damage *= 1.2
            if attacker_item == "Life Orb":
                damage *= 1.3

        if damage > max_damage:
            move = pokemon_move
        max_damage: int = max(damage, max_damage)
    return max_damage, move
