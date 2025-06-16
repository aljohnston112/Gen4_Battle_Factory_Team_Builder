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


class RoundStage(Enum):
    """
    Possible stages in a round.
    Middle battle is used for the second battle to the sixth battle, inclusive.
    """
    FIRST_BATTLE = 0
    MIDDLE_BATTLE = 1
    LAST_BATTLE = 2


class RoundUseCase:
    """
    A wrapper for the current round.
    """

    def __init__(self):
        """
        Sets the default round to round one.
        """
        self.__current_round__: Round = Round.ONE
        self.__observers__ = []
        self.__round_stage__: RoundStage = RoundStage.FIRST_BATTLE

    def set_current_round(self, current_round: Round) -> None:
        self.__current_round__: Round = current_round
        self.notify_observers()

    def notify_observers(self):
        for observer in self.__observers__:
            observer(self)

    def get_current_round(self) -> Round:
        return self.__current_round__

    def add_listener(self, __add_all_pokemon_names__):
        self.__observers__.append(__add_all_pokemon_names__)

    def set_round_stage(self, round_stage: RoundStage) -> None:
        self.__round_stage__ = round_stage


    def get_round_stage(self) -> RoundStage:
        return self.__round_stage__

