from itertools import groupby

from repository.PokemonRepository import find_pokemon
from use_case.TeamUseCase import TeamUseCase



def do_round_three(team_pokemon, choice_pokemon, opponent_pokemon, level):
    pass
    # # Remove all duplicates but the lowest set
    # sorted_opponent_pokemon = sorted(opponent_pokemon, key=lambda op: (op.name, op.set_number))
    # grouped_opponent_pokemon = groupby(sorted_opponent_pokemon, key=lambda op: op.name)
    # opponent_pokemon = [
    #     min(
    #         group,
    #         key=lambda op: op.set_number
    #     ) for _, group in grouped_opponent_pokemon
    # ]
    #
    # print_pokemon_ranks(
    #     team_pokemon,
    #     opponent_pokemon,
    #     level
    # )
    #
    # chosen_pokemon = ask_user_to_pick_pokemon(1, team_pokemon)
    #
    # # Rank the types by which need to be covered
    # weaknesses = get_weaknesses(chosen_pokemon)
    # resistances = get_resistances(chosen_pokemon)
    # remaining_pokemon = list(
    #     set(team_pokemon)
    #     .difference(set(chosen_pokemon))
    #     .union(choice_pokemon)
    # )
    # rank_from_weaknesses_and_resistances(remaining_pokemon, weaknesses, resistances)
    #
    # new_chosen_pokemon = ask_user_to_pick_pokemon(1, remaining_pokemon)
    # for poke in new_chosen_pokemon:
    #     chosen_pokemon.append(poke)
    #
    # # Rank the types by which need to be covered
    # weaknesses = get_weaknesses(chosen_pokemon)
    # resistances = get_resistances(chosen_pokemon)
    # remaining_pokemon = list(
    #     set(team_pokemon)
    #     .difference(set(chosen_pokemon))
    #     .union(choice_pokemon)
    # )
    # rank_from_weaknesses_and_resistances(remaining_pokemon, weaknesses, resistances)


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
            self.__team_use_case__.get_team_pokemon(),
            self.__team_use_case__.get_choice_pokemon(),
            self.__opponent_pokemon__,
            self.__level__
        )
