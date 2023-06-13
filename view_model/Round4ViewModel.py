from collections import defaultdict
from pprint import pp

from repository.PokemonRepository import find_pokemon, find_pokemon_with_move
from use_case.TeamUseCase import TeamUseCase


def do_round_four(team_pokemon, choice_pokemon, opponent_pokemon, level):
    pass
    # if opponent_pokemon is not None:
    #     team_pokemon_ranks = rank_team_pokemon_against_opponents(
    #         team_pokemon,
    #         opponent_pokemon,
    #         level
    #     )
    #     combined_ranks = defaultdict(lambda: None)
    #     for poke_to_rank in team_pokemon_ranks.values():
    #         for poke, rank in poke_to_rank.items():
    #             if combined_ranks[poke] is None:
    #                 combined_ranks[poke] = rank
    #             if "defense" in poke:
    #                 combined_ranks[poke] = max(combined_ranks[poke],  rank)
    #             else:
    #                 combined_ranks[poke] = min(combined_ranks[poke], rank)
    #
    #     ordered_poke_ranks = defaultdict(lambda: set())
    #     for poke, rank in sorted(
    #             combined_ranks.items(),
    #             key=lambda item: item[1]
    #     ):
    #         ordered_poke_ranks[poke].add(rank)
    #
    #     pp("Team pokemon ranks")
    #     pp(ordered_poke_ranks, sort_dicts=False)
    #
    #     chosen_pokemon = ask_user_to_pick_pokemon(1, team_pokemon)
    #
    #     # Rank the types by which need to be covered
    #     weaknesses = get_weaknesses(chosen_pokemon)
    #     resistances = get_resistances(chosen_pokemon)
    #     remaining_pokemon = list(
    #         set(team_pokemon)
    #         .difference(set(chosen_pokemon))
    #         .union(choice_pokemon)
    #     )
    #     rank_from_weaknesses_and_resistances(remaining_pokemon, weaknesses, resistances)
    #
    #     new_chosen_pokemon = ask_user_to_pick_pokemon(1, remaining_pokemon)
    #     for poke in new_chosen_pokemon:
    #         chosen_pokemon.append(poke)
    #
    #     # Rank the types by which need to be covered
    #     weaknesses = get_weaknesses(chosen_pokemon)
    #     resistances = get_resistances(chosen_pokemon)
    #     remaining_pokemon = list(
    #         set(team_pokemon)
    #         .difference(set(chosen_pokemon))
    #         .union(choice_pokemon)
    #     )
    #     rank_from_weaknesses_and_resistances(remaining_pokemon, weaknesses, resistances)


class Round4ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            level=50
    ) -> None:
        self.__team_use_case__ = team_use_case
        self.__opponent_pokemon__ = None
        self.__level__ = level

    def set_pokemon_move(self, move):
        self.__opponent_pokemon__ = find_pokemon_with_move(move)

    def confirm_clicked(self) -> None:
        do_round_four(
            self.__team_use_case__.get_team_pokemon(),
            self.__team_use_case__.get_choice_pokemon(),
            self.__opponent_pokemon__,
            self.__level__
        )
