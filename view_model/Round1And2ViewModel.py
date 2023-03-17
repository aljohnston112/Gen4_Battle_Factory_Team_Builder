from collections import defaultdict
from pprint import pprint
from typing import List, Dict, DefaultDict

from data_class.Pokemon import Pokemon
from repository.PokemonRepository import find_pokemon
from use_case.TeamUseCase import TeamUseCase


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
            attacker_to_max_damage[attacker] = attacker.max_damage_to_defender(
                defender
            )
        defender_to_attacker_to_max_damage[defender] = attacker_to_max_damage
    return defender_to_attacker_to_max_damage


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
            self.do_round_one()
        else:
            self.do_round_two()

    def do_round_one(self) -> None:
        team_pokemon = self.__team_use_case__.get_team_pokemon()
        choice_pokemon = self.__team_use_case__.get_choice_pokemon()

        self.print_pokemon_ranks(team_pokemon)
        # Print choice ranks if not the first battle
        if len(choice_pokemon) != 0:
            self.print_pokemon_ranks(choice_pokemon)

    def print_pokemon_ranks(
            self,
            pokemon: List[Pokemon]
    ) -> None:
        team_pokemon_ranks = self.rank_team_against_opponents(pokemon)
        pprint("Team pokemon ranks")
        pprint(team_pokemon_ranks)

    def rank_team_against_opponents(
            self,
            team_pokemon: List[Pokemon],
    ) -> Dict:
        pokemon_ranks = rank_team_pokemon_against_opponents(
            team_pokemon,
            self.__opponent_pokemon__
        )
        return pokemon_ranks

    def do_round_two(self):
        team_pokemon = self.__team_use_case__.get_team_pokemon(),
        choice_pokemon = self.__team_use_case__.get_choice_pokemon(),

        self.print_pokemon_ranks(team_pokemon)
        chosen_pokemon = ask_user_to_pick_pokemon(2, team_pokemon)

        # Rank the types by which need to be covered
        weaknesses = get_weaknesses(chosen_pokemon)
        resistances = get_resistances(chosen_pokemon)
        remaining_pokemon = set(team_pokemon) \
            .difference(set(chosen_pokemon)) \
            .union(choice_pokemon)
        rank_from_weaknesses_and_resistances(remaining_pokemon, weaknesses, resistances)
