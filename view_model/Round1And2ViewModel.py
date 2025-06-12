from algorithm.FrontierTeamBuilder import load_pokemon_ranks_accuracy
from data_class.BattleResult import BattleResult
from data_class.Hits import Hits
from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon, \
    get_pokemon_from_set, is_valid_round
from use_case.TeamUseCase import TeamUseCase, RoundStage
from view_model.TeamViewmodel import ask_user_to_pick_pokemon, \
    get_potential_threats_and_print_win_rates_and_coverage


def do_round_two(
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        opponent_pokemon: list[Pokemon],
        level: int,
        is_first_battle: bool,
        is_last_battle: bool,
        set_number: int
):
    do_round_one(player_pokemon, choice_pokemon, opponent_pokemon, level, set_number, is_first_battle, is_last_battle)


def do_round_one(
        player_pokemon: list[Pokemon],
        choice_pokemon: list[Pokemon],
        opponent_pokemon_in: list[Pokemon],
        level: int,
        set_number: int,
        is_first_battle: bool,
        is_last_battle: bool
) -> None:
    if set_number < 7:
        if is_last_battle:
            opponent_pokemon = \
                [p for p in opponent_pokemon_in if
                 is_valid_round(p, set_number + 1)]
        else:
            opponent_pokemon = \
                [p for p in opponent_pokemon_in if is_valid_round(p, set_number)]
            if set_number > 0:
                opponent_pokemon += \
                    [p for p in opponent_pokemon_in if
                     is_valid_round(p, set_number - 1)]
    else:
        opponent_pokemon = \
            [p for p in opponent_pokemon_in if is_valid_round(p, 3)]
        opponent_pokemon += [poke for poke in
                         opponent_pokemon_in if
                         is_valid_round(poke, 4)]
        opponent_pokemon += [poke for poke in
                         opponent_pokemon_in if
                         is_valid_round(poke, 5)]
        opponent_pokemon += [poke for poke in
                         opponent_pokemon_in if
                         is_valid_round(poke, 6)]
        opponent_pokemon += [poke for poke in
                         opponent_pokemon_in if
                         is_valid_round(poke, 7)]

    opponent_to_pokemon_to_hits: dict[Pokemon, dict[Pokemon, Hits]] = {}
    set_numbers = [set_number]
    if set_number > 0:
        set_numbers.append(set_number - 1)
    if set_number < 7:
        set_numbers.append(set_number + 1)
    all_ranks_accuracy = load_pokemon_ranks_accuracy()
    for opponent in opponent_pokemon:
        pokemon_to_hits = {}
        for set_number in set_numbers:
            ranks_accuracy = all_ranks_accuracy[set_number]
            battle_result: BattleResult = ranks_accuracy.get(opponent.unique_id)
            for poke in player_pokemon + choice_pokemon:
                if battle_result and poke.unique_id in battle_result.results:
                    hits = battle_result.results[poke.unique_id]
                    pokemon_to_hits[poke] = Hits(
                        hits_taken=hits.hits_given,
                        hits_given=hits.hits_taken
                    )
                else:
                    other_battle_result: BattleResult = ranks_accuracy.get(poke.unique_id)
                    if other_battle_result and opponent.unique_id in other_battle_result.results:
                        hits = other_battle_result.results[opponent.unique_id]
                        pokemon_to_hits[poke] = hits
        opponent_to_pokemon_to_hits[opponent] = {
            k: v for k, v in sorted(
                pokemon_to_hits.items(),
                key=lambda item: item[1].hits_given / item[1].hits_taken
            )
        }

    print("Team pokemon ranks")
    for opponent, pokemon_to_hits in opponent_to_pokemon_to_hits.items():
        opponent: Pokemon
        pokemon_to_hits: dict[Pokemon, Hits]
        print(f"--- Against {opponent.unique_id} ---")
        print(f"{'Pokémon':<20} {'Hits to KO':>12} {'Hits to be KOed':>18}")
        for poke, hits in sorted(
                pokemon_to_hits.items(),
                key=lambda item: 9999 if item[1].hits_taken == 0 or item[
                    1].hits_given == 0
                else item[1].hits_given / item[1].hits_taken
        ):
            poke: Pokemon
            hits: Hits
            hits_to_ko_opponent: float = hits.hits_given
            hits_to_get_koed: float = hits.hits_taken
            print(
                f"{poke.unique_id:<20} "
                f"{hits_to_ko_opponent:>12.2f} "
                f"{hits_to_get_koed:>18.2f}"
            )
        print()

    factory_pokemon = get_pokemon_from_set(set_number, is_last_battle)

    get_potential_threats_and_print_win_rates_and_coverage(
        level,
        set_numbers,
        factory_pokemon,
        player_pokemon,
        choice_pokemon,
        [],
        False
    )

    chosen_pokemon: list[Pokemon] = ask_user_to_pick_pokemon(1, player_pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(player_pokemon)
        .difference(set(chosen_pokemon))
    )


    get_potential_threats_and_print_win_rates_and_coverage(
        level,
        set_numbers,
        factory_pokemon,
        [p for p in choice_pokemon if p not in chosen_pokemon],
        remaining_pokemon,
        chosen_pokemon,
        is_first_battle
    )

    chosen_pokemon += ask_user_to_pick_pokemon(1, remaining_pokemon)
    remaining_pokemon: list[Pokemon] = list(
        set(player_pokemon)
        .difference(set(chosen_pokemon))
    )

    get_potential_threats_and_print_win_rates_and_coverage(
        level,
        set_numbers,
        factory_pokemon,
        [p for p in choice_pokemon if p not in chosen_pokemon],
        remaining_pokemon,
        chosen_pokemon,
        is_first_battle
    )


class Round1And2ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            is_round_2: bool,
            level: int
    ) -> None:
        self.__is_round_2: bool = is_round_2
        self.__team_use_case__: TeamUseCase = team_use_case
        self.__opponent_pokemon__: list[Pokemon] = []
        self.__level__: int = level

    def set_opponent_pokemon_names(
            self,
            opponent_pokemon_names: list[str]
    ) -> None:
        self.__opponent_pokemon__ = find_pokemon(
            pokemon_names=opponent_pokemon_names,
            move_names=None
        )

    def confirm_clicked(self) -> None:
        if not self.__is_round_2:
            do_round_one(
                self.__team_use_case__.get_team_pokemon(),
                self.__team_use_case__.get_choice_pokemon(),
                self.__opponent_pokemon__,
                self.__level__,
                0,
                self.__team_use_case__.get_round_stage() == RoundStage.FIRST_BATTLE,
                self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE
            )
        else:
            do_round_two(
                self.__team_use_case__.get_team_pokemon(),
                self.__team_use_case__.get_choice_pokemon(),
                self.__opponent_pokemon__,
                self.__level__,
                self.__team_use_case__.get_round_stage() == RoundStage.FIRST_BATTLE,
                self.__team_use_case__.get_round_stage() == RoundStage.LAST_BATTLE,
                1
            )
