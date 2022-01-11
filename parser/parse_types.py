import json
import typing
from collections import defaultdict
from os.path import exists

import cattr

from config import TYPE_FILE_ATTACKER_OUT, TYPE_FILE, TYPE_FILE_DEFENDER_OUT


def parse_type_chart_for_attack():
    with open(TYPE_FILE, "r") as f:
        done = False
        defender = f.readline().split()
        super_eff = defaultdict(list)
        normal_eff = defaultdict(list)
        not_eff = defaultdict(list)
        no_eff = defaultdict(list)

        s = f.readline().replace("×", "").replace("½", "0.5").split()
        while not done:
            attacker = s[0]
            for i, mul in enumerate(s[1:]):
                m = float(mul)
                if m == 0.5:
                    not_eff[attacker].append(defender[i])
                if m == 0:
                    no_eff[attacker].append(defender[i])
                if m == 2:
                    super_eff[attacker].append(defender[i])
                if m == 1:
                    normal_eff[attacker].append(defender[i])
            s = f.readline()
            if s == "":
                done = True
            s = s.replace("×", "").replace("½", "0.5").split()
        with open(TYPE_FILE_ATTACKER_OUT, "w") as fo:
            list_ = [no_eff, not_eff, normal_eff, super_eff]
            fo.write(json.dumps(cattr.unstructure(list_)))


# [no_eff, not_eff, normal_eff, super_eff]
def get_attack_type_dict() -> list[typing.DefaultDict[str, list[str]]]:
    if not exists(TYPE_FILE_ATTACKER_OUT):
        parse_type_chart_for_attack()
    with open(TYPE_FILE_ATTACKER_OUT, "r") as fo:
        return cattr.structure(json.loads(fo.read()), typing.List[typing.DefaultDict[str, typing.List[str]]])

# [no_eff, not_eff, super_eff]
def parse_type_chart_for_defense():
    super_eff = defaultdict(list)
    normal_eff = defaultdict(list)
    not_eff = defaultdict(list)
    no_eff = defaultdict(list)
    type_chart_attack = get_attack_type_dict()
    for k, vs in type_chart_attack[0].items():
        for v in vs:
            no_eff[v].append(k)
    for k, vs in type_chart_attack[1].items():
        for v in vs:
            not_eff[v].append(k)
    for k, vs in type_chart_attack[2].items():
        for v in vs:
            normal_eff[v].append(k)
    for k, vs in type_chart_attack[3].items():
        for v in vs:
            super_eff[v].append(k)

    with open(TYPE_FILE_DEFENDER_OUT, "w") as fo:
        list_ = [no_eff, not_eff, normal_eff, super_eff]
        fo.write(json.dumps(cattr.unstructure(list_)))

def get_defend_type_dict() -> list[typing.DefaultDict[str, list[str]]]:
    if not exists(TYPE_FILE_DEFENDER_OUT):
        parse_type_chart_for_defense()
    with open(TYPE_FILE_DEFENDER_OUT, "r") as fo:
        return cattr.structure(json.loads(fo.read()), typing.List[typing.DefaultDict[str, typing.List[str]]])