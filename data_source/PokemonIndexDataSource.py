import json
from os.path import exists
from typing import Dict

import cattr

from config import RAW_POKEMON_TYPES_FILE, FRESH_POKEMON_INDICES_FILE
from data_source.ParseUtil import get_next_non_newline


def __parse_pokemon_indices__() -> Dict[int, str]:
    index_to_pokemon = {}
    with open(RAW_POKEMON_TYPES_FILE, "r", encoding='utf-8') as file:
        get_next_non_newline(file)
        get_next_non_newline(file)
        get_next_non_newline(file)
        tokens = get_next_non_newline(file).strip().split("\t")
        while tokens != ['']:
            index = int(tokens[1].strip())
            name = tokens[2].strip().replace("♂/♀", "").replace("♂", "").replace("♀", "")
            index_to_pokemon[index] = name
            tokens = get_next_non_newline(file).strip().split("\t")

    return index_to_pokemon


def get_pokemon_indices() -> Dict[int, str]:
    if not exists(FRESH_POKEMON_INDICES_FILE):
        index_to_pokemon = __parse_pokemon_indices__()
        with open(FRESH_POKEMON_INDICES_FILE, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(index_to_pokemon)))
    else:
        with open(FRESH_POKEMON_INDICES_FILE, "r") as fo:
            index_to_pokemon = cattr.structure(json.loads(fo.read()), Dict[int, str])
    return index_to_pokemon


if __name__ == "__main__":
    get_pokemon_indices()
