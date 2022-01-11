import json
import re
import typing
from os.path import exists

import cattr

from config import MOVES_FILE, MOVES_FILE_OUT
from pokemon.Move import DetailedMove


def parse_moves():
    with open(MOVES_FILE, "r") as fo:
        done = False
        moves = {}
        while not done:
            s = fo.readline()
            if s != "":
                s = re.split("[\t\n]+", s)
                move_name = s[1].strip().replace(" ", "").replace("-", "").lower()
                move_type = s[2].strip()
                move_split = s[3].strip()
                p = s[5].strip()
                if p == "1HKO":
                    p = -1
                if p == "-" or p == "Fixed" or p == "Varies":
                    p = 0
                power = int(p)
                a = s[6].strip()
                if a == "-":
                    a = "100%"
                accuracy = int(a[:-1])
                moves[move_name] = DetailedMove(
                        name=move_name,
                        type_=move_type,
                        split=move_split,
                        power=power,
                        accuracy=accuracy
                    )
            else:
                done = True
    with open(MOVES_FILE_OUT, "w") as fo:
        fo.write(json.dumps(cattr.unstructure(moves)))


def get_moves():
    if not exists(MOVES_FILE_OUT):
        parse_moves()
    with open(MOVES_FILE_OUT, "r") as fo:
        return cattr.structure(json.loads(fo.read()), typing.Dict[str, DetailedMove])
