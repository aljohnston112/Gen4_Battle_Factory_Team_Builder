from data_class.Move import Move
from data_source.MoveDataSource import get_moves

all_moves: dict[str, Move] = get_moves()
