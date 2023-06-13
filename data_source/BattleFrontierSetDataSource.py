import json
from collections import defaultdict
from os.path import exists
from typing import Dict

import cattr

from config import FRESH_FRONTIER_POKEMON_FILE, RAW_FRONTIER_POKEMON_FILE, RAW_FRONTIER_TRAINER_FILE
from data_class.Pokemon import Pokemon
from data_class.Stat import Stat, StatEnum
from data_source.ParseUtil import get_next_non_newline
from repository.MoveRepository import get_all_moves
from repository.PokemonTypeRepository import all_pokemon_types


def __parse_trainers__() -> Dict[str, list[int]]:
    trainer_to_set = defaultdict(lambda: list())
    with open(RAW_FRONTIER_TRAINER_FILE, "r", encoding='utf-8') as file:
        get_next_non_newline(file)
        get_next_non_newline(file)
        s = get_next_non_newline(file)
        while s != "":
            tokens = s.split(",")
            name = tokens[2].strip()
            for i in range(8):
                if tokens[i + 3] == '?' or tokens[i + 3] == '?\n':
                    trainer_to_set[name].append(i)
            s = get_next_non_newline(file)
    return trainer_to_set


def __parse_effort_value__(stat_enum, stat_token):
    ev = int(stat_token) if stat_token != "-" else 0
    return Stat(stat_enum, ev)


def __parse_frontier_pokemon__() -> Dict[int, set[Pokemon]]:
    pokemon = defaultdict(lambda: set())
    trainers_to_sets = __parse_trainers__()
    pokemon_types = all_pokemon_types
    pokemon_moves = get_all_moves

    with open(RAW_FRONTIER_POKEMON_FILE, "r", encoding='utf-8') as file:
        s = file.read()
        trainer_sets = s.split("\n,,,,,,,,,,,,,,\n,,,,,,,,,,,,,,\n")
        for trainer_set in trainer_sets:
            tokens = trainer_set.split("\n")
            names = tokens[0].replace(" and ", ", ").split(", ")

            sets = set()

            names[0] = names[0].strip('"')
            names[len(names) - 1] = names[len(names) - 1][:-14].strip('"')

            for name in names:
                assert name in trainers_to_sets.keys()
                sets = sets.union(set(trainers_to_sets[name]))
            for i in range(4, len(tokens)):
                pokemon_tokens = tokens[i].split(",")
                name = pokemon_tokens[1]
                item = pokemon_tokens[3][:-int(len(pokemon_tokens[3]) / 2 + 1)]
                moves = [
                    pokemon_moves[pokemon_tokens[4]],
                    pokemon_moves[pokemon_tokens[5]],
                    pokemon_moves[pokemon_tokens[6]],
                    pokemon_moves[pokemon_tokens[7]]
                ]
                nature = pokemon_tokens[8]

                effort_values = [
                    __parse_effort_value__(StatEnum.HEALTH, pokemon_tokens[9]),
                    __parse_effort_value__(StatEnum.ATTACK, pokemon_tokens[10]),
                    __parse_effort_value__(StatEnum.DEFENSE, pokemon_tokens[11]),
                    __parse_effort_value__(StatEnum.SPECIAL_ATTACK, pokemon_tokens[12]),
                    __parse_effort_value__(StatEnum.SPECIAL_DEFENSE, pokemon_tokens[13]),
                    __parse_effort_value__(StatEnum.SPEED, pokemon_tokens[14]),
                ]
                for set_number in sets:
                    p = Pokemon(
                        name=name,
                        nature=nature,
                        types=pokemon_types[name],
                        item=item,
                        moves=moves,
                        set_number=-1,
                        effort_values=effort_values
                    )
                    pokemon[set_number].add(p)

    return pokemon


def get_battle_frontier_sets() -> Dict[int, set[Pokemon]]:
    if not exists(FRESH_FRONTIER_POKEMON_FILE):
        frontier_pokemon = __parse_frontier_pokemon__()
        with open(FRESH_FRONTIER_POKEMON_FILE, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(frontier_pokemon)))
    else:
        with open(FRESH_FRONTIER_POKEMON_FILE, "r") as fo:
            frontier_pokemon = cattr.structure(json.loads(fo.read()), Dict[int, set[Pokemon]])
    return frontier_pokemon


if __name__ == "__main__":
    get_battle_frontier_sets()
