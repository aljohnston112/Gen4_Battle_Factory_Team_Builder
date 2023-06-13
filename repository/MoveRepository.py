from typing import Dict

from data_class.Move import Move
from data_source.MoveDataSource import get_moves

get_all_moves: Dict[str, Move] = get_moves()
