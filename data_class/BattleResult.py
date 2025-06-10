from attr import dataclass

from data_class.Hits import Hits


@dataclass
class BattleResult:
    winner_id: str
    win_rate: float
    results: dict[str, Hits]