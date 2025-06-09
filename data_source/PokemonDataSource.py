import json
from os.path import exists
from pprint import pp

import cattr

from config import RAW_FACTORY_POKEMON_FILE, FRESH_FACTORY_POKEMON_FILE
from data_class.Move import Move
from data_class.Pokemon import Pokemon
from data_class.Stat import Stat, StatEnum, get_nature_enum
from data_class.Type import PokemonType
from data_source.ParseUtil import get_next_non_newline
from repository.MoveRepository import all_moves
from repository.PokemonTypeRepository import all_pokemon_types


def get_number_of_pokemon_in_set(set_number: int):
    return (150 if set_number == 0 else
            100 if set_number in [1, 2] else
            136 if set_number in [3, 4, 5, 6] else
            56)


def __parse_battle_factory_pokemon__() -> dict[str, Pokemon]:
    pokemon: dict[str, Pokemon] = {}
    counts: dict[str, int] = {}
    with open(RAW_FACTORY_POKEMON_FILE, "r", encoding='utf-8') as file:
        get_next_non_newline(file)
        tokens: list[str] = get_next_non_newline(file).strip().split("\t")
        pokemon_types: dict[str, set[PokemonType]] = all_pokemon_types
        pokemon_moves: dict[str, Move] = all_moves

        while tokens != ['']:
            index: int = int(tokens[0])
            set_number: int = (
                0 if (index < 151) else
                1 if (index < 251) else
                2 if (index < 351) else
                3 if (index < 487) else
                4 if (index < 623) else
                5 if (index < 759) else
                6 if (index < 895) else
                7
            )

            name: str = tokens[1].strip()  # .replace("♂/♀", "").replace("♂", "").replace("♀", "")
            nature: str = tokens[2].strip().lower()
            item: str = tokens[3]

            if name not in pokemon_types:
                raise Exception(name + " is missing\n")
            types: set[PokemonType] = pokemon_types[name]

            moves: list[Move] = [
                pokemon_moves[tokens[4].strip()],
                pokemon_moves[tokens[5].strip()],
                pokemon_moves[tokens[6].strip()],
                pokemon_moves[tokens[7].strip()]
            ]
            evs: list[str] = tokens[8].strip().split("/")
            effort_values: list[Stat] = []
            default_ev: int = 252 if len(evs) == 2 else 170
            if default_ev == 170 and len(evs) != 3:
                raise Exception("Wrong EVs")
            for ev in evs:
                if ev == "HP":
                    effort_values.append(Stat(StatEnum.HEALTH, int(default_ev)))
                elif ev == "Atk":
                    effort_values.append(Stat(StatEnum.ATTACK, int(default_ev)))
                elif ev == "Def":
                    effort_values.append(Stat(StatEnum.DEFENSE, int(default_ev)))
                elif ev == "SpA":
                    effort_values.append(Stat(StatEnum.SPECIAL_ATTACK, int(default_ev)))
                elif ev == "SpD":
                    effort_values.append(Stat(StatEnum.SPECIAL_DEFENSE, int(default_ev)))
                elif ev == "Spe":
                    effort_values.append(Stat(StatEnum.SPEED, int(default_ev)))
                else:
                    assert False

            base_key = f"{name}_{set_number}"
            counts[base_key] = counts.get(base_key, 0) + 1
            unique_key = f"{base_key}_{counts[base_key]}"
            pokemon[unique_key]: Pokemon = Pokemon(
                name=name,
                unique_key=unique_key,
                nature=get_nature_enum(nature),
                types=list(types),
                item=item,
                moves=moves,
                set_number=set_number,
                effort_values=effort_values
            )

            # Skip the png file line or get the end of file
            tokens: list[str] = get_next_non_newline(file).strip().split("\t")
    return pokemon


def get_battle_factory_pokemon() -> dict[str, Pokemon]:
    """
    Gets a name to Pokémon dict containing all possible battle factory Pokémon.
    :return: The name to Pokémon dict containing all possible battle factory Pokémon.
    """
    pokemon: dict[str, Pokemon] | None = None
    if not exists(FRESH_FACTORY_POKEMON_FILE):
        pokemon: dict[str, Pokemon] = __parse_battle_factory_pokemon__()
        with open(FRESH_FACTORY_POKEMON_FILE, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(pokemon)))
    else:
        with open(FRESH_FACTORY_POKEMON_FILE, "r") as fo:
            pokemon: dict[str, Pokemon] = cattr.structure(json.loads(fo.read()), dict[str, Pokemon])
    if pokemon is None:
        raise Exception("Failed to load battle factory pokemon")
    return pokemon


if __name__ == "__main__":
    g_pokemon: dict[str, Pokemon] = get_battle_factory_pokemon()
    pp(g_pokemon)
