from collections import defaultdict

from PyQt5.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QRadioButton, QStackedWidget

from build_team.Algorithms import get_defense_multipliers
from build_team.Data import pokemon, moves
from build_team.gui.RoundLayouts import Round1And2, Round3, Round4, Round5
from build_team.Strings import string_round_1_2, string_round_4, string_round_5_up, string_round_3
from build_team.gui.Team import Team
from parser.parse_moves import get_moves


class Hints(QGridLayout):

    def __init__(self):
        super().__init__()
        self.team = Team()
        self.addLayout(self.team, 0, 0)

        self.rb_round_5 = None
        self.rb_round_4 = None
        self.rb_round_3 = None
        self.rb_round_1_2 = None

        self.round_5 = None
        self.round_4 = None
        self.round_3 = None
        self.round_1_2 = None
        self.current_round = None
        self.stacked_rounds = None

        self.set_up_stacked_rounds()
        self.set_up_radio_buttons()

    def set_up_stacked_rounds(self):
        self.round_1_2 = Round1And2()
        self.round_3 = Round3()
        self.round_4 = Round4()
        self.round_5 = Round5()
        round_widgets = [self.round_1_2, self.round_3, self.round_4, self.round_5]

        self.stacked_rounds = QStackedWidget()
        self.addWidget(self.stacked_rounds, 2, 0, 2, 1)

        for w in round_widgets:
            self.stacked_rounds.addWidget(w)
        self.current_round = self.round_1_2
        self.stacked_rounds.setCurrentWidget(self.round_1_2)

    def set_up_radio_buttons(self):
        self.rb_round_1_2 = QRadioButton(string_round_1_2)
        self.rb_round_3 = QRadioButton(string_round_3)
        self.rb_round_4 = QRadioButton(string_round_4)
        self.rb_round_5 = QRadioButton(string_round_5_up)
        radio_buttons_rounds = [self.rb_round_1_2, self.rb_round_3, self.rb_round_4, self.rb_round_5]

        group_box_rb = QGroupBox()
        self.addWidget(group_box_rb, 1, 0, 1, 4)

        h_box_layout_rounds = QHBoxLayout()
        for r in radio_buttons_rounds:
            h_box_layout_rounds.addWidget(r)
            r.toggled.connect(self.round_changed)
        group_box_rb.setLayout(h_box_layout_rounds)
        self.rb_round_1_2.click()

    def round_changed(self, checked):
        if not checked:
            return
        if self.rb_round_1_2.isChecked():
            self.round_checked(self.round_1_2)
        if self.rb_round_3.isChecked():
            self.round_checked(self.round_3)
        if self.rb_round_4.isChecked():
            self.round_checked(self.round_4)
        if self.rb_round_5.isChecked():
            self.round_checked(self.round_5)

    def round_checked(self, round_):
        self.stacked_rounds.setCurrentWidget(round_)
        self.current_round = round_

    def confirm_clicked(self):
        if self.current_round is self.round_1_2:
            opponent_pokemon = self.round_1_2.get_pokemon()
            opponent_dms = get_defense_multipliers([p for p in opponent_pokemon])
            player_pokemon = self.team.get_pokemon()
            player_dms = get_defense_multipliers([p[0] for p in player_pokemon])

            ops = []
            for op in opponent_pokemon:
                for p in sorted(pokemon):
                    if op != "" and op in p:
                        ops.append(pokemon[p])

            player_defense_ranks = defaultdict(lambda: defaultdict(lambda: -1.0))
            all_moves = moves
            for op in ops:
                for m in op.moves:
                    dm = all_moves[m.name]
                    if dm.power != 0:
                        for pp in player_pokemon:
                            if pp[0] != "":
                                if player_defense_ranks[pp[0]][dm.type_] == -1:
                                    player_defense_ranks[pp[0]][dm.type_] = dm.power * player_dms[pp[0]][dm.type_]
                                else:
                                    player_defense_ranks[pp[0]][dm.type_] \
                                        = (
                                                  player_defense_ranks[pp[0]][dm.type_]
                                           + dm.power * player_dms[pp[0]][dm.type_]
                                          ) / 2.0

            pps = []
            for pp in player_pokemon:
                for p in sorted(pokemon):
                    if pp[0] != "" and pp[0] in p:
                        ms = [m.name for m in pokemon[p].moves]
                        if pp[1] == "" or pp[1] in ms:
                            pok = pokemon[p]
                            pok.name = pp[0]
                            pps.append(pok)

            player_to_opponent_defense = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: -1.0)))
            for pp in pps:
                opponent_defense_ranks = defaultdict(lambda: defaultdict(lambda: -1.0))
                for m in pp.moves:
                    dm = all_moves[m.name]
                    if dm.power != 0:
                        for op in opponent_pokemon:
                            if op != "":
                                if opponent_defense_ranks[op][dm.type_] == -1:
                                    opponent_defense_ranks[op][dm.type_] = dm.power * opponent_dms[op][dm.type_]
                                else:
                                    opponent_defense_ranks[op][dm.type_] \
                                        = (
                                                  opponent_defense_ranks[op][dm.type_]
                                           + dm.power * opponent_dms[op][dm.type_]
                                          ) / 2.0
                player_to_opponent_defense[pp.name] = opponent_defense_ranks

            defense_scores = defaultdict(lambda: 0)
            offense_scores = defaultdict(lambda: 0)
            for pp in pps:
                defense_scores[pp.name] += sum(player_defense_ranks[pp.name].values())
                for op in player_to_opponent_defense[pp.name].values():
                    offense_scores[pp.name] += sum(op.values())

            pokemon_ranks = defaultdict(lambda: 0)
            print(sorted(defense_scores.items(), key=lambda k: k[1]))
            print(sorted(offense_scores.items(), key=lambda k: k[1], reverse=True))
            for i, p in enumerate(sorted(defense_scores.items(), key=lambda k: k[1])):
                pokemon_ranks[p[0]] += i
            for i, p in enumerate(sorted(offense_scores.items(), key=lambda k: k[1], reverse=True)):
                pokemon_ranks[p[0]] += i

            print(sorted(pokemon_ranks.items(), key=lambda k: k[1]))
                                     