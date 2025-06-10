import json
import os.path
from pprint import pp

import cattr

from config import FRESH_HOLD_ITEMS, RAW_HOLD_ITEMS_FILE


def __parse_items__():
    with open(RAW_HOLD_ITEMS_FILE, "r") as f:
        items: dict[str, str] = {}
        done: bool = False
        while not done:
            s: str = f.readline()
            if s != "":
                s: list[str] = s.split("\t")
                item: str = s[0].strip()
                description: str = s[1].strip()
                items[item]: str = description
            else:
                done: bool = True
        with open(FRESH_HOLD_ITEMS, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(items), indent=2))


def get_items() -> dict[str, str]:
    if not os.path.exists(FRESH_HOLD_ITEMS):
        __parse_items__()
    with open(FRESH_HOLD_ITEMS, "r") as fo:
        return cattr.structure(json.loads(fo.read()), dict[str, str])


if __name__ == "__main__":
    g_items: dict[str, str] = get_items()
    pp(g_items)
