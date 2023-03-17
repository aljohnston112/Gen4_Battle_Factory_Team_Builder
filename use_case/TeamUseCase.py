from typing import List

from data_class.Pokemon import Pokemon


class TeamUseCase:
    def __init__(
            self,
            team_pokemon: List[Pokemon],
            choice_pokemon: List[Pokemon]
    ) -> None:
        self.__team_pokemon__ = team_pokemon
        self.__choice_pokemon__ = choice_pokemon

    def set_pokemon(
            self,
            team_pokemon: List[Pokemon],
            choice_pokemon: List[Pokemon]
    ) -> None:
        self.__team_pokemon__ = team_pokemon
        self.__choice_pokemon__ = choice_pokemon

    def get_team_pokemon(self) -> List[Pokemon]:
        return self.__team_pokemon__

    def get_choice_pokemon(self) -> List[Pokemon]:
        return self.__choice_pokemon__
