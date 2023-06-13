from enum import unique, Enum
from math import floor

import attr
from attr import frozen

from repository.BaseStatRepository import all_pokemon_stats


@unique
class StatEnum(Enum):
    """
       Represents Pokemon stats.
    """

    HEALTH = "health"
    ATTACK = "attack"
    DEFENSE = "defense"
    SPECIAL_ATTACK = "special_attack"
    SPECIAL_DEFENSE = "special_defense"
    SPEED = "speed"
    NO_STAT = "no_stat"


@attr.define
class Stat:
    stat_type: StatEnum
    value: int


__STAT_DICT__ = {
    "health": StatEnum.HEALTH,
    "attack": StatEnum.ATTACK,
    "defense": StatEnum.DEFENSE,
    "special_attack": StatEnum.SPECIAL_ATTACK,
    "special_defense": StatEnum.SPECIAL_DEFENSE,
    "speed": StatEnum.SPEED,
}


def get_stat_enum(stat):
    return __STAT_DICT__[stat.lower()]


def get_iv_for_battle_factory(round_number: int) -> int:
    iv = (round_number - 1) * 4
    return iv if iv < 32 else 31


@unique
class NatureEnum(Enum):
    """
    Represents the Pokemon natures.
    """
    HARDY = "hardy"
    LONELY = "lonely"
    BRAVE = "brave"
    ADAMANT = "adamant"
    NAUGHTY = "naughty"
    BOLD = "bold"
    DOCILE = "docile"
    RELAXED = "relaxed"
    IMPISH = "impish"
    LAX = "lax"
    TIMID = "timid"
    HASTY = "hasty"
    SERIOUS = "serious"
    JOLLY = "jolly"
    NAIVE = "naive"
    MODEST = "modest"
    MILD = "mild"
    QUIET = "quiet"
    BASHFUL = "bashful"
    RASH = "rash"
    CALM = "calm"
    GENTLE = "gentle"
    SASSY = "sassy"
    CAREFUL = "careful"
    QUIRKY = "quirky"


@frozen
class Nature:
    nature: NatureEnum
    up: StatEnum
    down: StatEnum


__NATURE_DICT__ = {
    "hardy": Nature(nature=NatureEnum.HARDY, up=StatEnum.NO_STAT, down=StatEnum.NO_STAT),
    "lonely": Nature(nature=NatureEnum.LONELY, up=StatEnum.ATTACK, down=StatEnum.DEFENSE),
    "brave": Nature(nature=NatureEnum.BRAVE, up=StatEnum.ATTACK, down=StatEnum.SPEED),
    "adamant": Nature(nature=NatureEnum.ADAMANT, up=StatEnum.ATTACK, down=StatEnum.SPECIAL_ATTACK),
    "naughty": Nature(nature=NatureEnum.NAUGHTY, up=StatEnum.ATTACK, down=StatEnum.SPECIAL_DEFENSE),
    "bold": Nature(nature=NatureEnum.BOLD, up=StatEnum.DEFENSE, down=StatEnum.ATTACK),
    "docile": Nature(nature=NatureEnum.DOCILE, up=StatEnum.NO_STAT, down=StatEnum.NO_STAT),
    "relaxed": Nature(nature=NatureEnum.RELAXED, up=StatEnum.DEFENSE, down=StatEnum.SPEED),
    "impish": Nature(nature=NatureEnum.IMPISH, up=StatEnum.DEFENSE, down=StatEnum.SPECIAL_ATTACK),
    "lax": Nature(nature=NatureEnum.LAX, up=StatEnum.DEFENSE, down=StatEnum.SPECIAL_DEFENSE),
    "timid": Nature(nature=NatureEnum.TIMID, up=StatEnum.SPEED, down=StatEnum.ATTACK),
    "hasty": Nature(nature=NatureEnum.HASTY, up=StatEnum.SPEED, down=StatEnum.DEFENSE),
    "serious": Nature(nature=NatureEnum.SERIOUS, up=StatEnum.NO_STAT, down=StatEnum.NO_STAT),
    "jolly": Nature(nature=NatureEnum.JOLLY, up=StatEnum.SPEED, down=StatEnum.SPECIAL_ATTACK),
    "naive": Nature(nature=NatureEnum.NAIVE, up=StatEnum.SPEED, down=StatEnum.SPECIAL_DEFENSE),
    "modest": Nature(nature=NatureEnum.MODEST, up=StatEnum.SPECIAL_ATTACK, down=StatEnum.ATTACK),
    "mild": Nature(nature=NatureEnum.MILD, up=StatEnum.SPECIAL_ATTACK, down=StatEnum.DEFENSE),
    "quiet": Nature(nature=NatureEnum.QUIET, up=StatEnum.SPECIAL_ATTACK, down=StatEnum.SPEED),
    "bashful": Nature(nature=NatureEnum.BASHFUL, up=StatEnum.NO_STAT, down=StatEnum.NO_STAT),
    "rash": Nature(nature=NatureEnum.RASH, up=StatEnum.SPECIAL_ATTACK, down=StatEnum.SPECIAL_DEFENSE),
    "calm": Nature(nature=NatureEnum.CALM, up=StatEnum.SPECIAL_DEFENSE, down=StatEnum.ATTACK),
    "gentle": Nature(nature=NatureEnum.GENTLE, up=StatEnum.SPECIAL_DEFENSE, down=StatEnum.DEFENSE),
    "sassy": Nature(nature=NatureEnum.SASSY, up=StatEnum.SPECIAL_DEFENSE, down=StatEnum.SPEED),
    "careful": Nature(nature=NatureEnum.CAREFUL, up=StatEnum.SPECIAL_DEFENSE, down=StatEnum.SPECIAL_ATTACK),
    "quirky": Nature(nature=NatureEnum.QUIRKY, up=StatEnum.NO_STAT, down=StatEnum.NO_STAT)
}


def get_attack_multiplier(nature: str):
    nature = __NATURE_DICT__[nature.lower()]
    m = 1.0
    if nature.up == StatEnum.ATTACK:
        m = 1.1
    elif nature.down == StatEnum.ATTACK:
        m = 0.9
    return m


def get_special_attack_multiplier(nature: str):
    nature = __NATURE_DICT__[nature.lower()]
    m = 1.0
    if nature.up == StatEnum.SPECIAL_ATTACK:
        m = 1.1
    elif nature.down == StatEnum.SPECIAL_ATTACK:
        m = 0.9
    return m


def get_defense_multiplier(nature: str):
    nature = __NATURE_DICT__[nature.lower()]
    m = 1.0
    if nature.up == StatEnum.DEFENSE:
        m = 1.1
    elif nature.down == StatEnum.DEFENSE:
        m = 0.9
    return m


def get_special_defense_multiplier(nature: str):
    nature = __NATURE_DICT__[nature.lower()]
    m = 1.0
    if nature.up == StatEnum.SPECIAL_DEFENSE:
        m = 1.1
    elif nature.down == StatEnum.SPECIAL_DEFENSE:
        m = 0.9
    return m


def get_speed_multiplier(nature):
    nature = __NATURE_DICT__[nature.lower()]
    m = 1.0
    if nature.up == StatEnum.SPEED:
        m = 1.1
    elif nature.down == StatEnum.SPEED:
        m = 0.9
    return m


def get_nature_multiplier(stat_type, nature):
    if stat_type == StatEnum.NO_STAT or stat_type == StatEnum.HEALTH:
        assert False
    return get_attack_multiplier(nature) if stat_type == StatEnum.ATTACK else \
        get_defense_multiplier(nature) if stat_type == StatEnum.DEFENSE else \
        get_special_attack_multiplier(nature) if stat_type == StatEnum.SPECIAL_ATTACK else \
        get_speed_multiplier(nature) if stat_type == StatEnum.SPEED else \
        get_special_defense_multiplier(nature)


def get_non_health_stat(base, iv, ev, nature, level, stat_type):
    return floor(
        (floor(
            ((2.0 * base + iv + floor(ev / 4.0)) * level) / 100.0
        ) + 5) * get_nature_multiplier(stat_type, nature)
    )


def get_health_stat(base, iv, ev, level):
    return floor((((2.0 * base + iv + floor(ev / 4.0)) * level) / 100.0)) + level + 10


def get_natures() -> list[Nature]:
    return [v for k, v in __NATURE_DICT__.items()]


def get_stat_for_battle_factory_pokemon(pokemon, level, stat_type):
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
            level=level
        )
    return stat


def get_iv_for_battle_frontier(set_number):
    return (set_number + 2) * 3


def get_base_stat(pokemon, stat_type):
    base_stats = all_pokemon_stats[pokemon.name]
    return base_stats.health if stat_type == StatEnum.HEALTH else \
        base_stats.attack if stat_type == StatEnum.ATTACK else \
            base_stats.defense if stat_type == StatEnum.DEFENSE else \
                base_stats.special_attack if stat_type == StatEnum.SPECIAL_DEFENSE else \
                    base_stats.special_defense if stat_type == StatEnum.SPECIAL_DEFENSE else \
                        base_stats.speed


def get_ev(pokemon, stat_type):
    ev = 0
    for stat in pokemon.effort_values:
        if stat.stat_type == stat_type:
            ev = stat.value
    return ev


def get_stat_for_battle_frontier_pokemon(set_number, pokemon, level, stat_type):
    if stat_type == StatEnum.HEALTH:
        stat = get_health_stat(
            base=get_base_stat(pokemon, stat_type),
            iv=get_iv_for_battle_frontier(set_number),
            ev=get_ev(pokemon, stat_type),
            level=level
        )
    else:
        stat = get_non_health_stat(
            base=get_base_stat(pokemon, stat_type),
            iv=get_iv_for_battle_frontier(set_number),
            ev=get_ev(pokemon, stat_type),
            nature=pokemon.nature,
            level=level,
            stat_type=stat_type
        )
    return stat
