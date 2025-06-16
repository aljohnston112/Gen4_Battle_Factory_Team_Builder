from data_class.Pokemon import Pokemon
from use_case.PokemonUseCase import PokemonUseCase
from use_case.RoundUseCase import RoundStage, RoundUseCase
from use_case.TeamUseCase import TeamUseCase


class TeamViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            round_use_case: RoundUseCase,
            pokemon_use_cases: list[PokemonUseCase],
    ) -> None:
        self.__team_use_case__: TeamUseCase = team_use_case
        self.__round_use_case__: RoundUseCase = round_use_case
        self.__pokemon_use_cases__: list[PokemonUseCase] = pokemon_use_cases

    def on_new_data(self) -> None:
        round_stage: RoundStage = self.__round_use_case__.get_round_stage()

        # All Pokémon are considered team Pokémon for the first round
        # It makes the logic in the rest of the program easier
        if round_stage == RoundStage.FIRST_BATTLE:
            choice_pokemon: list[Pokemon] = []
            team_pokemon: list[Pokemon] = [
                poke for pokemon_use_case in self.__pokemon_use_cases__
                for poke in pokemon_use_case.get_pokemon()
            ]
        else:
            team_pokemon: list[Pokemon] = [
                poke for pokemon_use_case in self.__pokemon_use_cases__[0:3]
                for poke in pokemon_use_case.get_pokemon()
            ]
            choice_pokemon: list[Pokemon] = [
                poke for pokemon_use_case in self.__pokemon_use_cases__[3:]
                for poke in pokemon_use_case.get_pokemon()
            ]
        self.__team_use_case__.set_pokemon(
            team_pokemon=team_pokemon,
            choice_pokemon=choice_pokemon
        )

    def set_round_stage(self, battle_type: RoundStage) -> None:
        self.__round_use_case__.set_round_stage(battle_type)
        self.on_new_data()
