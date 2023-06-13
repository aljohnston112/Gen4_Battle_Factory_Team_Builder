import json
import random
import time
import urllib.request
from collections import defaultdict
from os.path import exists

import cattrs
from bs4 import BeautifulSoup

from config import FRESH_POKEMON_MOVE_SET_FILE, FRESH_LAST_POKEMON_MOVE_SET_INDEX_FILE
from data_class.Move import LearnableMove
from data_source.PokemonIndexDataSource import get_pokemon_indices

base_url = "https://www.serebii.net/pokedex-dp/"
num_pokemon = 493


def get_url(index: int):
    return base_url + str(index).zfill(3) + ".shtml"


def __scrape_serebii_for_move_sets():
    pokemon_to_moves = defaultdict(lambda: list())
    last_url_index = 0
    if exists(FRESH_POKEMON_MOVE_SET_FILE):
        with open(FRESH_POKEMON_MOVE_SET_FILE, "r") as file:
            pokemon_to_moves_dict = cattrs.structure(
                json.loads(file.read()),
                defaultdict[str, list]
            )
            for poke, moves in pokemon_to_moves_dict:
                pokemon_to_moves[poke] = moves

    if exists(FRESH_LAST_POKEMON_MOVE_SET_INDEX_FILE):
        with open(FRESH_LAST_POKEMON_MOVE_SET_INDEX_FILE, "r") as file:
            last_url_index = int(file.read().strip())
    try:
        index_to_pokemon = get_pokemon_indices()
        num_pokemon = 493
        ms_delay = 500
        for pokemon_index in range(last_url_index + 1, num_pokemon + 1):
            pokemon_name = index_to_pokemon[pokemon_index]
            url = get_url(pokemon_index)
            with urllib.request.urlopen(url) as fp:
                soup = BeautifulSoup(fp, 'html.parser')
            # Every other row starting from 2 contains the desired table data
            # find_all('td')[0].text is the level
            # find_all('td')[1].text is the name
            tables = [
                table for table in soup.find_all('table')
                if 'Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up' in table.text
                   or 'Platinum/HeartGold/SoulSilver Level Up' in table.text
                   or 'Diamond/Pearl/Platinum Level Up' in table.text
                   or 'Platinum/HeartGold/SoulSilver Move Tutor Attacks' in table.text
                   or 'Egg Moves (Details)' in table.text
                   or 'Pre-Evolution Moves' in table.text
            ]
            for table in tables:
                row_number = 2
                contains_level = 'Diamond/Pearl/Platinum/HeartGold/SoulSilver Level Up' in table.text \
                                 or 'Platinum/HeartGold/SoulSilver Level Up' in table.text \
                                 or 'Diamond/Pearl/Platinum Level Up' in table.text
                is_move_tutor_move = 'Platinum/HeartGold/SoulSilver Move Tutor Attacks' in table.text
                is_egg_move = 'Egg Moves (Details)' in table.text
                is_pre_evolution = 'Pre-Evolution Moves' in table.text
                rows = table.find_all('tr')
                while row_number < len(rows):
                    columns = rows[row_number].find_all('td')
                    if contains_level:
                        level = columns[0].text
                        if level == '—':
                            level = 0
                        else:
                            level = int(level)
                        attack_name = columns[1].text
                    else:
                        level = -1
                        attack_name = columns[0].text

                    if "HGSS Only" not in attack_name:
                        if attack_name == 'Base/Max Pokéathlon Stats' or \
                           'Base/Max Pok�athlon Stats' in attack_name:
                            row_number = len(rows)
                        else:
                            if len(attack_name) > 20:
                                print()
                            pokemon_to_moves[pokemon_name].append(
                                LearnableMove(
                                    name=attack_name,
                                    level=level,
                                    is_move_tutor=is_move_tutor_move,
                                    is_egg_move=is_egg_move,
                                    is_pre_evolution=is_pre_evolution
                                )
                            )
                    row_number += 2
                    if is_pre_evolution or (
                            is_move_tutor_move and
                            (pokemon_index == 386 or pokemon_index == 413 or pokemon_index == 487 or pokemon_index == 492)
                    ):
                        row_number += 1
            last_url_index = pokemon_index
            good = False
            has_move_tutor = False
            for learnable_move in pokemon_to_moves[pokemon_name]:
                if learnable_move.level != -1:
                    good = True
                if learnable_move.is_move_tutor:
                    has_move_tutor = True
            if not good or not has_move_tutor:
                print()
            random_delay = random.randint(0, 500)
            time.sleep((ms_delay + random_delay) / 1000)
    except Exception as e:
        with open(FRESH_POKEMON_MOVE_SET_FILE, "w") as file:
            file.write(json.dumps(cattrs.unstructure(pokemon_to_moves)))
        with open(FRESH_LAST_POKEMON_MOVE_SET_INDEX_FILE, "w") as file:
            file.write(str(last_url_index))

    with open(FRESH_POKEMON_MOVE_SET_FILE, "w") as file:
        file.write(json.dumps(cattrs.unstructure(pokemon_to_moves)))
    with open(FRESH_LAST_POKEMON_MOVE_SET_INDEX_FILE, "w") as file:
        file.write(str(last_url_index))
    return pokemon_to_moves


def get_move_sets():
    if exists(FRESH_POKEMON_MOVE_SET_FILE):
        with open(FRESH_POKEMON_MOVE_SET_FILE, "r") as file:
            pokemon_to_moves = cattrs.structure(
                json.loads(file.read()),
                defaultdict[str, list]
            )
            # Nidoran bug made it so there is only one Nidoran
            if len(pokemon_to_moves) != num_pokemon - 1:
                print()
    else:
        pokemon_to_moves = __scrape_serebii_for_move_sets()
    return pokemon_to_moves


if __name__ == "__main__":
    get_move_sets()
