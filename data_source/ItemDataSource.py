import json
import os.path
import typing

import cattr

from config import FRESH_HOLD_ITEMS, RAW_HOLD_ITEMS_FILE


def __parse_items__():
    with open(RAW_HOLD_ITEMS_FILE, "r") as f:
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
        with open(FRESH_HOLD_ITEMS, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(items)))


def get_items():
    if not os.path.exists(FRESH_HOLD_ITEMS):
        __parse_items__()
    with open(FRESH_HOLD_ITEMS, "r") as fo:
        return cattr.structure(json.loads(fo.read()), typing.Dict[str, str])


if __name__ == "__main__":
    get_items()
