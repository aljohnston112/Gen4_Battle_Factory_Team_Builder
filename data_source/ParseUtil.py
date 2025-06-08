import typing


def get_next_non_newline(file: typing.IO) -> str:
    """
    Gets the next line that is not a new line from a file.

    :param file: The file to get the line from.
    :return: The next line that is not a new line.
    """
    s = "\n"
    while s.isspace():
        s = file.readline()
    return s



