from PyQt5.QtWidgets import QComboBox

from repository.MoveRepository import get_all_moves


class MoveComboBox(QComboBox):
    """
    A QComboBox containing all data_class moves
    """
    def __init__(self):
        super().__init__()
        self.addItem("")
        for move in sorted(get_all_moves):
            self.addItem(move)
