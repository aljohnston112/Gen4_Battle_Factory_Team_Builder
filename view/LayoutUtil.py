from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QGridLayout


def add_expanding_spacer(
        grid_layout: QGridLayout,
        row: int,
        column: int
) -> None:
    grid_layout.addItem(
        QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum),
        row,
        column
    )