from typing import Dict, List

from data_class.Pokemon import Pokemon
from data_source.PokemonDataSource import get_battle_factory_pokemon

pokemon: Dict[str, Pokemon] = get_battle_factory_pokemon()


def find_pokemon(
        pokemon_names: List[str],
        move_names: List[str] = None
) -> List[Pokemon]:
    """
    Finds the Pokemon objects with the given names and moves.
    :param pokemon_names: The names of the data_class.
    :param move_names: The corresponding move names of the data_class.
    :return:
    A list of Pokemon objects that match the given names and moves.
    """
    the_pokemon = []
    for i, name in enumerate(pokemon_names):
        if name != "":
            found = False
            for poke in pokemon.values():
                if name in poke.name:
                    could_be = False
                    if move_names is not None and move_names[i] != "":
                        move_name = move_names[i]
                        for detailed_move in poke.moves:
                            if move_name == detailed_move.name:
                                could_be = True
                    else:
                        could_be = True
                    if could_be:
                        the_pokemon.append(poke)
                        found = True
            if not found:
                print("Pokemon not found: " + name + "\n")
    return the_pokemon
