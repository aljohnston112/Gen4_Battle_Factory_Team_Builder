from view.DualTextOutputWidget import DualTextOutputWidget


class PrintUseCase:

    def __init__(self, dual_text_output_widget: DualTextOutputWidget):
        self.dual_text_output_widget = dual_text_output_widget

    def print_1(self, text: str | None = None):
        if text:
            self.dual_text_output_widget.write_1(text + "\n")
        else:
            self.dual_text_output_widget.write_1("\n")

    def print_2(self, text: str | None = None):
        if text:
            self.dual_text_output_widget.write_2(text + "\n")
        else:
            self.dual_text_output_widget.write_2("\n")