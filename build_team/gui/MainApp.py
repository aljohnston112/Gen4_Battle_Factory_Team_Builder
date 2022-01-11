import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout

from build_team.Strings import string_confirm
from build_team.gui.Hints import Hints
from build_team.gui.Team import Team


def main_app():
    app = QApplication([])

    window = QWidget()
    window.setWindowTitle("Gen4 Team Builder")
    window.setLayout(MainApp())

    window.show()
    sys.exit(app.exec())


class MainApp(QGridLayout):

    def __init__(self):
        super().__init__()
        self.hints = Hints()
        self.addLayout(self.hints, 0, 0)
        self.set_up_button()

    def set_up_button(self):
        button_confirm = QPushButton(string_confirm)
        self.addWidget(button_confirm, 2, 0)
        button_confirm.clicked.connect(self.confirm_clicked)

    def confirm_clicked(self):
        self.hints.confirm_clicked()
