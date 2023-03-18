

class MainViewModel:

    def __init__(self):
        pass


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
