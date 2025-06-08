import json
import re
from os.path import exists
from pprint import pp

import cattrs

from config import RAW_MOVES_FILE, FRESH_MOVES_FILE
from data_class.Move import Move
from data_class.Category import get_category, Category
from data_class.Type import get_type, PokemonType


def __parse_moves__() -> dict[str, Move]:
    moves: dict[str, Move] = {}
    with open(RAW_MOVES_FILE, "r") as moves_file:
        moves_file.readline()
        done: bool = False
        while not done:
            s: str = moves_file.readline()
            if s != "":
                s: list[str] = re.split("[\t\n]+", s)
                move_name: str = s[1].strip()
                move_type: PokemonType = get_type(s[2].strip())
                move_split: Category = get_category(s[3].strip())
                power: str = s[5].strip()
                if power == "1HKO":
                    power: int = -1
                if power == "-" or power == "Fixed" or power == "Varies":
                    power: int = 0
                power: int = int(power)
                accuracy: str = s[6].strip()
                if accuracy == "-":
                    accuracy = "100%"
                accuracy: int = int(accuracy[:-1])
                moves[move_name]: Move = Move(
                    name=move_name,
                    move_type=move_type,
                    category=move_split,
                    power=power,
                    accuracy=accuracy
                )
            else:
                done: bool = True
    return moves


def get_moves() -> dict[str, Move]:
    """
    Gets all the moves from Pokémon Platinum.
    :return: A dictionary of move names to detailed move data.
    """
    moves: dict[str, Move] | None = None
    if not exists(FRESH_MOVES_FILE):
        moves: dict[str, Move] = __parse_moves__()
        with open(FRESH_MOVES_FILE, "w") as moves_file:
            moves_file.write(json.dumps(cattrs.unstructure(moves)))
    else:
        with open(FRESH_MOVES_FILE, "r") as fo:
            moves: dict[str, Move] = cattrs.structure(
                json.loads(fo.read()),
                dict[str, Move]
            )
    if moves is None:
        raise Exception("Failed to load moves")
    return moves


if __name__ == "__main__":
    g_moves: dict[str, Move] = get_moves()
    pp(g_moves)
