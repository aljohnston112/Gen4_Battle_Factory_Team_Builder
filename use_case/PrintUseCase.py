from view.DualTextOutputWidget import DualTextOutputWidget


class PrintUseCase:

    def __init__(self, dual_text_output_widget: DualTextOutputWidget):
        self.__dual_text_output_widget__ = dual_text_output_widget

    def print_1(self, text: str | None = None):
        if text:
            self.__dual_text_output_widget__.write_1(text + "\n")
        else:
            self.__dual_text_output_widget__.write_1("\n")

    def print_2(self, text: str | None = None):
        if text:
            self.__dual_text_output_widget__.write_2(text + "\n")
        else:
            self.__dual_text_output_widget__.write_2("\n")

    def clear_both(self):
        self.__dual_text_output_widget__.clear_button.click()