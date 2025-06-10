import json
from collections import defaultdict
from os.path import exists
from pprint import pprint

import cattr

from config import FRESH_ATTACKER_TYPE_FILE, RAW_TYPE_FILE, \
    FRESH_DEFENDER_TYPE_FILE
from data_class.Type import get_type, PokemonType, TypeMatchups, \
    build_type_matchups


def parse_type_chart_for_attack():
    with open(RAW_TYPE_FILE, "r", encoding="UTF-8") as input_file:
        type_to_super_effective: \
            defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
        type_to_normal_effective: \
            defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
        type_to_not_effective: \
            defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
        type_to_no_effect: \
            defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)

        defender_type_strings: list[str] = input_file.readline().split()
        while True:
            multiplier_string_list: list[str] = input_file.readline() \
                .replace("×", "") \
                .replace("½", "0.5") \
                .split()
            if len(multiplier_string_list) == 0:
                break

            attack_type: PokemonType = get_type(multiplier_string_list[0])
            for i, multiplier_string in enumerate(multiplier_string_list[1:]):
                i: int
                multiplier_string: str
                multiplier: float = float(multiplier_string)
                defender_type_string = defender_type_strings[i]
                defender_type = get_type(defender_type_string)
                if multiplier == 0:
                    type_to_no_effect[attack_type].append(defender_type)
                elif multiplier == 0.5:
                    type_to_not_effective[attack_type].append(defender_type)
                elif multiplier == 1:
                    type_to_normal_effective[attack_type].append(defender_type)
                elif multiplier == 2:
                    type_to_super_effective[attack_type].append(defender_type)
        type_matchups: TypeMatchups = build_type_matchups(
            type_to_super_effective=type_to_super_effective,
            type_to_normal_effective=type_to_normal_effective,
            type_to_not_effective=type_to_not_effective,
            type_to_no_effect=type_to_no_effect
        )
        with open(FRESH_ATTACKER_TYPE_FILE, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(type_matchups), indent=2))


def get_attack_type_dict() -> TypeMatchups:
    if not exists(FRESH_ATTACKER_TYPE_FILE):
        parse_type_chart_for_attack()
    with open(FRESH_ATTACKER_TYPE_FILE, "r") as fo:
        return cattr.structure(json.loads(fo.read()), TypeMatchups)


def parse_type_chart_for_defense():
    with open(RAW_TYPE_FILE, "r", encoding="UTF-8") as input_file:
        type_to_super_effective: \
            defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
        type_to_normal_effective: \
            defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
        type_to_not_effective: \
            defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)
        type_to_no_effect: \
            defaultdict[PokemonType, list[PokemonType]] = defaultdict(list)

        defender_type_strings: list[str] = input_file.readline().split()
        while True:
            multiplier_string_list: list[str] = input_file.readline() \
                .replace("×", "") \
                .replace("½", "0.5") \
                .split()
            if len(multiplier_string_list) == 0:
                break

            attack_type: PokemonType = get_type(multiplier_string_list[0])
            for i, multiplier_string in enumerate(multiplier_string_list[1:]):
                i: int
                multiplier_string: str
                multiplier: float = float(multiplier_string)
                defender_type_string = defender_type_strings[i]
                defender_type = get_type(defender_type_string)
                if multiplier == 0:
                    type_to_no_effect[defender_type].append(attack_type)
                elif multiplier == 0.5:
                    type_to_not_effective[defender_type].append(attack_type)
                elif multiplier == 1:
                    type_to_normal_effective[defender_type].append(attack_type)
                elif multiplier == 2:
                    type_to_super_effective[defender_type].append(attack_type)
        type_matchups: TypeMatchups = build_type_matchups(
            type_to_super_effective=type_to_super_effective,
            type_to_normal_effective=type_to_normal_effective,
            type_to_not_effective=type_to_not_effective,
            type_to_no_effect=type_to_no_effect
        )
        with open(FRESH_DEFENDER_TYPE_FILE, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(type_matchups), indent=2))


def get_defend_type_dict() -> TypeMatchups:
    if not exists(FRESH_DEFENDER_TYPE_FILE):
        parse_type_chart_for_defense()
    with open(FRESH_DEFENDER_TYPE_FILE, "r") as fo:
        return cattr.structure(json.loads(fo.read()), TypeMatchups)


def print_type_matchups(label: str, matchups: TypeMatchups):
    print(f"\n=== {label} ===")
    print("Super effective:")
    pprint(dict(matchups.type_to_super_effective))
    print("Normal effective:")
    pprint(dict(matchups.type_to_normal_effective))
    print("Not effective:")
    pprint(dict(matchups.type_to_not_effective))
    print("No effect:")
    pprint(dict(matchups.type_to_no_effect))

if __name__ == "__main__":
    g_defend_types: TypeMatchups = get_defend_type_dict()
    print_type_matchups("Defender Matchups", g_defend_types)

    g_attack_types = get_attack_type_dict()
    print_type_matchups("Attack Matchups", g_attack_types)
