from enum import Enum, unique


@unique
class Category(Enum):
    """
    Represents whether a Pokemon move of physical or special.
    """
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


__SPLIT_DICT__ = {
    "physical": Category.PHYSICAL,
    "special": Category.SPECIAL,
    "status": Category.STATUS
}


def get_split(split):
    return __SPLIT_DICT__[split.lower()]
