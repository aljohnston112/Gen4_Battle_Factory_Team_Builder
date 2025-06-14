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
from repository.PokemonTypeRepository import all_pokemon_types
from repository.TypeChartRepository import type_chart_defend


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
        return dict(__types_to_defense_multipliers__[key])

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
#  Lucky Punch, Mental Herb, Razor Claw, Razor Fang, Scope Lens, Stick
#  are not implemented; not sure if there are good ways to implement
implemented_items = [
    "", "Aspear Berry", "Big Root", "Black Belt", "Black Sludge",
    "BlackGlasses", "Brightpowder", "Charcoal", "Charti Berry", "Cheri Berry",
    "Chesto Berry", "Choice Band", "Choice Scarf", "Choice Specs",
    "Chople Berry", "Coba Berry", "Colbur Berry", "Damp Rock", "DeepSeaScale",
    "Dragon Fang", "Expert Belt", "Focus Band", "Focus Sash", "Grip Claw",
    "Haban Berry", "Hard Stone", "Heat Rock", "Icy Rock", "Iron Ball",
    "Kasib Berry", "King's Rock", "Lansat Berry", "Lax Incense", "Leftovers",
    "Liechi Berry", "Life Orb", "Light Clay", "Lum Berry", "Lucky Punch",
    "Magnet", "Mental Herb", "Metal Coat", "Metronome", "Miracle Seed",
    "Muscle Band", "Mystic Water", "NeverMeltIce", "Occa Berry", "Odd Incense",
    "Passho Berry", "Payapa Berry", "Pecha Berry", "Persim Berry",
    "Petaya Berry", "Poison Barb", "Power Herb", "Quick Claw", "Rawst Berry",
    "Razor Claw", "Razor Fang", "Rindo Berry", "Rock Incense", "Rose Incense",
    "Salac Berry", "Scope Lens", "Sea Incense", "Sharp Beak", "Shell Bell",
    "Shuca Berry", "Silk Scarf", "SilverPowder", "Sitrus Berry", "Soft Sand",
    "Spell Tag", "Stick", "Thick Club", "Toxic Orb", "Twisted Spoon",
    "Wacan Berry", "Wave Incense", "Wide Lens", "Wise Glasses",
    "White Herb", "Yache Berry", "Zoom Lens"
]

__boosting_items__: dict[str, PokemonType] = {
    "Black Belt": PokemonType.FIGHTING,
    "BlackGlasses": PokemonType.DARK,
    "Charcoal": PokemonType.FIRE,
    "Dragon Fang": PokemonType.DRAGON,
    "Hard Stone": PokemonType.ROCK,
    "Rock Incense": PokemonType.ROCK,
    "Magnet": PokemonType.ELECTRIC,
    "Metal Coat": PokemonType.STEEL,
    "Miracle Seed": PokemonType.GRASS,
    "Rose Incense": PokemonType.GRASS,
    "Mystic Water": PokemonType.WATER,
    "Sea Incense": PokemonType.WATER,
    "Wave Incense": PokemonType.WATER,
    "NeverMeltIce": PokemonType.ICE,
    "Odd Incense": PokemonType.PSYCHIC,
    "Twisted Spoon": PokemonType.PSYCHIC,
    "Poison Barb": PokemonType.POISON,
    "Sharp Beak": PokemonType.FLYING,
    "Silk Scarf": PokemonType.NORMAL,
    "SilverPowder": PokemonType.BUG,
    "Soft Sand": PokemonType.GROUND,
    "Spell Tag": PokemonType.GHOST,
}


def get_max_damage_attacker_can_do_to_defender(
        attacker: Pokemon,
        defender: Pokemon,
        level: int,
        random: float,
        accuracy: int,
        is_poisoned: bool
) -> tuple[int, Move | None]:
    move: Move | None = None
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
    if attacker_item not in implemented_items:
        raise Exception(f"Item {attacker_item} not implemented")
    if attacker_item == "Choice Band":
        attack_stat: int = floor(1.5 * attack_stat)
    elif (attacker_item == "Thick Club" and
          attacker.name in ["Cubone", "Marowak"]):
        attack_stat: int = floor(2 * attack_stat)
    special_attack_stat: int = get_stat_for_battle_factory_pokemon(
        pokemon=attacker,
        level=level,
        stat_type=StatEnum.SPECIAL_ATTACK
    )
    if attacker_item == "Choice Specs":
        special_attack_stat: int = floor(1.5 * special_attack_stat)
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
    if defender_item not in implemented_items:
        raise Exception(f"Item {defender_item} not implemented")
    if defender.name == "Clamperl" and defender_item == "DeepSeaScale":
        special_defense_stat = floor(2 * special_defense_stat)
    for pokemon_move in attacker.moves:
        pokemon_move: Move
        if pokemon_move.accuracy < accuracy:
            continue
        if (pokemon_move.name in ["Sky Attack", "Solarbeam"] and
                (attacker_item != "Power Herb")
        ):
            continue
        power: int = pokemon_move.power
        if attacker_item == "Iron Ball" and pokemon_move.name == "Fling":
            power: int = 130
        if power == 0:
            damage: int = 0
        else:
            is_special: bool = pokemon_move.category is Category.SPECIAL
            attack_stat_used: int = \
                special_attack_stat if is_special else attack_stat
            defense_stat_used: int = \
                special_defense_stat if is_special else defense_stat
            pokemon_move_type = pokemon_move.move_type
            is_stab: bool = pokemon_move_type in attacker.types
            type_multiplier: float = \
                defender_defense_multipliers.get(pokemon_move_type, 1.0)
            if is_poisoned and pokemon_move.name == "Facade":
                power: int = floor(2 * power)
            if (attacker_item in __boosting_items__ and
                    pokemon_move_type == __boosting_items__[attacker_item]
            ):
                power: int = floor(1.2 * power)
            if ((not is_special and attacker_item == "Muscle Band") or
                    (is_special and attacker_item == "Wise Glasses")
            ):
                power: int = floor(1.1 * power)
            damage: int = calculate_gen4_damage(
                level=level,
                power=power,
                attack=attack_stat_used,
                defense=defense_stat_used,
                is_stab=is_stab,
                type_multiplier=type_multiplier,
                random=random
            )

            if type_multiplier >= 2.0 and attacker_item == "Expert Belt":
                damage: int = floor(1.2 * damage)
            if attacker_item == "Life Orb":
                damage: int = floor(1.3 * damage)
        if damage > max_damage:
            move: Move = pokemon_move
        max_damage: int = max(damage, max_damage)
    return max_damage, move
