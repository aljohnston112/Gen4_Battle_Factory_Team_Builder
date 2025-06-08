from collections import defaultdict

from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon, all_battle_factory_pokemon
from use_case.TeamUseCase import TeamUseCase
from view_model.Round1And2ViewModel import do_round_one, get_num_hits_attackers_need_do_to_defenders
from view_model.TeamViewmodel import ask_user_to_pick_pokemon, is_valid_round, get_potential_threats, \
    aggregate_and_print_win_rates


def do_round_three(
        pokemon: list[Pokemon],
        opponent_pokemon_in: list[Pokemon],
        level: int,
        is_last_battle: bool
):
    do_round_one(pokemon, opponent_pokemon_in, level, 2, is_last_battle)

    chosen_pokemon: list[Pokemon] = ask_user_to_pick_pokemon(1, pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(pokemon)
        .difference(set(chosen_pokemon))
    )

    opponent_pokemon = [poke for poke in all_battle_factory_pokemon.values() if is_valid_round(poke, 2)]
    if is_last_battle:
        opponent_pokemon += [poke for poke in all_battle_factory_pokemon.values() if is_valid_round(poke, 3)]
    else:
        opponent_pokemon += [poke for poke in all_battle_factory_pokemon.values() if is_valid_round(poke, 1)]

    potential_threats = get_potential_threats(chosen_pokemon, level, opponent_pokemon)

    opponent_to_pokemon_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            potential_threats,
            remaining_pokemon,
            level,
            True
        )

    pokemon_to_opponent_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            remaining_pokemon,
            potential_threats,
            level,
            False
        )

    aggregate_and_print_win_rates(opponent_pokemon, opponent_to_pokemon_to_hits, pokemon, pokemon_to_opponent_to_hits)
    chosen_pokemon: list[Pokemon] = ask_user_to_pick_pokemon(1, remaining_pokemon)
    potential_threats = get_potential_threats(chosen_pokemon, level, opponent_pokemon)

    opponent_to_pokemon_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            potential_threats,
            remaining_pokemon,
            level,
            True
        )

    pokemon_to_opponent_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            remaining_pokemon,
            potential_threats,
            level,
            False
        )
    aggregate_and_print_win_rates(opponent_pokemon, opponent_to_pokemon_to_hits, pokemon, pokemon_to_opponent_to_hits)



class Round3ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            level=50
    ) -> None:
        self.__team_use_case__ = team_use_case
        self.__opponent_pokemon__ = None
        self.__level__ = level

    def set_pokemon_name_and_move(self, name, move):
        self.__opponent_pokemon__ = find_pokemon([name], [move])

    def confirm_clicked(self) -> None:
        do_round_three(
            self.__team_use_case__.get_team_pokemon() + self.__team_use_case__.get_choice_pokemon(),
            self.__opponent_pokemon__,
            self.__level__,
            self.__team_use_case__.is_last_battle()
        )
