import json
from os.path import exists
from typing import List, TextIO, Dict

import cattr

from config import POKEMON_FILE, POKEMON_FILE_OUT
from data_class.Move import Move
from data_class.Pokemon import Pokemon
from data_class.Split import get_split
from data_class.Type import get_type, PokemonType
from data_source.ParseUtil import get_next_non_newline


def parse_types(file: TextIO) -> List[PokemonType]:
    """
    Gets the types of the Pokemon.
    :param file: The TextIO of POKEMON_FILE.
    :return: A List of PokemonTypes.
    """
    s: str = get_next_non_newline(file)
    assert "type" in s.lower()
    types: List[str] = get_next_non_newline(file).strip().split()
    return [get_type(type.lower()) for type in types]


def parse_abilities(file: TextIO) -> List[str]:
    """
    Gets the possible abilities of the Pokemon.
    :param file: The TextIO of POKEMON_FILE.
    :return: A List of abilities.
    """
    s = get_next_non_newline(file)
    assert "ability" in s.lower()
    return get_next_non_newline(file).strip().split(" or ")


def parse_hold_item(file: TextIO) -> str:
    """
    Gets the hold item of the Pokemon.
    :param file: The TextIO of POKEMON_FILE.
    :return: The item.
    """
    s = get_next_non_newline(file)
    assert "held item" in s.lower()
    s = get_next_non_newline(file).strip()
    i = s.index("png")
    return s[i + 4:]


def parse_name(file: TextIO) -> str:
    """
    Gets the name of the Pokemon.
    :param file: The TextIO of POKEMON_FILE.
    :return: The name of the Pokemon.
    """
    s = get_next_non_newline(file).strip()
    i = s.index("Lv.")
    return s[:i - 1].replace("♂/♀", "").replace("♂", "").replace("♀", "")


def parse_move(file: TextIO) -> Move:
    """
    Gets a move from the file.
    :param file: The opened POKEMON_FILE.
    :return: A data_class move.
    """
    move_name = get_next_non_newline(file).strip().replace(" ", "").replace("-", "").lower()
    move_type, move_split = get_next_non_newline(file).strip().split()
    return Move(move_name, get_type(move_type), get_split(move_split))


def __parse_battle_factory_pokemon__() -> Dict[str, Pokemon]:
    pokemon = {}
    with open(POKEMON_FILE, "r", encoding='utf-8') as file:
        s = get_next_non_newline(file)
        while s != "":
            types = parse_types(file)
            print(types)

            abilities = parse_abilities(file)
            print(abilities)

            item = parse_hold_item(file)
            print(item)

            name = parse_name(file)
            print(name)

            moves = [parse_move(file), parse_move(file), parse_move(file), parse_move(file)]
            print(moves)

            # Append numbers to names if the specific Pokemon was already read from the file.
            if name in pokemon:
                name += " 2"
            if name in pokemon:
                name = name[:-2] + " 3"
            if name in pokemon:
                name = name[:-2] + " 4"
            if name in pokemon:
                assert False

            pokemon[name] = Pokemon(
                types=types,
                ability=abilities,
                item=item,
                name=name,
                moves=moves
            )

            # Skip the png file line or get the end of file
            s = get_next_non_newline(file)

    return pokemon


def get_battle_factory_pokemon() -> Dict[str, Pokemon]:
    """
    Gets a name to Pokemon dict containing all possible battle factory Pokemon.
    :return: The name to Pokemon dict containing all possible battle factory Pokemon.
    """
    if not exists(POKEMON_FILE_OUT):
        pokemon = __parse_battle_factory_pokemon__()
        with open(POKEMON_FILE_OUT, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(pokemon)))
    else:
        with open(POKEMON_FILE_OUT, "r") as fo:
            pokemon = cattr.structure(json.loads(fo.read()), Dict[str, Pokemon])
    return pokemon
