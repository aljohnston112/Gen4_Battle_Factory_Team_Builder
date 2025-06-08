from data_class.Type import PokemonType
from data_source.PokemonTypeDataSource import get_pokemon_types

all_pokemon_types: dict[str, set[PokemonType]] = get_pokemon_types()
