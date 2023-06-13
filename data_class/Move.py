from attr import frozen

from data_class.Category import Category
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

    category: Category
    """
    Whether the move is special or physical
    """

    power: int
    """
    The power of the move.
    """

    accuracy: int
    """
    The accuracy of the move.
    """


@frozen
class LearnableMove:
    name: str
    level: int
    is_move_tutor: bool
    is_egg_move: bool
    is_pre_evolution: bool
