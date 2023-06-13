import json
from os.path import exists
from typing import Dict

import cattr

from config import FRESH_POKEMON_TYPES_FILE, RAW_POKEMON_TYPES_FILE
from data_class.Type import PokemonType, get_type
from data_source.ParseUtil import get_next_non_newline


def __parse_pokemon_types__() -> Dict[str, list[PokemonType]]:
    pokemon_to_types = {}
    with open(RAW_POKEMON_TYPES_FILE, "r", encoding='utf-8') as file:
        get_next_non_newline(file)
        get_next_non_newline(file)
        get_next_non_newline(file)
        tokens = get_next_non_newline(file).strip().split("\t")
        while tokens != ['']:
            name = tokens[2].strip().replace("♂/♀", "").replace("♂", "").replace("♀", "")

            types = [get_type(tokens[4].strip())]
            if len(tokens) > 5:
                types.append(get_type(tokens[5].strip()))

            pokemon_to_types[name] = types
            tokens = get_next_non_newline(file).strip().split("\t")

    return pokemon_to_types


def get_pokemon_types() -> Dict[str, list[PokemonType]]:
    """
    Gets a name to Pokemon dict containing all possible battle factory Pokemon.
    :return: The name to Pokemon dict containing all possible battle factory Pokemon.
    """
    if not exists(FRESH_POKEMON_TYPES_FILE):
        pokemon_to_types = __parse_pokemon_types__()
        with open(FRESH_POKEMON_TYPES_FILE, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(pokemon_to_types)))
    else:
        with open(FRESH_POKEMON_TYPES_FILE, "r") as fo:
            pokemon_to_types = cattr.structure(json.loads(fo.read()), Dict[str, list[PokemonType]])
    return pokemon_to_types


if __name__ == "__main__":
    get_pokemon_types()
