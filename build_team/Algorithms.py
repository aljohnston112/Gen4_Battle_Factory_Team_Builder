from collections import defaultdict

from build_team.Data import pokemon, moves, types, type_chart_attack, type_chart_defend
from pokemon import Pokemon


def get_defense_multipliers(pokemon_in):
    defense_multipliers = defaultdict(lambda: defaultdict(lambda: 1.0))
    ap: list[Pokemon] = []
    for p in pokemon_in:
        if p != "":
            gen = [v for k, v in pokemon.items() if p.lower() in k.lower()]
            for g in gen:
                ap.append(g)
    for p in ap:
        types_ = p.types
        for t in types_:
            # [no_eff, not_eff, normal_eff, super_eff]
            no_effect_types = type_chart_defend[0].get(t, [])
            not_effective_types = type_chart_defend[1].get(t, [])
            super_effective_types = type_chart_defend[3].get(t, [])
            defense_multipliers[p.name][t] = defense_multipliers[p.name][t]
            for tt in no_effect_types:
                defense_multipliers[p.name][tt] *= 0.0
            for tt in not_effective_types:
                defense_multipliers[p.name][tt] *= 0.5
            for tt in super_effective_types:
                defense_multipliers[p.name][tt] *= 2.0

    return defense_multipliers
