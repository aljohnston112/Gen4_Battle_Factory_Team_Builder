from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, \
    QSizePolicy, QGridLayout, QSpacerItem

from data.Strings import string_name, string_move, string_confirm
from view.combo_boxes.MoveComboBox import MoveComboBox
from view.combo_boxes.PokemonComboBox import PokemonComboBox
from view_model.Round3ViewModel import Round3ViewModel


class Round3Layout(QWidget):
    """
    Allows the user to enter hints for round three of battle factory
    """
    def __init__(self, team_use_case):
        super().__init__()
        self.__view_model__ = Round3ViewModel(team_use_case)

        root_layout = QGridLayout()
        self.setLayout(root_layout)

        # One name
        root_layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            0
        )
        label_name = QLabel(string_name)
        root_layout.addWidget(label_name, 0, 1)
        pokemon_combo_box = PokemonComboBox()
        pokemon_combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pokemon_combo_box.currentTextChanged.connect(self.text_changed)
        root_layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            2
        )
        root_layout.addWidget(pokemon_combo_box, 0, 3)
        self.pokemonComboBox = pokemon_combo_box
        root_layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            4
        )

        # One move
        label_move = QLabel(string_move)
        root_layout.addWidget(label_move, 0, 5)
        root_layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            6
        )
        move = MoveComboBox()
        move.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        move.currentTextChanged.connect(self.text_changed)
        root_layout.addWidget(move, 0, 7)
        root_layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            8
        )
        self.moveComboBox = move

        button_confirm = QPushButton(string_confirm)
        root_layout.addWidget(button_confirm, 1, 1, 1, 7)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)

    def text_changed(self):
        self.__view_model__.set_pokemon_name_and_move(self.get_pokemon(), self.get_move())

    def get_pokemon(self):
        return self.pokemonComboBox.currentText()

    def get_move(self):
        return self.moveComboBox.currentText()
