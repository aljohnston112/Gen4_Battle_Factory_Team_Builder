import json
import re
from os.path import exists
from typing import Dict

import cattrs

from config import RAW_MOVES_FILE, FRESH_MOVES_FILE
from data_class.Move import Move
from data_class.Category import get_split
from data_class.Type import get_type


def __parse_moves__() -> Dict[str, Move]:
    moves = {}
    with open(RAW_MOVES_FILE, "r") as moves_file:
        moves_file.readline()
        done = False
        while not done:
            s = moves_file.readline()
            if s != "":
                s = re.split("[\t\n]+", s)
                move_name = s[1].strip()
                move_type = get_type(s[2].strip())
                move_split = get_split(s[3].strip())
                power = s[5].strip()
                if power == "1HKO":
                    power = -1
                if power == "-" or power == "Fixed" or power == "Varies":
                    power = 0
                power = int(power)
                accuracy = s[6].strip()
                if accuracy == "-":
                    accuracy = "100%"
                accuracy = int(accuracy[:-1])
                moves[move_name] = Move(
                    name=move_name,
                    move_type=move_type,
                    category=move_split,
                    power=power,
                    accuracy=accuracy
                )
            else:
                done = True
    return moves


def get_moves() -> Dict[str, Move]:
    """
    Gets all the moves from Pokemon Platinum.
    :return: A dictionary of move names to detailed move data.
    """
    if not exists(FRESH_MOVES_FILE):
        moves = __parse_moves__()
        with open(FRESH_MOVES_FILE, "w") as moves_file:
            moves_file.write(json.dumps(cattrs.unstructure(moves)))
    else:
        with open(FRESH_MOVES_FILE, "r") as fo:
            moves = cattrs.structure(
                json.loads(fo.read()),
                Dict[str, Move]
            )
    return moves


if __name__ == "__main__":
    get_moves()
