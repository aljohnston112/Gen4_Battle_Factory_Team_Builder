from data_class.Pokemon import Pokemon
from data_class.Type import PokemonType
from data_source.PokemonDataSource import get_battle_factory_pokemon
from use_case.RoundUseCase import Round

all_battle_factory_pokemon: dict[str, Pokemon] = get_battle_factory_pokemon()


def find_pokemon_with_type(
        pokemon_type: PokemonType | None,
        round_number: Round,
        is_last_battle: bool,
) -> list[Pokemon]:
    pokemon: list[Pokemon] = []
    all_pokemon = get_pokemon_from_round(
        round_number=round_number.value,
        is_last_battle=is_last_battle
    )
    if pokemon_type is not None:
        for poke in all_pokemon:
            poke: Pokemon
            if pokemon_type in poke.types:
                pokemon_type: PokemonType
                pokemon.append(poke)
        return pokemon
    else:
        return all_pokemon


def find_pokemon_with_move(
        move_name: str,
        is_last_battle: bool
) -> list[Pokemon]:
    pokemon: list[Pokemon] = []
    all_pokemon: list[Pokemon] = get_pokemon_from_round(
        round_number=3,
        is_last_battle=is_last_battle
    )
    for poke in all_pokemon:
        poke: Pokemon
        if move_name == poke.moves[0].name:
            pokemon.append(poke)
    return pokemon


def is_from_round(pokemon: Pokemon, round_number: int) -> bool:
    parts = pokemon.unique_id.split('_')
    return int(parts[1]) == round_number


def get_pokemon_from_round(
        round_number: int,
        is_last_battle: bool
) -> list[Pokemon]:
    if round_number < 7:
        if is_last_battle:
            pokemon_list: list[Pokemon] = [
                poke for poke in all_battle_factory_pokemon.values()
                if is_from_round(poke, round_number + 1)
            ]
        else:
            pokemon_list: list[Pokemon] = [
                p for p in all_battle_factory_pokemon.values()
                if is_from_round(p, round_number)
            ]
            if round_number > 0:
                pokemon_list += [
                    poke for poke in all_battle_factory_pokemon.values()
                    if is_from_round(poke, round_number - 1)]
    else:
        pokemon_list: list[Pokemon] = []
        for i in range(3, 8):
            pokemon_list += [
                p for p in all_battle_factory_pokemon.values()
                if is_from_round(p, i)
            ]
    return pokemon_list


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
        i: int
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
