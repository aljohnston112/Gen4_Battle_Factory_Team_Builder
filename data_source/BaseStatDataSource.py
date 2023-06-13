import json
from os.path import exists
from typing import Dict

import cattr

from config import FRESH_POKEMON_BASE_STATS, RAW_POKEMON_BASE_STATS
from data_class.BaseStats import BaseStats
from data_source.ParseUtil import get_next_non_newline


def __parse_pokemon_stats__() -> Dict[str, BaseStats]:
    base_stats = {}
    with open(RAW_POKEMON_BASE_STATS, "r", encoding='utf-8') as file:
        s = get_next_non_newline(file)
        s = get_next_non_newline(file)
        while s != "":
            line = s.split("\t")
            base_stats[line[1]] = BaseStats(
                name=line[1],
                health=line[3],
                attack=line[4],
                defense=line[5],
                special_attack=line[6],
                special_defense=line[7],
                speed=line[8]
            )
            s = get_next_non_newline(file)
    return base_stats


def get_base_stats() -> Dict[str, BaseStats]:
    """
    Gets a name to base stat dict containing all possible Pokemon up to gen 4.
    :return: The name to base stat dict containing all possible Pokemon up to gen 4.
    """
    if not exists(FRESH_POKEMON_BASE_STATS):
        pokemon_stats = __parse_pokemon_stats__()
        with open(FRESH_POKEMON_BASE_STATS, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(pokemon_stats)))
    else:
        with open(FRESH_POKEMON_BASE_STATS, "r") as fo:
            pokemon_stats = cattr.structure(json.loads(fo.read()), Dict[str, BaseStats])
    return pokemon_stats


if __name__ == "__main__":
    get_base_stats()
