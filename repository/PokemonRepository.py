from typing import Collection

from data_class.Pokemon import Pokemon
from data_class.Type import PokemonType
from data_source.PokemonDataSource import get_battle_factory_pokemon

all_battle_factory_pokemon: dict[str, Pokemon] = get_battle_factory_pokemon()


def find_pokemon_with_type(pokemon_type: PokemonType | None) -> Collection[Pokemon]:
    p: list[Pokemon] = []
    if pokemon_type is not None:
        for poke in all_battle_factory_pokemon.values():
            poke: Pokemon
            if pokemon_type in poke.types:
                pokemon_type: PokemonType
                p.append(poke)
        return p
    else:
        return all_battle_factory_pokemon.values()


def find_pokemon_with_move(move_name: str) -> list[Pokemon]:
    p: list[Pokemon] = []
    for poke in all_battle_factory_pokemon.values():
        poke: Pokemon
        if move_name == poke.moves[0].name:
            p.append(poke)
    return p


def find_pokemon(
        pokemon_names: list[str],
        move_names: list[str] | None
) -> list[Pokemon]:
    """
    Finds the Pokémon objects with the given names and moves.
    :param pokemon_names: The names of the Pokémon objects.
    :param move_names: The corresponding move names of the Pokémon objects.
                       If an empty string is given or move_names is None,
                       all Pokémon with the given corresponding name will be returned.
    :return:
    A list of Pokémon objects that match the given names and moves.
    """
    found_pokemon: list[Pokemon] = []
    for i, name in enumerate(pokemon_names):
        i :int
        name: str
        if name != "":
            found: bool = False
            for poke in all_battle_factory_pokemon.values():
                poke: Pokemon
                could_be: bool = False
                if name in poke.name:
                    if move_names is not None and move_names[i] != "":
                        move_name: str = move_names[i].lower()
                        could_be = any(move_name == move.name.lower()
                                       for move in poke.moves)
                    else:
                        could_be: bool = True
                if could_be:
                    found_pokemon.append(poke)
                    found: bool = True
            if not found:
                print("Pokemon not found: " + name + "\n")
    return found_pokemon


def is_valid_round(pokemon: Pokemon, round_number: int) -> bool:
    parts = pokemon.unique_id.split('_')
    return int(parts[1]) == round_number


def get_pokemon_from_set(set_number: int):
    pokemon_list: list[Pokemon] = [p for p in
                                   all_battle_factory_pokemon.values() if
                                   is_valid_round(p, set_number)]
    pokemon_list += [poke for poke in
                     all_battle_factory_pokemon.values() if
                     is_valid_round(poke, set_number + 1)]
    if set_number > 0:
        pokemon_list += [poke for poke in
                         all_battle_factory_pokemon.values() if
                         is_valid_round(poke, set_number - 1)]
    return pokemon_list
