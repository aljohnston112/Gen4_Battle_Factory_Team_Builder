import sys

from PyQt5.QtWidgets import QGridLayout, QGroupBox, QRadioButton, \
    QStackedWidget, QWidget, QHBoxLayout

from data.Strings import string_round_1, string_round_2, string_round_3, \
    string_round_4, string_round_5, string_round_6, string_round_7, \
    string_round_8_plus
from use_case.RoundUseCase import RoundUseCase, Round
from use_case.TeamUseCase import TeamUseCase
from view.TextOutputWidget import TextOutputWidget
from view.Round1And2Layout import Round1And2Layout
from view.Round3Layout import Round3Layout
from view.Round4Layout import Round4Layout
from view.Round5Layout import Round5Layout
from view.TeamLayout import TeamLayout


class HintsLayout(QGridLayout):
    """
    A layout that lets the user provide hints for the team analyzer.
    """

    def __round_changed__(self, new_round: Round) -> None:
        """
        Sets the round layout based on which round the user selected
        :param new_round: The Round of the radio button that the user selected.
        """
        i: int = new_round.value
        if i >= len(self.hint_widgets):
            i = len(self.hint_widgets) - 1
        self.stacked_round_layouts.setCurrentWidget(self.hint_widgets[i])
        self.__current_round_use_case__.set_current_round(new_round)

    def __set_up_stacked_rounds__(self, level: int) -> None:
        """
        Adds all hint widgets to the layout.
        They are stacked so only one appears at a time.
        """
        self.stacked_round_layouts: QStackedWidget = QStackedWidget()
        self.hint_widgets: list[QWidget] = [
            Round1And2Layout(
                team_use_case=self.__team_use_case__,
                level=level,
                is_round_2=False
            ),
            Round1And2Layout(
                team_use_case=self.__team_use_case__,
                level=level,
                is_round_2=True
            ),
            Round3Layout(self.__team_use_case__, level),
            Round4Layout(self.__team_use_case__, level),
            Round5Layout(
                self.__team_use_case__,
                self.__current_round_use_case__,
                level
            )
        ]
        for hint_widget in self.hint_widgets:
            hint_widget: QWidget
            self.stacked_round_layouts.addWidget(hint_widget)
        # row, column, row_span, row_column
        self.addWidget(self.stacked_round_layouts, 2, 0, 2, 1)

    def __round_checked__(self, checked) -> None:
        """
        Changes the round based on which radio button the user has checked.
        :param checked: Whether the radio button is checked.
        """
        if not checked:
            return
        for i in range(len(self.radio_buttons_rounds)):
            i: int
            radio_button: QRadioButton = self.radio_buttons_rounds[i]
            if radio_button.isChecked():
                self.__round_changed__(Round(i))
                break

    def __set_up_round_radio_buttons__(self) -> None:
        """
        Sets up the radio buttons used to pick the round number.
        """
        h_box_layout_rounds: QHBoxLayout = QHBoxLayout()
        h_box_layout_rounds.addStretch()
        self.radio_buttons_rounds: list[QRadioButton] = [
            QRadioButton(string) for string in
            [
                string_round_1,
                string_round_2,
                string_round_3,
                string_round_4,
                string_round_5,
                string_round_6,
                string_round_7,
                string_round_8_plus
             ]
        ]
        for radio_button in self.radio_buttons_rounds:
            radio_button: QRadioButton
            h_box_layout_rounds.addWidget(radio_button)
            radio_button.toggled.connect(self.__round_checked__)
            h_box_layout_rounds.addStretch()

        group_box_radio_buttons: QGroupBox = QGroupBox()
        group_box_radio_buttons.setLayout(h_box_layout_rounds)
        # row, column, row_span, row_column
        self.addWidget(group_box_radio_buttons, 1, 0, 1, 4)
        # Set the default round to 1
        self.radio_buttons_rounds[Round.ONE.value].click()

    def __init__(self, level: int) -> None:
        """
        Creates the hints UI.
        The three Pokémon the user has and
        the three they have to choose from are input to the Team UI.
        If it is the first battle, then all six will be choices.
        The appropriate UI will appear
        depending on which round and battle are selected,
        and the user can input the hints they are given
        by the battle factory before a match.
        """
        super().__init__()
        self.__current_round_use_case__: RoundUseCase = RoundUseCase()
        self.__team_use_case__: TeamUseCase = TeamUseCase(
            team_pokemon=[],
            choice_pokemon=[]
        )
        self.team_layout: TeamLayout = TeamLayout(self.__team_use_case__)
        # row, column
        self.addLayout(self.team_layout, 0, 0)

        self.hint_widgets: list[QWidget] | None = None
        self.stacked_round_layouts: list[QWidget] | None = None
        self.__set_up_stacked_rounds__(level=level)

        self.radio_buttons_rounds = None
        self.__set_up_round_radio_buttons__()

        # Output text box
        self.text_output_widget = TextOutputWidget()
        self.addWidget(self.text_output_widget, 4, 0, 1, 2)
