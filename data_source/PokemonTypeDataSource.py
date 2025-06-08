import json
from os.path import exists
from pprint import pp

import cattr

from config import FRESH_POKEMON_TYPES_FILE, RAW_POKEMON_TYPES_FILE
from data_class.Type import PokemonType, get_type
from data_source.ParseUtil import get_next_non_newline


def __parse_pokemon_types__() -> dict[str, set[PokemonType]]:
    pokemon_to_types: dict[str, set[PokemonType]] = {}
    with (open(RAW_POKEMON_TYPES_FILE, "r", encoding='utf-8') as file):
        get_next_non_newline(file)
        get_next_non_newline(file)
        get_next_non_newline(file)
        tokens: list[str] = get_next_non_newline(file).strip().split("\t")
        while tokens != ['']:
            # Nidoran can be ignored since it is not in the battle factory dataset
            name: str = tokens[2].strip().replace("♂/♀", "").replace("♂", "").replace("♀", "")

            types: set[PokemonType] = {get_type(tokens[4].strip())}
            if len(tokens) > 5:
                types.add(get_type(tokens[5].strip()))

            pokemon_to_types[name]: list[PokemonType] = types
            tokens: list[str] = get_next_non_newline(file).strip().split("\t")
    return pokemon_to_types


def get_pokemon_types() -> dict[str, set[PokemonType]]:
    """
    Gets a name to Pokémon dict containing all possible battle factory Pokémon.
    :return: The name to Pokémon dict containing all possible battle factory Pokémon.
    """
    pokemon_to_types: dict[str, set[PokemonType]] | None = None
    if not exists(FRESH_POKEMON_TYPES_FILE):
        pokemon_to_types: dict[str, set[PokemonType]] = __parse_pokemon_types__()
        with open(FRESH_POKEMON_TYPES_FILE, "w") as fo:
            serializable = {k: list(v) for k, v in pokemon_to_types.items()}
            fo.write(json.dumps(cattr.unstructure(serializable)))
    else:
        with open(FRESH_POKEMON_TYPES_FILE, "r") as fo:
            pokemon_to_types: dict[str, set[PokemonType]] = \
                cattr.structure(json.loads(fo.read()), dict[str, set[PokemonType]])
    if pokemon_to_types is None:
        raise Exception("No pokemon types found")
    return pokemon_to_types


if __name__ == "__main__":
    g_pokemon_to_types: dict[str, set[PokemonType]] = get_pokemon_types()
    pp(g_pokemon_to_types)
