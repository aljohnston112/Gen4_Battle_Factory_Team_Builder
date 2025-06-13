from collections import defaultdict
from typing import Mapping
from enum import Enum, unique
from types import MappingProxyType

from attrs import frozen


@unique
class PokemonType(Enum):
    """
    Represents the Pokémon types.
    """
    NORMAL = "normal"
    FIGHTING = "fighting"
    FLYING = "flying"
    POISON = "poison"
    GROUND = "ground"
    ROCK = "rock"
    BUG = "bug"
    GHOST = "ghost"
    STEEL = "steel"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    ELECTRIC = "electric"
    PSYCHIC = "psychic"
    ICE = "ice"
    DRAGON = "dragon"
    DARK = "dark"


__TYPE_DICT__: dict[str, PokemonType] = {
    "normal": PokemonType.NORMAL,
    "fighting": PokemonType.FIGHTING,
    "flying": PokemonType.FLYING,
    "poison": PokemonType.POISON,
    "ground": PokemonType.GROUND,
    "rock": PokemonType.ROCK,
    "bug": PokemonType.BUG,
    "ghost": PokemonType.GHOST,
    "steel": PokemonType.STEEL,
    "fire": PokemonType.FIRE,
    "water": PokemonType.WATER,
    "grass": PokemonType.GRASS,
    "electric": PokemonType.ELECTRIC,
    "psychic": PokemonType.PSYCHIC,
    "ice": PokemonType.ICE,
    "dragon": PokemonType.DRAGON,
    "dark": PokemonType.DARK,
}

pokemon_types = [t for t in PokemonType]


def get_type(pokemon_type: str) -> PokemonType:
    """
    Gets the enum representing a Pokémon type.
    :param pokemon_type: The string of the type.
    :return: The enum representing pokemon_type.
    """
    return __TYPE_DICT__[pokemon_type.lower()]


@frozen
class TypeMatchups:
    type_to_super_effective: Mapping[PokemonType, list[PokemonType]]
    type_to_normal_effective: Mapping[PokemonType, list[PokemonType]]
    type_to_not_effective: Mapping[PokemonType, list[PokemonType]]
    type_to_no_effect: Mapping[PokemonType, list[PokemonType]]


def build_type_matchups(
        type_to_super_effective: defaultdict[PokemonType, list[PokemonType]],
        type_to_normal_effective: defaultdict[PokemonType, list[PokemonType]],
        type_to_not_effective: defaultdict[PokemonType, list[PokemonType]],
        type_to_no_effect: defaultdict[PokemonType, list[PokemonType]]
) -> TypeMatchups:
    return TypeMatchups(
        type_to_super_effective=MappingProxyType(type_to_super_effective),
        type_to_normal_effective=MappingProxyType(type_to_normal_effective),
        type_to_not_effective=MappingProxyType(type_to_not_effective),
        type_to_no_effect=MappingProxyType(type_to_no_effect)
    )
