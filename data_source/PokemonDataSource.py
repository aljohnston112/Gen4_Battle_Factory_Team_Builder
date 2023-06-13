import json
from os.path import exists
from typing import List, TextIO, Dict

import cattr

from config import RAW_FACTORY_POKEMON_FILE, FRESH_FACTORY_POKEMON_FILE
from data_class.Pokemon import Pokemon
from data_class.Stat import Stat, StatEnum
from data_source.ParseUtil import get_next_non_newline
from repository.MoveRepository import get_all_moves
from repository.PokemonTypeRepository import all_pokemon_types


def __parse_battle_factory_pokemon__() -> Dict[str, Pokemon]:
    pokemon = {}
    with open(RAW_FACTORY_POKEMON_FILE, "r", encoding='utf-8') as file:
        get_next_non_newline(file)
        tokens = get_next_non_newline(file).strip().split("\t")
        pokemon_types = all_pokemon_types
        pokemon_moves = get_all_moves

        while tokens != ['']:
            index = int(tokens[0])
            set_number = (
                0 if (index < 151) else
                1 if (index < 251) else
                2 if (index < 351) else
                3 if (index < 487) else
                4 if (index < 623) else
                5 if (index < 759) else
                6 if (index < 951) else
                7
            )
            assert set_number != 7

            name = tokens[1].strip().replace("♂/♀", "").replace("♂", "").replace("♀", "")
            nature = tokens[2].strip().lower()
            item = tokens[3]

            if name not in pokemon_types:
                print(name + " is missing\n")
            types = pokemon_types[name]

            moves = [
                pokemon_moves[tokens[4].strip()],
                pokemon_moves[tokens[5].strip()],
                pokemon_moves[tokens[6].strip()],
                pokemon_moves[tokens[7].strip()]
            ]
            evs = tokens[8].strip().split("/")
            effort_values = []
            default_ev = (512.0 / len(evs))
            for ev in evs:
                if ev == "HP":
                    effort_values.append(Stat(StatEnum.HEALTH, int(default_ev)))
                elif ev == "Atk":
                    effort_values.append(Stat(StatEnum.ATTACK, int(default_ev)))
                elif ev == "Def":
                    effort_values.append(Stat(StatEnum.DEFENSE, int(default_ev)))
                elif ev == "SpA":
                    effort_values.append(Stat(StatEnum.SPECIAL_ATTACK, int(default_ev)))
                elif ev == "SpD":
                    effort_values.append(Stat(StatEnum.SPECIAL_DEFENSE, int(default_ev)))
                elif ev == "Spe":
                    effort_values.append(Stat(StatEnum.SPEED, int(default_ev)))
                else:
                    assert False

            pokemon[name + "_" + str(set_number)] = Pokemon(
                name=name,
                nature=nature,
                types=types,
                item=item,
                moves=moves,
                set_number=set_number,
                effort_values=effort_values
            )

            # Skip the png file line or get the end of file
            tokens = get_next_non_newline(file).strip().split("\t")

    return pokemon


def get_battle_factory_pokemon() -> Dict[str, Pokemon]:
    """
    Gets a name to Pokemon dict containing all possible battle factory Pokemon.
    :return: The name to Pokemon dict containing all possible battle factory Pokemon.
    """
    if not exists(FRESH_FACTORY_POKEMON_FILE):
        pokemon = __parse_battle_factory_pokemon__()
        with open(FRESH_FACTORY_POKEMON_FILE, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(pokemon)))
    else:
        with open(FRESH_FACTORY_POKEMON_FILE, "r") as fo:
            pokemon = cattr.structure(json.loads(fo.read()), Dict[str, Pokemon])
    return pokemon


if __name__ == "__main__":
    get_battle_factory_pokemon()
