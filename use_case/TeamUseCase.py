from typing import Callable

from data_class.Pokemon import Pokemon

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
        self.__trade_listeners__: list[Callable[[Pokemon, Pokemon], None]] = []

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

    def user_traded(self, pokemon_traded_away, pokemon_traded_for):
        for listener in self.__trade_listeners__:
            listener(pokemon_traded_away, pokemon_traded_for)

    def add_trade_listener(self, user_traded):
        self.__trade_listeners__.append(user_traded)