import json
from os.path import exists
from pprint import pp

import cattr

from config import RAW_POKEMON_TYPES_FILE, FRESH_POKEMON_INDICES_FILE
from data_source.ParseUtil import get_next_non_newline


def __parse_pokemon_indices__() -> dict[int, str]:
    index_to_pokemon: dict[int, str] = {}
    with open(RAW_POKEMON_TYPES_FILE, "r", encoding='utf-8') as file:
        get_next_non_newline(file)
        get_next_non_newline(file)
        get_next_non_newline(file)
        tokens: list[str] = get_next_non_newline(file).strip().split("\t")
        while tokens != ['']:
            index: int = int(tokens[1].strip())
            name: str = tokens[2].strip().replace("♂/♀", "").replace("♂", "").replace("♀", "")
            index_to_pokemon[index] = name
            tokens: list[str] = get_next_non_newline(file).strip().split("\t")
    return index_to_pokemon


def get_pokemon_indices() -> dict[int, str]:
    index_to_pokemon: dict[int, str] | None = None
    if not exists(FRESH_POKEMON_INDICES_FILE):
        index_to_pokemon: dict[int, str] = __parse_pokemon_indices__()
        with open(FRESH_POKEMON_INDICES_FILE, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(index_to_pokemon)))
    else:
        with open(FRESH_POKEMON_INDICES_FILE, "r") as fo:
            index_to_pokemon = cattr.structure(json.loads(fo.read()), dict[int, str])
    if index_to_pokemon is None:
        raise Exception("No pokemon indices found")
    return index_to_pokemon


if __name__ == "__main__":
    g_index_to_pokemon: dict[int, str] = get_pokemon_indices()
    pp(g_index_to_pokemon)
