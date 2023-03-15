from PyQt5.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QRadioButton, QStackedWidget

from data.Strings import string_round_4, string_round_5_up, string_round_3, string_round_1, \
    string_round_2
from use_case.CurrentRoundUseCase import Round
from view.Round1And2Layout import Round1And2Layout
from view.Round3Layout import Round3Layout
from view.Round4Layout import Round4Layout
from view.Round5Layout import Round5Layout
from view.TeamLayout import TeamLayout


class HintsLayout(QGridLayout):
    """
    The layout for the hints UI.
    """

    def __init__(
            self,
            current_round_use_case,
            round_1_and_2_use_case,
            team_use_case
    ):
        """
        Creates the hints UI.
        The three Pokemon the user has, and the three they have to choose from
        are input to the Team UI.
        The user has 4 choices to choose from in regard to which round they are on.
        The appropriate UI will appear depending on which choice is selected,
        and then the user inputs the hints they are given by the battle factory before a match.
        """
        super().__init__()

        self.__current_round_use_case__ = current_round_use_case
        self.__round_1_and_2_use_case__ = round_1_and_2_use_case
        self.team = TeamLayout(team_use_case)
        self.addLayout(self.team, 0, 0)

        self.round_widgets = None
        self.stacked_rounds = None
        self.radio_buttons_rounds = None

        self.__set_up_stacked_rounds__()
        self.__set_up_radio_buttons__()

    def __set_up_radio_buttons__(self):
        """
        Sets up the radio buttons used to pick the round number.
        """
        group_box_rb = QGroupBox()

        self.radio_buttons_rounds = [
            QRadioButton(string_round_1),
            QRadioButton(string_round_2),
            QRadioButton(string_round_3),
            QRadioButton(string_round_4),
            QRadioButton(string_round_5_up),
        ]

        h_box_layout_rounds = QHBoxLayout()
        for radio_button in self.radio_buttons_rounds:
            h_box_layout_rounds.addWidget(radio_button)
            radio_button.toggled.connect(self.__round_checked__)
        group_box_rb.setLayout(h_box_layout_rounds)
        self.addWidget(group_box_rb, 1, 0, 1, 4)
        self.radio_buttons_rounds[0].click()

    def __round_checked__(self, checked):
        """
        Changes the round based on which radio button the used has checked.
        :param checked: Whether the radio button is checked.
        """
        if not checked:
            return
        if self.radio_buttons_rounds[0].isChecked():
            self.__round_changed__(0)
        elif self.radio_buttons_rounds[1].isChecked():
            self.__round_changed__(1)
        elif self.radio_buttons_rounds[2].isChecked():
            self.__round_changed__(2)
        elif self.radio_buttons_rounds[3].isChecked():
            self.__round_changed__(3)
        elif self.radio_buttons_rounds[4].isChecked():
            self.__round_changed__(4)

    def __round_changed__(self, new_round):
        """
        Sets the round layout based on which round the user selected
        :param new_round: The index of the radio button that the user selected.
        """
        self.stacked_rounds.setCurrentWidget(self.round_widgets[new_round])
        match new_round:
            case 0:
                self.__current_round_use_case__.set_current_round(Round.ONE)
            case 1:
                self.__current_round_use_case__.set_current_round(Round.TWO)
            case 2:
                self.__current_round_use_case__.set_current_round(Round.THREE)
            case 3:
                self.__current_round_use_case__.set_current_round(Round.FOUR)
            case 4:
                self.__current_round_use_case__.set_current_round(Round.FIVE)

    def __set_up_stacked_rounds__(self):
        """
        Adds all round widgets to the layout.
        They are stacked so only one appears at a time.
        """
        self.stacked_rounds = QStackedWidget()
        self.round_widgets = [
            Round1And2Layout(self.__round_1_and_2_use_case__),
            Round1And2Layout(self.__round_1_and_2_use_case__, is_round_2=True),
            Round3Layout(),
            Round4Layout(),
            Round5Layout()
        ]
        for round_widget in self.round_widgets:
            self.stacked_rounds.addWidget(round_widget)

        self.addWidget(self.stacked_rounds, 2, 0, 2, 1)
