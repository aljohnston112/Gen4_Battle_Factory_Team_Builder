from enum import Enum


class Round(Enum):
    """
    Possible round numbers in the battle factory.
    EIGHT is used for round 8 and up.
    """
    ONE = 0
    TWO = 1
    THREE = 2
    FOUR = 3
    FIVE = 4
    SIX = 5
    SEVEN = 6
    EIGHT = 7


class RoundUseCase:
    """
    A wrapper for the current round.
    """

    def __init__(self):
        self.__current_round__: Round = Round.ONE

    def set_current_round(self, current_round: Round) -> None:
        self.__current_round__ = current_round

    def get_current_round(self) -> Round:
        return self.__current_round__
