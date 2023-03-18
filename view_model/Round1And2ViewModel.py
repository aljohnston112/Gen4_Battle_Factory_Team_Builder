from collections import defaultdict
from pprint import pprint, pp
from typing import List, Dict, DefaultDict

from data_class.Pokemon import Pokemon, get_defense_multipliers_for_list, get_max_attack_power_for_list, \
    max_damage_attacker_can_do_to_defender
from data_class.Type import PokemonType, pokemon_types
from repository.PokemonRepository import find_pokemon
from use_case.PokemonPickerUseCase import PokemonPickerUseCase
from use_case.TeamUseCase import TeamUseCase


def do_round_one(
        pokemon: List[Pokemon],
        opponent_pokemon: List[Pokemon]
) -> None:
    print_pokemon_ranks(
        pokemon,
        opponent_pokemon
    )


def print_pokemon_ranks(
        team_pokemon: List[Pokemon],
        opponent_pokemon: List[Pokemon]
) -> None:
    team_pokemon_ranks = rank_team_against_opponents(
        team_pokemon,
        opponent_pokemon
    )
    pp("Team pokemon ranks", sort_dicts=False)
    pp(team_pokemon_ranks)


def rank_team_against_opponents(
        team_pokemon: List[Pokemon],
        opponent_pokemon: List[Pokemon]
) -> Dict[str, Dict[Pokemon, int]]:
    pokemon_ranks = rank_team_pokemon_against_opponents(
        team_pokemon,
        opponent_pokemon
    )
    return pokemon_ranks


def rank_team_pokemon_against_opponents(
        team_pokemon,
        opponent_pokemon
):
    opponent_to_pokemon_attack_rank = rank_attack_of_attackers_against_defenders(
        team_pokemon,
        opponent_pokemon
    )

    opponent_to_pokemon_defense_rank = rank_defense_of_defenders_against_attackers(
        team_pokemon,
        opponent_pokemon,
    )

    pokemon_ranks = rank_based_on_attack_and_defense_rank(
        opponent_to_pokemon_attack_rank,
        opponent_to_pokemon_defense_rank
    )
    return pokemon_ranks


def rank_attack_of_attackers_against_defenders(
        attackers: List[Pokemon],
        defenders: List[Pokemon]
) -> DefaultDict[Pokemon, DefaultDict[int, List[Pokemon]]]:
    """
    Ranks pokemon by how much attackers can do to the defenders.
    :param attackers: The attacking pokemon.
    :param defenders: The defending pokemon.
    :return:
    A dictionary of defending pokemon
    to a rank to list of attacking pokemon dictionary.
    The lower the rank, the more damage the attacker can do to the defender.
    """
    defender_to_attacker_to_max_damage = get_max_damage_attackers_can_do_to_defenders(
        attackers,
        defenders
    )
    pokemon_ranks = rank_by_max_damage(defender_to_attacker_to_max_damage)
    return pokemon_ranks


def rank_defense_of_defenders_against_attackers(
        defenders: List[Pokemon],
        attackers: List[Pokemon]
) -> DefaultDict[Pokemon, DefaultDict[int, List[Pokemon]]]:
    defender_to_attacker_to_max_damage = get_max_damage_attackers_can_do_to_defenders(
        attackers,
        defenders
    )

    # Map from opponent to pokemon to max damage
    attacker_to_defender_to_max_damage = defaultdict(lambda: defaultdict(lambda: 0.0))
    for attacker in attackers:
        for pokemon in defender_to_attacker_to_max_damage.keys():
            attacker_to_defender_to_max_damage[attacker][pokemon] = \
                defender_to_attacker_to_max_damage[pokemon][attacker]

    pokemon_ranks = rank_by_max_damage(
        attacker_to_defender_to_max_damage,
        descending=False
    )
    return pokemon_ranks


def get_max_damage_attackers_can_do_to_defenders(
        attacking_pokemon: List[Pokemon],
        defending_pokemon: List[Pokemon]
) -> defaultdict[Pokemon, defaultdict[Pokemon, float]]:
    defender_to_attacker_to_max_damage = defaultdict(
        lambda: defaultdict(lambda: 0.0)
    )
    for defender in defending_pokemon:
        attacker_to_max_damage = defaultdict(lambda: 0.0)
        for attacker in attacking_pokemon:
            attacker_to_max_damage[attacker] = max_damage_attacker_can_do_to_defender(
                attacker,
                defender
            )
        defender_to_attacker_to_max_damage[defender] = attacker_to_max_damage
    return defender_to_attacker_to_max_damage


def rank_by_max_damage(
        pokemon_to_pokemon_to_max_damage: defaultdict[Pokemon, defaultdict[Pokemon, float]],
        descending=True
) -> DefaultDict[Pokemon, DefaultDict[int, List[Pokemon]]]:
    pokemon_ranks = defaultdict(lambda: defaultdict(lambda: []))
    pokemon_to_pokemon_rank = {}
    for pokemon in pokemon_to_pokemon_to_max_damage.keys():
        # Sort by max damage
        pokemon_to_pokemon_rank[pokemon] = sorted(
            (poke for poke in pokemon_to_pokemon_to_max_damage[pokemon].keys()),
            key=lambda poke: pokemon_to_pokemon_to_max_damage[pokemon][poke],
            reverse=descending
        )

        # Rank by max damage
        rank = 0
        last_damage = pokemon_to_pokemon_to_max_damage[pokemon][
            next(iter(pokemon_to_pokemon_rank[pokemon]))
        ]
        for poke in pokemon_to_pokemon_rank[pokemon]:
            damage = pokemon_to_pokemon_to_max_damage[pokemon][poke]
            if damage != last_damage:
                rank = rank + 1
            pokemon_ranks[pokemon][rank].append(poke)
            last_damage = damage
    return pokemon_ranks


def rank_based_on_attack_and_defense_rank(
        opponent_to_pokemon_attack_rank: DefaultDict[Pokemon, DefaultDict[int, List[Pokemon]]],
        opponent_to_pokemon_defense_rank: DefaultDict[Pokemon, DefaultDict[int, List[Pokemon]]]
) -> dict[str, dict[Pokemon, int]]:
    """
    Ranks pokemon by the combining the attack and defense ranks.
    The rank number of each pokemon is added for both ranks.
    The pokemon with the lower rank is better.
    :param opponent_to_pokemon_attack_rank:
    :param opponent_to_pokemon_defense_rank:
    :return:
    """
    pokemon_ranks = defaultdict(lambda: defaultdict(lambda: 0))
    for opponent in opponent_to_pokemon_defense_rank.keys():
        for i, poke_list in opponent_to_pokemon_attack_rank[opponent].items():
            for poke in poke_list:
                pokemon_ranks[opponent][poke] += i

        for i, poke_list in opponent_to_pokemon_defense_rank[opponent].items():
            for poke in poke_list:
                pokemon_ranks[opponent][poke] += i

    opponent_to_pokemon_ranks = {}
    for opponent in pokemon_ranks.keys():
        opponent_to_pokemon_ranks[opponent] = {
            pokemon: i
            for pokemon, i in sorted(
                (poke for poke in pokemon_ranks[opponent].items()),
                key=lambda item: item[1],
            )
        }
    return opponent_to_pokemon_ranks


def do_round_two(
        team_pokemon: List[Pokemon],
        choice_pokemon: List[Pokemon],
        opponent_pokemon: List[Pokemon]
):
    print_pokemon_ranks(team_pokemon, opponent_pokemon)
    chosen_pokemon = ask_user_to_pick_pokemon(2, team_pokemon)

    # Rank the types by which need to be covered
    weaknesses = get_weaknesses(chosen_pokemon)
    resistances = get_resistances(chosen_pokemon)
    remaining_pokemon = list(
        set(team_pokemon)
        .difference(set(chosen_pokemon))
        .union(choice_pokemon)
    )
    rank_from_weaknesses_and_resistances(remaining_pokemon, weaknesses, resistances)


def ask_user_to_pick_pokemon(
        num_pokemon: int,
        team_pokemon: List[Pokemon]
):
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


def get_weaknesses(
        pokemon: List[Pokemon]
) -> dict[PokemonType, float]:
    defense_multipliers = get_defense_multipliers_for_list(pokemon)

    all_defense_multipliers = defaultdict(lambda: [])
    for poke in pokemon:
        assert (poke.name in defense_multipliers.keys())
        for poke_type in defense_multipliers[poke.name]:
            all_defense_multipliers[poke_type].append(
                defense_multipliers[poke.name][poke_type]
            )

    average_defense_multipliers = {
        poke_type: sum(multipliers) / len(multipliers)
        for poke_type, multipliers in all_defense_multipliers.items()
    }

    weaknesses_of_team = {
        poke_type: multiplier
        for poke_type, multiplier in sorted(
            average_defense_multipliers.items(),
            key=lambda item: item[1],
            reverse=True
        )
    }
    return weaknesses_of_team


def get_resistances(
        choice_pokemon: list[Pokemon]
) -> dict[PokemonType, float]:
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


def rank_pokemon_by_type_advantage(pokemon, type_ranks):
    # TODO
    pass


def rank_from_weaknesses_and_resistances(
        pokemon: List[Pokemon],
        weaknesses: dict[PokemonType, float],
        resistances: dict[PokemonType, float]
):
    # These are ranks that the team is bad against both offensively and defensively
    type_ranks = rank_types_by_weakness_and_resistance(weaknesses, resistances)

    rank_pokemon_by_type_advantage(pokemon, type_ranks)

def rank_types_by_weakness_and_resistance(
        weaknesses: dict[PokemonType, float],
        resistances: dict[PokemonType, float]
) -> DefaultDict[int, set[PokemonType]]:
    weakness_ranks = defaultdict(lambda: [])
    rank = 0
    last_weakness = next(iter(weaknesses.values()))
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

    # Average ranks
    type_ranks = defaultdict(lambda: 0.0)
    for rank, poke_types in weakness_ranks.items():
        for poke_type in poke_types:
            type_ranks[poke_type] += rank
    for rank, poke_types in resistance_ranks.items():
        for poke_type in poke_types:
            type_ranks[poke_type] += rank
            type_ranks[poke_type] = type_ranks[poke_type] / 2.0

    ordered_type_ranks = defaultdict(lambda: set())
    for poke_type, rank in sorted(
            type_ranks.items(),
            key=lambda item: item[1]
    ):
        ordered_type_ranks[rank].add(poke_type)

    return ordered_type_ranks


class Round1And2ViewModel:

    def __init__(
            self,
            team_use_case: TeamUseCase,
            is_round_2=False
    ) -> None:
        self.__is_round_2 = is_round_2
        self.__team_use_case__ = team_use_case
        self.__opponent_pokemon__ = []

    def set_opponent_pokemon_names(
            self,
            opponent_pokemon_names: List[str]
    ) -> None:
        self.__opponent_pokemon__ = find_pokemon(opponent_pokemon_names)

    def confirm_clicked(self) -> None:
        if not self.__is_round_2:
            pokemon = self.__team_use_case__.get_team_pokemon()
            for poke in self.__team_use_case__.get_choice_pokemon():
                pokemon.append(poke)

            do_round_one(
                pokemon,
                self.__opponent_pokemon__
            )
        else:
            do_round_two(
                self.__team_use_case__.get_team_pokemon(),
                self.__team_use_case__.get_choice_pokemon(),
                self.__opponent_pokemon__
            )
