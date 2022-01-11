from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QStackedWidget

from build_team.Strings import string_team
from build_team.gui.ComboBoxes import PokemonComboBox, PokemonMoveComboBox


class TeamMove(QVBoxLayout):

    def __init__(self):
        super().__init__()

        self.stacked_rounds = QStackedWidget()
        self.addWidget(self.stacked_rounds)

        self.pokemon = PokemonComboBox()
        self.pokemon.currentTextChanged.connect(self.pokemon_picked)
        self.pokemon_move = PokemonMoveComboBox()
        self.pokemon_move.pokemon_combo_box.currentTextChanged.connect(self.pokemon_changed)

        self.stacked_rounds.addWidget(self.pokemon)
        self.stacked_rounds.addWidget(self.pokemon_move)

    def pokemon_picked(self, pokemon_in):
        self.pokemon_move.pokemon_combo_box.setCurrentIndex(
            self.pokemon_move.pokemon_combo_box.findText(pokemon_in)
        )

    def pokemon_changed(self, s):
        if self.stacked_rounds.currentWidget() != self.pokemon_move:
            self.stacked_rounds.setCurrentWidget(self.pokemon_move)


class Team(QHBoxLayout):

    def __init__(self):
        super().__init__()
        label_names = QLabel(string_team)
        self.addWidget(label_names)
        self.pokemon1 = TeamMove()
        self.pokemon2 = TeamMove()
        self.pokemon3 = TeamMove()
        self.pokemon4 = TeamMove()
        self.pokemon5 = TeamMove()
        self.pokemon6 = TeamMove()
        self.addLayout(self.pokemon1)
        self.addLayout(self.pokemon2)
        self.addLayout(self.pokemon3)
        self.addLayout(self.pokemon4)
        self.addLayout(self.pokemon5)
        self.addLayout(self.pokemon6)

    def get_pokemon(self):
        return [
            (
                self.pokemon1.pokemon_move.pokemon_combo_box.currentText(),
                self.pokemon1.pokemon_move.move_combo_box.currentText()),
            (
                self.pokemon2.pokemon_move.pokemon_combo_box.currentText(),
                self.pokemon2.pokemon_move.move_combo_box.currentText()
            ),
            (
                self.pokemon3.pokemon_move.pokemon_combo_box.currentText(),
                self.pokemon3.pokemon_move.move_combo_box.currentText()
            ),
            (
                self.pokemon4.pokemon_move.pokemon_combo_box.currentText(),
                self.pokemon4.pokemon_move.move_combo_box.currentText()),
            (
                self.pokemon5.pokemon_move.pokemon_combo_box.currentText(),
                self.pokemon5.pokemon_move.move_combo_box.currentText()
            ),
            (
                self.pokemon6.pokemon_move.pokemon_combo_box.currentText(),
                self.pokemon6.pokemon_move.move_combo_box.currentText()
            ),
        ]
