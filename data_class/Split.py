from enum import Enum, unique


@unique
class Split(Enum):
    """
    Represents whether a Pokemon move of physical or special.
    """
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


__SPLIT_DICT__ = {
    "physical": Split.PHYSICAL,
    "special": Split.SPECIAL,
    "status": Split.STATUS
}


def get_split(split):
    return __SPLIT_DICT__[split.lower()]
