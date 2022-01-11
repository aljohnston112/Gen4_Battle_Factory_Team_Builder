from PyQt5.QtWidgets import QComboBox, QWidget, QVBoxLayout, QSizePolicy

from build_team.Data import pokemon, moves, types


class PokemonComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        tp = "ZZZ"
        self.addItem("")
        for p in sorted(pokemon):
            if tp not in p:
                self.addItem(p)
            else:
                p = tp
            tp = p


class PokemonMoveComboBox(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.pokemon_combo_box = PokemonComboBox()
        self.pokemon_combo_box.currentTextChanged.connect(self.set_pokemon)
        self.move_combo_box = QComboBox()
        self.move_combo_box.setVisible(False)

        layout.addWidget(self.pokemon_combo_box)
        layout.addWidget(self.move_combo_box)

    def set_pokemon(self, pokemon_in):
        self.move_combo_box.clear()
        ps = []
        for p in sorted(pokemon):
            if pokemon_in in p:
                ps.append(pokemon[p])
        ms = set()
        if len(ps) > 1:
            for p in ps:
                move_list = p.moves
                ms = ms.symmetric_difference(move_list)
            for move in ms:
                self.move_combo_box.addItem(move.name)
            self.move_combo_box.setVisible(True)
        else:
            self.move_combo_box.setVisible(False)


class MoveComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        tm = "ZZZ"
        self.addItem("")
        for m in sorted(moves):
            if tm not in m:
                self.addItem(m)
            else:
                m = tm
            tm = m


class TypeComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        tp = "ZZZ"
        self.addItem("")
        for p in sorted(types):
            if tp not in p:
                self.addItem(p)
            else:
                p = tp
            tp = p
