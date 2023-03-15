import json
import re
from os.path import exists
from typing import Dict

import cattrs

from config import MOVES_FILE, MOVES_FILE_OUT
from data_class.Move import DetailedMove
from data_class.Split import get_split
from data_class.Type import get_type


def __parse_moves__() -> Dict[str, DetailedMove]:
    moves = {}
    with open(MOVES_FILE, "r") as moves_file:
        done = False
        while not done:
            s = moves_file.readline()
            if s != "":
                s = re.split("[\t\n]+", s)
                move_name = s[1].strip().replace(" ", "").replace("-", "").lower()
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
                moves[move_name] = DetailedMove(
                    name=move_name,
                    move_type=move_type,
                    split=move_split,
                    power=power,
                    accuracy=accuracy
                )
            else:
                done = True
    return moves


def get_moves() -> Dict[str, DetailedMove]:
    """
    Gets all the moves from Pokemon Platinum.
    :return: A dictionary of move names to detailed move data.
    """
    if not exists(MOVES_FILE_OUT):
        moves = __parse_moves__()
        with open(MOVES_FILE_OUT, "w") as moves_file:
            moves_file.write(json.dumps(cattrs.unstructure(moves)))
    else:
        with open(MOVES_FILE_OUT, "r") as fo:
            moves = cattrs.structure(
                json.loads(fo.read()),
                Dict[str, DetailedMove]
            )
    return moves
