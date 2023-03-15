import attr

from data_class.Move import Move
from data_class.Type import PokemonType


@attr.define
class Pokemon:
    name: str
    types: list[PokemonType]
    ability: list[str]
    item: str
    moves: list[Move]

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name
