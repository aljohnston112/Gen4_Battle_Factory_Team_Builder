import json
import typing
from os.path import exists

import cattr

from config import POKEMON_FILE_OUT, POKEMON_FILE
from pokemon.Move import Move
from pokemon.Pokemon import Pokemon


def skip_white_space(f):
    s = "\n"
    while s.isspace():
        s = f.readline()
    return s


def get_move(f):
    move_name = skip_white_space(f).strip().replace(" ", "").replace("-", "").lower()

    move_type, move_split = skip_white_space(f).strip().split()
    return Move(move_name, move_type, move_split)


def parse_pokemon():
    with open(POKEMON_FILE, "r") as f:
        done = False
        pokemon = {}
        while not done:
            s = skip_white_space(f)
            if s != "":
                s = skip_white_space(f)
                assert "type" in s.lower()
                types = skip_white_space(f).strip().split()
                s = skip_white_space(f)
                assert "ability" in s.lower()
                abilities = skip_white_space(f).strip().split(" or ")
                print(types)
                print(abilities)
                s = skip_white_space(f)
                assert "held item" in s.lower()
                s = skip_white_space(f).strip()
                i = s.index("png")
                item = s[i+4:]
                print(item)
                s = skip_white_space(f).strip()
                i = s.index("Lv.")
                name = s[:i-1].replace("♂/♀", "").replace("♂", "").replace("♀", "")
                print(name)
                moves = [get_move(f), get_move(f), get_move(f), get_move(f)]
                print(moves)
                if name in pokemon:
                    name += " 2"
                if name in pokemon:
                    name = name[:-2] + " 3"
                if name in pokemon:
                    name = name[:-2] + " 4"
                if name in pokemon:
                    assert False
                pokemon[name] = Pokemon(types=types, ability=abilities, item=item, name=name, moves=moves)
            else:
                done = True
        with open(POKEMON_FILE_OUT, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(pokemon)))


def get_pokemon():
    if not exists(POKEMON_FILE_OUT):
        parse_pokemon()
    with open(POKEMON_FILE_OUT, "r") as fo:
        return cattr.structure(json.loads(fo.read()), typing.Dict[str, Pokemon])
