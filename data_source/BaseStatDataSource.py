import json
from os.path import exists
from pprint import pp

import cattr

from config import FRESH_POKEMON_BASE_STATS, RAW_POKEMON_BASE_STATS
from data_class.BaseStats import BaseStats
from data_source.ParseUtil import get_next_non_newline


def __parse_pokemon_stats__() -> dict[str, BaseStats]:
    base_stats: dict[str, BaseStats] = {}
    with open(RAW_POKEMON_BASE_STATS, "r", encoding='utf-8') as file:
        # Skip header
        get_next_non_newline(file)
        s: str = get_next_non_newline(file)
        while s != "":
            line = s.split("\t")
            base_stats[line[1]] = BaseStats(
                name=line[1],
                health=int(line[3]),
                attack=int(line[4]),
                defense=int(line[5]),
                special_attack=int(line[6]),
                special_defense=int(line[7]),
                speed=int(line[8])
            )
            s: str = get_next_non_newline(file)
    return base_stats


def get_base_stats() -> dict[str, BaseStats]:
    """
    Gets a name to base stat dict containing all possible Pokémon up to gen 4.
    :return: The name to base stat dict containing all possible Pokémon up to gen 4.
    """
    pokemon_stats: dict[str, BaseStats] | None = None
    if not exists(FRESH_POKEMON_BASE_STATS):
        pokemon_stats: dict[str, BaseStats] = __parse_pokemon_stats__()
        with open(FRESH_POKEMON_BASE_STATS, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(pokemon_stats)))
    else:
        with open(FRESH_POKEMON_BASE_STATS, "r") as fo:
            pokemon_stats: dict[str, BaseStats] = cattr.structure(json.loads(fo.read()), dict[str, BaseStats])
    if pokemon_stats is None:
        raise Exception("No pokemon stats found")
    return pokemon_stats


if __name__ == "__main__":
    g_pokemon_stats: dict[str, BaseStats] = get_base_stats()
    pp(g_pokemon_stats)