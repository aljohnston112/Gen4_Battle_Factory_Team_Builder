import attr

from pokemon.Move import Move


@attr.s
class Pokemon:

    name: str = attr.ib()
    types: list[str] = attr.ib()
    ability: list[str] = attr.ib()
    item: str = attr.ib()
    moves: list[Move] = attr.ib()
