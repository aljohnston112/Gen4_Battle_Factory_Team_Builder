import json
import typing

import cattr

from config import ITEM_FILE_OUT, HOLD_ITEMS_FILE


def parse_items():
    with open(HOLD_ITEMS_FILE, "r") as f:
        items = {}
        done = False
        while not done:
            s = f.readline()
            if s != "":
                s = s.split("\t")
                item = s[0].strip()
                d = s[1].strip()
                items[item] = d
            else:
                done = True
        with open(ITEM_FILE_OUT, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(items)))

parse_items()

def get_items():
    with open(ITEM_FILE_OUT, "r") as fo:
        return cattr.structure(json.loads(fo.read()), typing.Dict[str, str])

