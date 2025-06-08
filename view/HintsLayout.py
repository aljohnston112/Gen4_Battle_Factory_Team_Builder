from PyQt5.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QRadioButton, QStackedWidget, QWidget

from data.Strings import string_round_4, string_round_5_up, string_round_3, string_round_1, \
    string_round_2
from use_case.RoundUseCase import Round, RoundUseCase
from use_case.TeamUseCase import TeamUseCase
from view.Round1And2Layout import Round1And2Layout
from view.Round3Layout import Round3Layout
from view.Round4Layout import Round4Layout
from view.Round5Layout import Round5Layout
from view.TeamLayout import TeamLayout


class HintsLayout(QGridLayout):
    """
    The layout for the hints UI.
    """

    def __set_up_radio_buttons__(self):
        """
        Sets up the radio buttons used to pick the round number.
        """
        group_box_rb: QGroupBox = QGroupBox()

        self.radio_buttons_rounds: list[QRadioButton] = [
            QRadioButton(string_round_1),
            QRadioButton(string_round_2),
            QRadioButton(string_round_3),
            QRadioButton(string_round_4),
            QRadioButton(string_round_5_up),
        ]

        h_box_layout_rounds: QHBoxLayout = QHBoxLayout()
        for radio_button in self.radio_buttons_rounds:
            radio_button: QRadioButton
            h_box_layout_rounds.addWidget(radio_button)
            radio_button.toggled.connect(self.__round_checked__)
        group_box_rb.setLayout(h_box_layout_rounds)
        # row, column, row_span, row_column
        self.addWidget(group_box_rb, 1, 0, 1, 4)
        self.radio_buttons_rounds[0].click()

    def __set_up_stacked_rounds__(self):
        """
        Adds all round widgets to the layout.
        They are stacked so only one appears at a time.
        """
        self.stacked_rounds: QStackedWidget = QStackedWidget()
        self.round_widgets: list[QWidget] = [
            Round1And2Layout(self.__team_use_case__),
            Round1And2Layout(self.__team_use_case__, is_round_2=True),
            Round3Layout(self.__team_use_case__),
            Round4Layout(self.__team_use_case__),
            Round5Layout(self.__team_use_case__)
        ]
        for round_widget in self.round_widgets:
            round_widget: QWidget
            self.stacked_rounds.addWidget(round_widget)
        # row, column, row_span, row_column
        self.addWidget(self.stacked_rounds, 2, 0, 2, 1)

    def __round_changed__(self, new_round: int) -> None:
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

    def __init__(self):
        """
        Creates the hints UI.
        The three Pokémon the user has, and the three they have to choose from are input to the Team UI.
        The user has 4 choices to choose from in regard to which round they are on.
        The appropriate UI will appear depending on which choice is selected,
        and then the user inputs the hints they are given by the battle factory before a match.
        """
        super().__init__()

        self.__current_round_use_case__: RoundUseCase = RoundUseCase()
        self.__team_use_case__: TeamUseCase = TeamUseCase(
            team_pokemon=[],
            choice_pokemon=[]
        )
        self.team = TeamLayout(self.__team_use_case__)
        # row, column
        self.addLayout(self.team, 0, 0)

        self.round_widgets = None
        self.stacked_rounds = None
        self.__set_up_stacked_rounds__()

        self.radio_buttons_rounds = None
        self.__set_up_radio_buttons__()
