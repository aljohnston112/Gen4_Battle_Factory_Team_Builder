from attr import frozen

from data_class.Split import Split
from data_class.Type import PokemonType


@frozen
class Move:
    """
    Represents a data_class move.
    """

    name: str
    """
    The name of the move.
    """

    move_type: PokemonType
    """
    The type of the move
    """

    split: Split
    """
    Whether the move is special or physical
    """


@frozen
class DetailedMove(Move):
    """
    Represents a detailed data_class move.
    """

    power: int
    """
    The power of the move.
    """

    accuracy: int
    """
    The accuracy of the move.
    """
