from enum import Enum, unique


@unique
class Category(Enum):
    """
    Represents whether a Pokémon move of physical or special.
    """
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


__CATEGORY_DICT__: dict[str, Category] = {
    "physical": Category.PHYSICAL,
    "special": Category.SPECIAL,
    "status": Category.STATUS
}


def get_category(category: str):
    return __CATEGORY_DICT__[category.lower()]
