from PyQt5.QtWidgets import QGridLayout, QGroupBox, QRadioButton, \
    QStackedWidget, QWidget, QHBoxLayout

from data.Strings import string_round_1, string_round_2, string_round_3, \
    string_round_4, string_round_5, string_round_6, string_round_7, \
    string_round_8_plus
from use_case.PrintUseCase import PrintUseCase
from use_case.RoundUseCase import RoundUseCase, Round
from use_case.TeamUseCase import TeamUseCase
from view.DualTextOutputWidget import DualTextOutputWidget
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
        Sets the round layout based on which round the user selected.
        :param new_round: The Round of the radio button that the user selected.
        """
        i: int = new_round.value
        if i >= len(self.__hint_widgets__):
            i = len(self.__hint_widgets__) - 1
        self.__stacked_round_layouts__.setCurrentWidget(
            self.__hint_widgets__[i]
        )
        self.__current_round_use_case__.set_current_round(new_round)

    def __round_checked__(self, checked: bool) -> None:
        """
        Changes the round based on which radio button the user has checked.
        :param checked: Whether the radio button is checked.
        """
        if not checked:
            return
        for i in range(len(self.__radio_buttons_rounds__)):
            i: int
            if self.__radio_buttons_rounds__[i].isChecked():
                self.__round_changed__(Round(i))
                break

    def __set_up_round_radio_buttons__(self) -> None:
        """
        Sets up the radio buttons used to pick the round number.
        """
        h_box_layout_rounds: QHBoxLayout = QHBoxLayout()
        h_box_layout_rounds.addStretch()
        self.__radio_buttons_rounds__: list[QRadioButton] = [
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
        for radio_button in self.__radio_buttons_rounds__:
            radio_button: QRadioButton
            h_box_layout_rounds.addWidget(radio_button)
            radio_button.toggled.connect(self.__round_checked__)
            h_box_layout_rounds.addStretch()

        group_box_radio_buttons: QGroupBox = QGroupBox()
        group_box_radio_buttons.setLayout(h_box_layout_rounds)
        # row, column, row_span, column_span
        self.addWidget(group_box_radio_buttons, 1, 0, 1, 4)
        # Set the default round to 1
        self.__radio_buttons_rounds__[Round.ONE.value].click()

    def __set_up_stacked_rounds__(self, level: int) -> None:
        """
        Adds all hint widgets to the layout.
        They are stacked so only one appears at a time.
        """
        self.__stacked_round_layouts__: QStackedWidget = QStackedWidget()
        self.__hint_widgets__: list[QWidget] = [
            Round1And2Layout(
                team_use_case=self.__team_use_case__,
                print_use_case=self.__print_use_case__,
                level=level,
                is_round_2=False
            ),
            Round1And2Layout(
                team_use_case=self.__team_use_case__,
                print_use_case=self.__print_use_case__,
                level=level,
                is_round_2=True
            ),
            Round3Layout(
                team_use_case=self.__team_use_case__,
                print_use_case=self.__print_use_case__,
                level=level
            ),
            Round4Layout(
                team_use_case=self.__team_use_case__,
                print_use_case=self.__print_use_case__,
                level=level
            ),
            Round5Layout(
                team_use_case=self.__team_use_case__,
                print_use_case=self.__print_use_case__,
                current_round_use_case=self.__current_round_use_case__,
                level=level
            )
        ]
        for hint_widget in self.__hint_widgets__:
            hint_widget: QWidget
            self.__stacked_round_layouts__.addWidget(hint_widget)
        # row, column, row_span, column_span
        self.addWidget(self.__stacked_round_layouts__, 2, 0, 2, 1)

    def __init__(self, level: int) -> None:
        """
        Creates the UI where the user can enter hints
        they are given by the battle factory.
        The hints include three Pokémon the user has,
        and the three they have to choose from.
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

        # Output text boxes
        self.__text_output_widget__ = DualTextOutputWidget()
        # row, column, row_span, column_span
        self.addWidget(self.__text_output_widget__, 4, 0, 1, 2)
        self.__print_use_case__: PrintUseCase = \
            PrintUseCase(self.__text_output_widget__)

        # For the user to enter their team and choice Pokémon
        self.__team_layout__: TeamLayout = TeamLayout(self.__team_use_case__)
        # row, column
        self.addLayout(self.__team_layout__, 0, 0)

        # For the user to enter the hints they get
        self.__hint_widgets__: list[QWidget] | None = None
        self.__stacked_round_layouts__: list[QWidget] | None = None
        self.__set_up_stacked_rounds__(level=level)

        # For the user to change the round they are in
        self.__radio_buttons_rounds__ = None
        self.__set_up_round_radio_buttons__()
