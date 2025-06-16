from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy, \
    QGridLayout

from data.Strings import string_name, string_move, string_confirm
from use_case.PrintUseCase import PrintUseCase
from use_case.RoundUseCase import RoundUseCase
from use_case.TeamUseCase import TeamUseCase
from view.LayoutUtil import add_expanding_spacer
from view.combo_boxes.MoveComboBox import MoveComboBox
from view.combo_boxes.PokemonComboBox import PokemonComboBox
from view_model.Round3ViewModel import Round3ViewModel


class Round3Layout(QWidget):
    """
    Allows the user to enter hints for round three of battle factory
    """

    def get_move(self) -> str:
        return self.__move_combo_box__.currentText()

    def get_pokemon(self) -> str:
        return self.__pokemon_combo_box__.currentText()

    def text_changed(self) -> None:
        self.__view_model__.set_pokemon_name_and_move(
            name=self.get_pokemon(),
            move=self.get_move()
        )

    def __init__(
            self,
            team_use_case: TeamUseCase,
            round_use_case: RoundUseCase,
            print_use_case: PrintUseCase,
            level: int
    ) -> None:
        super().__init__()
        self.__view_model__: Round3ViewModel = Round3ViewModel(
            team_use_case=team_use_case,
            round_use_case=round_use_case,
            print_use_case=print_use_case,
            level=level
        )

        root_layout: QGridLayout = QGridLayout()
        self.setLayout(root_layout)

        # One name
        add_expanding_spacer(grid_layout=root_layout, row=0, column=0)
        label_name = QLabel(string_name)
        # row, column
        root_layout.addWidget(label_name, 0, 1)
        add_expanding_spacer(grid_layout=root_layout, row=0, column=2)

        pokemon_combo_box: PokemonComboBox = PokemonComboBox(
            round_use_case=round_use_case,
            is_player=False
        )
        pokemon_combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pokemon_combo_box.currentTextChanged.connect(self.text_changed)
        root_layout.addWidget(pokemon_combo_box, 0, 3)
        self.__pokemon_combo_box__: PokemonComboBox = pokemon_combo_box
        add_expanding_spacer(grid_layout=root_layout, row=0, column=4)

        # One move
        label_move: QLabel = QLabel(string_move)
        # row_ column
        root_layout.addWidget(label_move, 0, 5)
        add_expanding_spacer(grid_layout=root_layout, row=0, column=6)

        move_combo_box: MoveComboBox = MoveComboBox()
        self.__move_combo_box__: MoveComboBox = move_combo_box
        move_combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        move_combo_box.currentTextChanged.connect(self.text_changed)
        root_layout.addWidget(move_combo_box, 0, 7)
        add_expanding_spacer(grid_layout=root_layout, row=0, column=8)

        button_confirm: QPushButton = QPushButton(string_confirm)
        # row, column, row_span, column_span
        root_layout.addWidget(button_confirm, 1, 1, 1, 7)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)
