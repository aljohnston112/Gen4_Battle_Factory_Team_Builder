from data_class.Pokemon import Pokemon


class TeamUseCase:
    def __init__(
            self,
            team_pokemon: list[Pokemon],
            choice_pokemon: list[Pokemon]
    ) -> None:
        self.__team_pokemon__ = team_pokemon
        self.__choice_pokemon__ = choice_pokemon
        self.__is_last_battle__ = False

    def set_pokemon(
            self,
            team_pokemon: list[Pokemon],
            choice_pokemon: list[Pokemon]
    ) -> None:
        self.__team_pokemon__ = team_pokemon
        self.__choice_pokemon__ = choice_pokemon

    def get_team_pokemon(self) -> list[Pokemon]:
        return self.__team_pokemon__

    def get_choice_pokemon(self) -> list[Pokemon]:
        return self.__choice_pokemon__

    def set_is_last_battle(self, is_last_battle):
        self.__is_last_battle__ = is_last_battle

    def is_last_battle(self) -> bool:
        return self.__is_last_battle__
