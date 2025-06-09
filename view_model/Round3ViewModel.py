from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon, get_pokemon_from_set
from use_case.TeamUseCase import TeamUseCase
from view_model.Round1And2ViewModel import do_round_one
from view_model.TeamViewmodel import ask_user_to_pick_pokemon, \
    get_potential_threats_and_print_win_rates, print_coverage


def do_round_three(
        pokemon: list[Pokemon],
        opponent_pokemon_in: list[Pokemon],
        level: int,
        is_last_battle: bool
):
    do_round_one(pokemon, opponent_pokemon_in, level, 2, is_last_battle)

    opponent_pokemon = get_pokemon_from_set(2, is_last_battle)

    chosen_pokemon: list[Pokemon] = ask_user_to_pick_pokemon(1, pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(pokemon)
        .difference(set(chosen_pokemon))
    )
    get_potential_threats_and_print_win_rates(chosen_pokemon, level, opponent_pokemon, remaining_pokemon)

    chosen_pokemon: list[Pokemon] = ask_user_to_pick_pokemon(1, remaining_pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(remaining_pokemon)
        .difference(set(chosen_pokemon))
    )
    get_potential_threats_and_print_win_rates(chosen_pokemon, level, opponent_pokemon, remaining_pokemon)

    set_numbers = [2]
    if is_last_battle:
        set_numbers.append(3)
    else:
        set_numbers.append(1)
    print_coverage(opponent_pokemon, remaining_pokemon, set_numbers)



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
