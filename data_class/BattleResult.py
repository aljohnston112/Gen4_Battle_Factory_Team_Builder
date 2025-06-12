from attr import dataclass

from data_class.Hits import Hits


@dataclass
class BattleResult:
    winner_id: str
    win_rate: float
    win_results: dict[str, Hits]
    lose_results: dict[str, Hits]