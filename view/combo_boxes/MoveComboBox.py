from PyQt5.QtWidgets import QComboBox

from repository.MoveRepository import moves


class MoveComboBox(QComboBox):
    """
    A QComboBox containing all data_class moves
    """
    def __init__(self):
        super().__init__()
        # No move has this string of letters
        last_move = "ZZZ"
        self.addItem("")
        for move in sorted(moves):
            if last_move not in move:
                self.addItem(move)
            else:
                move = last_move
            last_move = move
