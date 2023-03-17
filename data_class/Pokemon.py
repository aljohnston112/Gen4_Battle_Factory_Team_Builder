from __future__ import annotations
import attr

from data_class.Move import Move
from data_class.Type import PokemonType
from repository.MoveRepository import get_all_moves
from repository.TypeChartRepository import get_defense_multipliers


@attr.define
class Pokemon:
    name: str
    types: list[PokemonType]
    ability: list[str]
    item: str
    moves: list[Move]

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    def max_damage_to_defender(
            self,
            defender: Pokemon
    ) -> float:
        opponent_defense_multipliers = get_defense_multipliers(defender)
        max_damage = 0
        for pokemon_move in self.moves:
            max_damage = max(
                opponent_defense_multipliers[pokemon_move.move_type] *
                get_all_moves[pokemon_move.name].power,
                max_damage
            )
        return max_damage
