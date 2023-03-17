from typing import Callable

from PyQt5.QtWidgets import QPushButton, QDialog


class StringButton(QPushButton):
    """
    A button that can take a callback that takes a String as a parameter,
    so the registered callback can get the string in this button when it is clicked.
    """

    def __init__(
            self,
            string: str,
            clicked_callback: Callable[[str], None]
    ) -> None:
        super().__init__()
        self.setText(string)
        self.clicked_callback = clicked_callback
        self.clicked.connect(self.callback)

    def callback(self):
        self.clicked_callback(self.text())
