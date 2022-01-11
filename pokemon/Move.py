import attr


@attr.s(frozen=True)
class Move:

    name: str = attr.ib()
    type_: str = attr.ib()
    split: str = attr.ib()


@attr.s
class DetailedMove(Move):
    power: int = attr.ib()
    accuracy: int = attr.ib()
