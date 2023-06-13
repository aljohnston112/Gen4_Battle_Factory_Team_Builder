from typing import Dict

from data_class.Type import PokemonType
from data_source.PokemonTypeDataSource import get_pokemon_types

all_pokemon_types: Dict[str, list[PokemonType]] = get_pokemon_types()
