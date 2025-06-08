import json
from collections import defaultdict
from os.path import exists
from pprint import pp

import cattr

from config import FRESH_ATTACKER_TYPE_FILE, RAW_TYPE_FILE, FRESH_DEFENDER_TYPE_FILE
from data_class.Type import get_type, PokemonType


def parse_type_chart_for_attack():
    with open(RAW_TYPE_FILE, "r", encoding="UTF-8") as f:
        done: bool = False
        defender: list[str] = f.readline().split()
        super_eff: defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
        normal_eff: defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
        not_eff: defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
        no_eff: defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)

        s: list[str] = f.readline().replace("×", "").replace("½", "0.5").split()
        while not done:
            attacker: PokemonType = get_type(s[0])
            for i, mul in enumerate(s[1:]):
                i: int
                mul: str
                m: float = float(mul)
                if m == 0.5:
                    not_eff[attacker].append(get_type(defender[i]))
                if m == 0:
                    no_eff[attacker].append(get_type(defender[i]))
                if m == 2:
                    super_eff[attacker].append(get_type(defender[i]))
                if m == 1:
                    normal_eff[attacker].append(get_type(defender[i]))
            s: str = f.readline()
            if s == "":
                done = True
            s: list[str] = s.replace("×", "").replace("½", "0.5").split()
        with open(FRESH_ATTACKER_TYPE_FILE, "w") as fo:
            list_: list[defaultdict[PokemonType, list[PokemonType]]] = [no_eff, not_eff, normal_eff, super_eff]
            fo.write(json.dumps(cattr.unstructure(list_)))


# [no_eff, not_eff, normal_eff, super_eff]
def get_attack_type_dict() -> list[defaultdict[PokemonType, list[PokemonType]]]:
    if not exists(FRESH_ATTACKER_TYPE_FILE):
        parse_type_chart_for_attack()
    with open(FRESH_ATTACKER_TYPE_FILE, "r") as fo:
        return cattr.structure(
            json.loads(fo.read()),
            list[defaultdict[PokemonType, list[PokemonType]]]
        )


# [no_eff, not_eff, super_eff]
def parse_type_chart_for_defense():
    super_eff: defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
    normal_eff: defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
    not_eff: defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
    no_eff: defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
    type_chart_attack: list[defaultdict[PokemonType, list[PokemonType]]] = get_attack_type_dict()
    for k, vs in type_chart_attack[0].items():
        k: PokemonType
        vs: list[PokemonType]
        for v in vs:
            v: PokemonType
            no_eff[v].append(k)
    for k, vs in type_chart_attack[1].items():
        k: PokemonType
        vs: list[PokemonType]
        for v in vs:
            v: PokemonType
            not_eff[v].append(k)
    for k, vs in type_chart_attack[2].items():
        k: PokemonType
        vs: list[PokemonType]
        for v in vs:
            v: PokemonType
            normal_eff[v].append(k)
    for k, vs in type_chart_attack[3].items():
        k: PokemonType
        vs: list[PokemonType]
        for v in vs:
            v: PokemonType
            super_eff[v].append(k)

    with open(FRESH_DEFENDER_TYPE_FILE, "w") as fo:
        list_: list[defaultdict[PokemonType, list[PokemonType]]] = [no_eff, not_eff, normal_eff, super_eff]
        fo.write(json.dumps(cattr.unstructure(list_)))


def get_defend_type_dict() -> list[defaultdict[PokemonType, list[PokemonType]]]:
    if not exists(FRESH_DEFENDER_TYPE_FILE):
        parse_type_chart_for_defense()
    with open(FRESH_DEFENDER_TYPE_FILE, "r") as fo:
        return cattr.structure(
            json.loads(fo.read()),
            list[defaultdict[PokemonType, list[PokemonType]]])


if __name__ == "__main__":
    g_defend_types: list[defaultdict[PokemonType, list[PokemonType]]] = get_defend_type_dict()
    pp(g_defend_types)
    g_attack_types: list[defaultdict[PokemonType, list[PokemonType]]] = get_attack_type_dict()
    pp(g_attack_types)
