from parser.parse_moves import get_moves
from parser.parse_pokemon import get_pokemon
from parser.parse_types import get_attack_type_dict, get_defend_type_dict

pokemon = get_pokemon()
moves = get_moves()
type_chart_attack = get_attack_type_dict()
type_chart_defend = get_defend_type_dict()
types = ["Normal", "Fighting", "Flying",
         "Poison", "Ground", "Rock",
         "Bug",	"Ghost", "Steel",
         "Fire", "Water", "Grass",
         "Electric", "Psychic", "Ice",
         "Dragon", "Dark"
         ]
