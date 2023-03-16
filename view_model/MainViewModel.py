from collections import defaultdict
from pprint import pprint
from typing import List

from data_class.Pokemon import Pokemon
from repository.MoveRepository import moves
from repository.TypeChartRepository import get_defense_multipliers, get_defense_multipliers_for_list, \
    get_max_attack_power_for_list
from use_case.PokemonPickerUseCase import PokemonPickerUseCase


def max_damage_attacker_can_do_to_defender(
        attacker: Pokemon,
        defender: Pokemon
):
    opponent_defense_multipliers = get_defense_multipliers(defender)
    max_damage = 0
    for pokemon_move in attacker.moves:
        max_damage = max(
            opponent_defense_multipliers[pokemon_move.move_type] * moves[pokemon_move.name].power,
            max_damage
        )
    return max_damage


def get_max_damage_attackers_can_do_to_defenders(attacking_pokemon, defending_pokemon):
    defender_to_attacker_to_max_damage = defaultdict(
        lambda: defaultdict(lambda: 0.0)
    )
    for defender in defending_pokemon:
        pokemon_to_max_damage = defaultdict(lambda: 0.0)
        for member in attacking_pokemon:
            pokemon_to_max_damage[member] = max_damage_attacker_can_do_to_defender(
                member,
                defender
            )
        defender_to_attacker_to_max_damage[defender] = pokemon_to_max_damage
    return defender_to_attacker_to_max_damage


def rank_attack_of_attackers_against_defenders(
        attackers: List[Pokemon],
        defenders: List[Pokemon]
):
    """
    Ranks pokemon by how much attackers can do to the defenders.
    :param attackers: The attacking pokemon.
    :param defenders: The defending pokemon.
    :return: 
    A dictionary of defending pokemon
    to a list of attacking pokemon
    in order by how much they can damage the corresponding defender.
    """
    opponent_to_pokemon_to_max_damage = get_max_damage_attackers_can_do_to_defenders(
        attackers,
        defenders
    )

    # Sort by max damage
    opponent_to_pokemon_rank = defaultdict(lambda: [])
    pokemon_ranks = defaultdict(lambda: defaultdict(lambda: []))
    for opponent in opponent_to_pokemon_to_max_damage.keys():
        opponent_to_pokemon_rank[opponent] = sorted(
            (poke for poke in opponent_to_pokemon_to_max_damage[opponent]),
            key=lambda poke: opponent_to_pokemon_to_max_damage[opponent][poke],
            reverse=True
        )

        rank = 0
        last_damage = opponent_to_pokemon_to_max_damage[opponent][
            next(iter(opponent_to_pokemon_rank[opponent]))
        ]
        for poke in opponent_to_pokemon_rank[opponent]:
            damage = opponent_to_pokemon_to_max_damage[opponent][poke]
            if damage != last_damage:
                rank = rank + 1
            pokemon_ranks[opponent][rank].append(poke)
            last_damage = damage
    return pokemon_ranks


def rank_defense_of_team_against_opponents(
        team_pokemon: List[Pokemon],
        opponent_pokemon: List[Pokemon]
):
    pokemon_to_opponent_to_max_damage = get_max_damage_attackers_can_do_to_defenders(
        opponent_pokemon,
        team_pokemon
    )

    # Map from opponent to pokemon to max damage
    opponent_to_pokemon_to_max_damage = defaultdict(lambda: defaultdict(lambda: 0.0))
    for opponent in opponent_pokemon:
        for pokemon in pokemon_to_opponent_to_max_damage.keys():
            opponent_to_pokemon_to_max_damage[opponent][pokemon] = \
                pokemon_to_opponent_to_max_damage[pokemon][opponent]

    # Sort by max damage
    opponent_to_pokemon_rank = defaultdict(lambda: [])
    pokemon_ranks = defaultdict(lambda: defaultdict(lambda: []))
    for opponent in opponent_to_pokemon_to_max_damage.keys():
        opponent_to_pokemon_rank[opponent] = \
            sorted(
                (poke for poke in opponent_to_pokemon_to_max_damage[opponent]),
                key=lambda poke: opponent_to_pokemon_to_max_damage[opponent][poke],
            )

        # rank by max damage
        rank = 0
        last_damage = opponent_to_pokemon_to_max_damage[opponent][
            next(iter(opponent_to_pokemon_rank[opponent]))
        ]
        for poke in opponent_to_pokemon_rank[opponent]:
            damage = opponent_to_pokemon_to_max_damage[opponent][poke]
            if damage != last_damage:
                rank = rank + 1
            pokemon_ranks[opponent][rank].append(poke)
            last_damage = damage

    return pokemon_ranks


def rank_team_pokemon_against_each_opponent(
        opponent_to_pokemon_attack_rank,
        opponent_to_pokemon_defense_rank
):
    pokemon_ranks = defaultdict(lambda: 0)
    for pokemon_attack_ranks in opponent_to_pokemon_attack_rank.values():
        for i, poke_list in pokemon_attack_ranks.items():
            for poke in poke_list:
                pokemon_ranks[poke] += i
    for pokemon_defense_ranks in opponent_to_pokemon_defense_rank.values():
        for i, poke_list in pokemon_defense_ranks.items():
            for poke in poke_list:
                pokemon_ranks[poke] += i
    pokemon_ranks_out = sorted(pokemon_ranks.items(), key=lambda item: item[1])
    return pokemon_ranks_out


def rank_team_against_opponents(team_pokemon, opponent_pokemon):
    opponent_to_pokemon_attack_rank = rank_attack_of_attackers_against_defenders(
        team_pokemon,
        opponent_pokemon
    )
    opponent_to_pokemon_defense_rank = rank_defense_of_team_against_opponents(
        team_pokemon,
        opponent_pokemon,
    )
    pokemon_ranks = rank_team_pokemon_against_each_opponent(
        opponent_to_pokemon_attack_rank,
        opponent_to_pokemon_defense_rank
    )

    return pokemon_ranks


def print_pokemon_ranks(pokemon, opponent_pokemon):
    team_pokemon_ranks = rank_team_against_opponents(
        pokemon,
        opponent_pokemon
    )
    pprint("Team pokemon ranks")
    pprint(team_pokemon_ranks)


def get_weaknesses(pokemon):
    defense_multipliers = get_defense_multipliers_for_list(pokemon)

    # Average defense multipliers
    all_defense_multipliers = defaultdict(lambda: [])
    for poke in pokemon:
        if poke.name in defense_multipliers.keys():
            for poke_type in defense_multipliers[poke.name]:
                all_defense_multipliers[poke_type].append(
                    defense_multipliers[poke.name][poke_type]
                )

    average_defense_multipliers = {
        poke_type: sum(multipliers) / len(multipliers)
        for poke_type, multipliers in all_defense_multipliers.items()
    }

    # Filter out the ones less than 1.0
    weaknesses_of_team = {
        poke_type: multiplier
        for poke_type, multiplier in sorted(
            average_defense_multipliers.items(),
            key=lambda item: item[1],
            reverse=True
        )
    }
    return weaknesses_of_team


def get_resistances(choice_pokemon):
    pokemon_to_max_attack_powers = get_max_attack_power_for_list(choice_pokemon)
    team_max_attack_powers = defaultdict(lambda: 0.0)
    for pokemon in pokemon_to_max_attack_powers.keys():
        for poke_type in pokemon_to_max_attack_powers[pokemon].keys():
            team_max_attack_powers[poke_type] = max(
                team_max_attack_powers[poke_type],
                pokemon_to_max_attack_powers[pokemon][poke_type]
            )
    sorted_team_max_attack_powers = {
        poke_type: power
        for poke_type, power in sorted(team_max_attack_powers.items(), key=lambda item: item[1])
    }
    return sorted_team_max_attack_powers


def ask_user_to_pick_pokemon(num_pokemon, team_pokemon):
    pokemon_picker_use_case = PokemonPickerUseCase()
    chosen_pokemon_names = pokemon_picker_use_case.got_pokemon_choices_from_user(
        num_pokemon,
        team_pokemon
    )
    chosen_pokemon = [
        team_poke
        for team_poke in team_pokemon
        if team_poke.name in chosen_pokemon_names
    ]
    return chosen_pokemon


def rank_types_by_weakness_and_resistance(weaknesses, resistances):
    weakness_ranks = defaultdict(lambda: [])
    rank = 0
    last_weakness = next(iter(weaknesses.items()))[1]
    for poke_type, weakness in weaknesses.items():
        if weakness != last_weakness:
            rank = rank + 1
        weakness_ranks[rank].append(poke_type)
        last_weakness = weakness

    resistance_ranks = defaultdict(lambda: [])
    rank = 0
    last_resistance = next(iter(resistances.items()))[1]
    for poke_type, resistance in resistances.items():
        if resistance != last_resistance:
            rank = rank + 1
        resistance_ranks[rank].append(poke_type)
        last_resistance = resistance

    type_ranks = defaultdict(lambda: [])
    for rank, poke_types in weakness_ranks.items():
        for poke_type in poke_types:
            type_ranks[rank].append(poke_type)
    for rank, poke_types in resistance_ranks.items():
        for poke_type in poke_types:
            type_ranks[rank].append(poke_type)
    return type_ranks


def rank_from_weaknesses_and_resistances(
        remaining_pokemon,
        weaknesses,
        resistances
):
    type_ranks = rank_types_by_weakness_and_resistance(weaknesses, resistances)


class MainViewModel:

    def __init__(self):
        pass

    def confirm_clicked_round_one(
            self,
            team_pokemon,
            choice_pokemon,
            opponent_pokemon
    ):
        print_pokemon_ranks(team_pokemon, opponent_pokemon)
        # Print choice ranks if not the first battle
        if len(choice_pokemon) != 0:
            print_pokemon_ranks(choice_pokemon, opponent_pokemon)

    def confirm_clicked_round_two(
            self,
            team_pokemon,
            choice_pokemon,
            opponent_pokemon
    ):
        print_pokemon_ranks(team_pokemon, opponent_pokemon)
        chosen_pokemon = ask_user_to_pick_pokemon(2, team_pokemon)

        # Rank the types by which need to be covered
        weaknesses = get_weaknesses(chosen_pokemon)
        resistances = get_resistances(chosen_pokemon)
        remaining_pokemon = set(team_pokemon).difference(set(chosen_pokemon))
        rank_from_weaknesses_and_resistances(remaining_pokemon, weaknesses, resistances)
        pprint(True)
        # Print choice ranks if not the first battle
        if len(choice_pokemon) != 0:
            print_pokemon_ranks(choice_pokemon, opponent_pokemon)


def do_round_three(team, choices):
    pass

# def do_round_one_two(player_pokemon_names, player_pokemon_moves):
#     # Get opponent data_class names
#     round_one_two_use_case = RoundOneTwoUseCase()
#     opponent_pokemon_names = round_one_two_use_case.get_pokemon_names()
#
#     # Find the data_class objects
#     player_pokemon = find_pokemon(player_pokemon_names, player_pokemon_moves)
#     opponent_pokemon = find_pokemon(opponent_pokemon_names)
#
#     player_defense_ranks, opponent_defense_ranks = get_defense_ranks(
#         player_pokemon,
#         opponent_pokemon,
#     )
#
#     print_ranks(player_pokemon, player_defense_ranks, opponent_defense_ranks)


# def do_round_three(player_pokemon_names, player_pokemon_moves):
#     round_three_use_case = RoundThreeUseCase()
#     opponent_pokemon_name, opponent_pokemon_move = round_three_use_case.get_pokemon_name_and_move()
#
#     player_pokemon = find_pokemon(player_pokemon_names, player_pokemon_moves)
#     opponent_pokemon = find_pokemon([opponent_pokemon_name], [opponent_pokemon_move])
#     player_defense_ranks, opponent_defense_ranks = get_defense_ranks(player_pokemon, opponent_pokemon)
#     print_ranks(player_pokemon, player_defense_ranks, opponent_defense_ranks)
#
#     # Get weakness of all data_class
#     player_defense_multipliers = get_defense_multipliers(player_pokemon)
#
#     # Find the weakness of the team
#     team_defense_multipliers = defaultdict(list)
#     for defense_multipliers in player_defense_multipliers.values():
#         for poke_type, mul in defense_multipliers:
#             team_defense_multipliers[poke_type].append(mul)
#     team_defense_multiplier_averages = {
#         poke_type: sum(multipliers) / len(multipliers)
#         for poke_type, multipliers in team_defense_multipliers
#     }
#
#     # Rank team by weakness score
#     # Check if choices will cause better rank
#     # If so, rank those
#
#
# def get_defense_ranks_for_defender(
#         attacking_pokemon: Pokemon,
#         defending_pokemon: Pokemon,
#         defending_pokemon_defense_multipliers: defaultdict[str, defaultdict[PokemonType, float]]
# ) -> dict[PokemonType, float]:
#     defender_defense_ranks = defaultdict(lambda: list())
#     all_moves = moves
#     for attackers_move in attacking_pokemon.moves:
#         detailed_move = all_moves[attackers_move.name]
#         if detailed_move.power != 0 and defending_pokemon != "":
#             # power of moves times defense multiplier
#             defender_defense_ranks[detailed_move.move_type].append(
#                 detailed_move.power *
#                 defending_pokemon_defense_multipliers[defending_pokemon.name][detailed_move.move_type]
#             )
#     defender_defense_rank_averages = {
#         poke_type:
#             sum(defender_defense_ranks[poke_type]) /
#             len(defender_defense_ranks[poke_type])
#         for poke_type in defender_defense_ranks.keys()
#     }
#     return defender_defense_rank_averages
#
#
# def print_ranks(player_pokemon, player_defense_ranks, opponent_defense_ranks):
#     defense_scores = defaultdict(lambda: 0)
#     offense_scores = defaultdict(lambda: 0)
#     for player_pokemon in player_pokemon:
#         defense_scores[player_pokemon.name] += sum(player_defense_ranks[player_pokemon.name].values())
#         offense_scores[player_pokemon.name] += sum(opponent_defense_ranks[player_pokemon.name].values())
#
#     pokemon_ranks = defaultdict(lambda: 0)
#     print("Defense:")
#     print(sorted(defense_scores.items(), key=lambda k: k[1]))
#     print("Offense:")
#     print(sorted(offense_scores.items(), key=lambda k: k[1], reverse=True))
#     for i, poke in enumerate(sorted(defense_scores.items(), key=lambda k: k[1])):
#         pokemon_ranks[poke[0]] += i
#     for i, poke in enumerate(sorted(offense_scores.items(), key=lambda k: k[1], reverse=True)):
#         pokemon_ranks[poke[0]] += i
#     print("Rank")
#     print(sorted(pokemon_ranks.items(), key=lambda k: k[1]))
#
#
#
#
# def get_defense_ranks(
#         player_pokemon,
#         opponent_pokemon
# ) -> tuple[
#     Dict[str, Dict[PokemonType, float]],
#     Dict[str, Dict[PokemonType, float]]
# ]:
#     player_defense_multipliers = get_defense_multipliers(player_pokemon)
#     opponent_defense_multipliers = get_defense_multipliers(opponent_pokemon)
#
#     # {playerPokemon -> {type -> list[float]}}
#     player_defense_ranks = defaultdict(lambda: defaultdict(lambda: list[float]()))
#     opponent_defense_ranks = defaultdict(lambda: defaultdict(lambda: list[float]()))
#
#     for opponent in opponent_pokemon:
#         for player in player_pokemon:
#             single_player_defense_ranks = get_defense_ranks_for_defender(
#                 opponent,
#                 player,
#                 player_defense_multipliers
#             )
#             for poke_type in single_player_defense_ranks.keys():
#                 player_defense_ranks[player.name][poke_type].append(
#                     single_player_defense_ranks[poke_type]
#                 )
#
#             single_opponent_defense_ranks = get_defense_ranks_for_defender(
#                 player,
#                 opponent,
#                 opponent_defense_multipliers
#             )
#             for poke_type in single_opponent_defense_ranks.keys():
#                 opponent_defense_ranks[player.name][poke_type].append(
#                     single_opponent_defense_ranks[poke_type]
#                 )
#
#     # Calculate averages
#     player_defense_ranks_average = {
#         name:
#             {
#                 poke_type:
#                     sum(player_defense_ranks[name][poke_type]) /
#                     len(player_defense_ranks[name][poke_type])
#                 for poke_type in player_defense_ranks[name]
#             }
#         for name in player_defense_ranks.keys()
#     }
#
#     opponent_defense_ranks_average = {
#         name:
#             {
#                 poke_type:
#                     sum(opponent_defense_ranks[name][poke_type]) /
#                     len(opponent_defense_ranks[name][poke_type])
#                 for poke_type in opponent_defense_ranks[name]
#             }
#         for name in opponent_defense_ranks.keys()
#     }
#     return player_defense_ranks_average, opponent_defense_ranks_average
