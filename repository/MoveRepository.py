from typing import Dict

from data_class.Move import DetailedMove
from data_source.MoveDataSource import get_moves

moves: Dict[str, DetailedMove] = get_moves()
