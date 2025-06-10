from collections import defaultdict
from typing import List

from data_class.Hits import Hits
from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon, \
    get_pokemon_from_set, is_valid_round
from use_case.TeamUseCase import TeamUseCase
from view_model.TeamViewmodel import ask_user_to_pick_pokemon, \
    get_num_hits_attackers_need_do_to_defenders, aggregate_hit_info, \
    get_potential_threats_and_print_win_rates_and_coverage


def do_round_two(
        pokemon: list[Pokemon],
        opponent_pokemon: list[Pokemon],
        level: int,
        is_last_battle: bool,
        set_number: int
):
    do_round_one(pokemon, opponent_pokemon, level, set_number, is_last_battle)

def do_round_one(
        player_pokemon: list[Pokemon],
        opponent_pokemon_in: list[Pokemon],
        level,
        set_number: int,
        is_last_battle: bool
) -> None:
    """
    Given a list of Pokémon, a list of opponents, and their level,
    Pokémon are ranked by how likely they are to beat each opponent.
    :param player_pokemon:
    :param opponent_pokemon_in:
    :param level:
    :param set_number:
    :param is_last_battle:
    :return:
    """

    opponent_pokemon = \
        [p for p in opponent_pokemon_in if is_valid_round(p, set_number)]
    if is_last_battle:
        opponent_pokemon += \
            [p for p in opponent_pokemon_in if is_valid_round(p, set_number + 1)]
    elif set_number > 0:
        opponent_pokemon += \
            [p for p in opponent_pokemon_in if is_valid_round(p, set_number - 1)]

    opponent_to_pokemon_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            attackers=opponent_pokemon,
            defenders=player_pokemon,
            level=level,
            is_opponent=True
        )

    pokemon_to_opponent_to_hits: defaultdict[Pokemon, dict[Pokemon, float]] = \
        get_num_hits_attackers_need_do_to_defenders(
            attackers=player_pokemon,
            defenders=opponent_pokemon,
            level=level,
            is_opponent=False
        )

    sorted_opponent_to_pokemon_to_rank: dict[Pokemon, dict[Pokemon, Hits]] = aggregate_hit_info(
        opponent_to_pokemon_to_hits=opponent_to_pokemon_to_hits,
        pokemon_to_opponent_to_hits=pokemon_to_opponent_to_hits
    )

    print("Team pokemon ranks")
    for opponent, pokemon_to_hits in sorted_opponent_to_pokemon_to_rank.items():
        opponent: Pokemon
        pokemon_to_hits: dict[Pokemon, Hits]
        print(f"\n--- Against {opponent.unique_key} ---")
        print(f"{'Pokémon':<20} {'Hits to KO':>12} {'Hits to be KOed':>18}")
        for poke, hits in sorted(
                pokemon_to_hits.items(),
                key=lambda item: 9999 if item[1].hits_taken == 0 or item[1].hits_given == 0
                else item[1].hits_given / item[1].hits_taken
        ):
            poke: Pokemon
            hits: Hits
            hits_to_ko_opponent: float = hits.hits_given
            hits_to_get_koed: float = hits.hits_taken
            print(f"{poke.unique_key:<20} {hits_to_ko_opponent:>12.2f} {hits_to_get_koed:>18.2f}")

    factory_pokemon = get_pokemon_from_set(set_number)
    set_numbers = [set_number, set_number + 1]
    if set_number > 0:
        set_numbers.append(set_number - 1)
    get_potential_threats_and_print_win_rates_and_coverage([], level, factory_pokemon, player_pokemon, set_numbers)

    chosen_pokemon: list[Pokemon] = ask_user_to_pick_pokemon(1, player_pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(player_pokemon)
        .difference(set(chosen_pokemon))
    )
    get_potential_threats_and_print_win_rates_and_coverage(chosen_pokemon, level, factory_pokemon, remaining_pokemon, set_numbers)


    chosen_pokemon += ask_user_to_pick_pokemon(1, remaining_pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(player_pokemon)
        .difference(set(chosen_pokemon))
    )
    get_potential_threats_and_print_win_rates_and_coverage(chosen_pokemon, level, factory_pokemon, remaining_pokemon, set_numbers)


class Round1And2ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            is_round_2=False,
            level=50
    ) -> None:
        self.__is_round_2 = is_round_2
        self.__team_use_case__ = team_use_case
        self.__opponent_pokemon__ = []
        self.__level__ = level

    def set_opponent_pokemon_names(
            self,
            opponent_pokemon_names: List[str]
    ) -> None:
        self.__opponent_pokemon__ = find_pokemon(opponent_pokemon_names)

    def confirm_clicked(self) -> None:
        pokemon = self.__team_use_case__.get_team_pokemon() + \
                  self.__team_use_case__.get_choice_pokemon()
        if not self.__is_round_2:
            do_round_one(
                pokemon,
                self.__opponent_pokemon__,
                self.__level__,
                0,
                self.__team_use_case__.is_last_battle()
            )
        else:
            do_round_two(
                pokemon,
                self.__opponent_pokemon__,
                self.__level__,
                self.__team_use_case__.is_last_battle(),
                1
            )
