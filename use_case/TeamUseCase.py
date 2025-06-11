from enum import Enum

from data_class.Pokemon import Pokemon


class RoundStage(Enum):
    """
    An enum used to mark what stage a round is in.
    """
    FIRST_BATTLE = 0
    MIDDLE_BATTLE = 1
    LAST_BATTLE = 2


class TeamUseCase:
    """
    A wrapper for the team and choice Pokémon.
    """

    def __init__(
            self,
            team_pokemon: list[Pokemon],
            choice_pokemon: list[Pokemon]
    ) -> None:
        self.__team_pokemon__: list[Pokemon] = team_pokemon
        self.__choice_pokemon__: list[Pokemon] = choice_pokemon
        self.__round_stage__: RoundStage = RoundStage.FIRST_BATTLE

    def set_pokemon(
            self,
            team_pokemon: list[Pokemon],
            choice_pokemon: list[Pokemon]
    ) -> None:
        self.__team_pokemon__: list[Pokemon] = team_pokemon
        self.__choice_pokemon__: list[Pokemon] = choice_pokemon

    def get_team_pokemon(self) -> list[Pokemon]:
        return self.__team_pokemon__

    def get_choice_pokemon(self) -> list[Pokemon]:
        return self.__choice_pokemon__

    def set_round_stage(self, round_stage: RoundStage) -> None:
        self.__round_stage__ = round_stage

    def get_round_stage(self) -> RoundStage:
        return self.__round_stage__
