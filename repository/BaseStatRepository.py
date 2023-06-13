from data_class.BaseStats import BaseStats
from data_source.BaseStatDataSource import get_base_stats

all_pokemon_stats: dict[str, BaseStats] = get_base_stats()



