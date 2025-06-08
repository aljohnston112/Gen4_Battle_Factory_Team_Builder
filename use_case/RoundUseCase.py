from enum import Enum


class Round(Enum):
    """
    Used to switch the layout on the round number.
    """
    ONE = 0
    TWO = 1
    THREE = 2
    FOUR = 3
    FIVE = 4


class RoundUseCase:

    def __init__(self):
        self.__current_round__ = Round.ONE

    def set_current_round(self, current_round):
        self.__current_round__ = current_round

    def get_current_round(self):
        return self.__current_round__
