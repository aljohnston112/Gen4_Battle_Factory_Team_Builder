from data_class.Pokemon import Pokemon
from use_case.RoundUseCase import RoundStage


class TeamUseCase:
    """
    A wrapper for the team and choice Pokémon.
    """

    def __init__(
            self,
            team_pokemon: list[Pokemon],
            choice_pokemon: list[Pokemon]
    ) -> None:
        """
        Sets the team and choice Pokémon.
        The round stage will be set to the first battle.
        :param team_pokemon: The Pokémon on the user's team.
        :param choice_pokemon: The Pokémon the user can trade for.
        """
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
