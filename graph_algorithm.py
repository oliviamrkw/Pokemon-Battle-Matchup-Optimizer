"""algorithm to create the type graph

"""
import pokemon_class
from pokemon_type_data_scraper import read_effectiveness


def graph_builder(file_path):
    """return the type graph
    """
    types, effectiveness = read_effectiveness(file_path)
    type_indices = {type_name: idx for idx, type_name in enumerate(types)}
    graph = pokemon_class.TypeGraph()
    for p_type in types:
        graph.add_vertex(p_type)
    for po_type in types:
        for pok_type in types:
            graph.add_attacking_edge(po_type, pok_type, effectiveness[type_indices[po_type]][type_indices[pok_type]])
    return graph


def get_effectiveness(graph, attacker, defender):
    """return the effectieve wieght of types
    """
    if isinstance(defender, tuple):
        eff1 = get_effectiveness(graph, attacker, defender[0])
        eff2 = get_effectiveness(graph, attacker, defender[1])
        return eff1 * eff2
    else:
        vertex = graph.vertices[attacker]
        for weight, neighbors in vertex.outgoing_neighbors.items():
            if defender in {v.item for v in neighbors}:
                return weight


def get_overall_effectiveness(graph, recommended_types, enemy_types):
    """Calculate the maximum offensive effectiveness of recommended_types against enemy_types."""
    if isinstance(recommended_types, str):
        return get_effectiveness(graph, recommended_types, enemy_types)
    elif isinstance(recommended_types, tuple):
        return max(get_effectiveness(graph, r, enemy_types) for r in recommended_types)


def strong_weak(chosen_pokemons):
    """return the strong and weak dictionary of the given team
     """
    strong = {}
    weak = {}
    graph = graph_builder(file_path='chart.csv')
    all_types = list(graph.vertices.keys())

    for chosen_pokemon in chosen_pokemons:
        if isinstance(chosen_pokemon, tuple):
            for pok_type in all_types:
                max_eff = max(get_effectiveness(graph, chosen_pokemon[0], pok_type),
                              get_effectiveness(graph, chosen_pokemon[1], pok_type))
                if max_eff == 2.0:
                    strong[pok_type] = strong.get(pok_type, 0) + 1
                elif max_eff in (0.5, 0.0):
                    weak[pok_type] = weak.get(pok_type, 0) + 1

            for pok_type in all_types:
                combined_eff = get_effectiveness(graph, pok_type, chosen_pokemon)
                if combined_eff > 1.0:
                    weak[pok_type] = weak.get(pok_type, 0) + 1
                elif combined_eff < 1.0:
                    strong[pok_type] = strong.get(pok_type, 0) + 1
        else:
            pokemon_vertex = graph.vertices[chosen_pokemon]
            for out in pokemon_vertex.outgoing_neighbors:
                if out == 2.0:
                    for pokemon in pokemon_vertex.outgoing_neighbors[out]:
                        poke = pokemon.item
                        strong[poke] = strong.get(poke, 0) + 1
                elif out in (0.5, 0.0):
                    for pokemon in pokemon_vertex.outgoing_neighbors[out]:
                        poke = pokemon.item
                        weak[poke] = weak.get(poke, 0) + 1
            for inc in pokemon_vertex.incoming_neighbors:
                if inc == 2.0:
                    for pokemon in pokemon_vertex.incoming_neighbors[inc]:
                        poke = pokemon.item
                        weak[poke] = weak.get(poke, 0) + 1
                elif inc in (0.5, 0.0):
                    for pokemon in pokemon_vertex.incoming_neighbors[inc]:
                        poke = pokemon.item
                        strong[poke] = strong.get(poke, 0) + 1
    return strong, weak


def dict_subtraction(strong, weak):
    """return a subtracted strong and weak dictionary to get the final type dictionary
    """
    final_dict = {}
    for poke_type in weak:
        if poke_type in strong:
            temp = weak[poke_type] - strong[poke_type]
            if temp > 0:
                final_dict[poke_type] = temp
        else:
            final_dict[poke_type] = weak[poke_type]
    return final_dict


def get_attacking_effectiveness(graph, attacker, defender):
    """Get effectiveness of attacker against defender from the graph."""
    vertex = graph.vertices[attacker]
    for weight, neighbors in vertex.outgoing_neighbors.items():
        if defender in {v.item for v in neighbors}:
            return weight
    return 1.0


def get_defense_effectiveness(graph, attack_type, defend_types):
    """Get effectiveness of attack_type against defend_types (product for dual types)."""
    multiplier = 1.0
    if isinstance(defend_types, str):
        defend_types = (defend_types,)
    for defend_type in defend_types:
        for weight, vertices in graph.vertices[defend_type].incoming_neighbors.items():
            if attack_type in {v.item for v in vertices}:
                multiplier *= weight
                break
    return multiplier


def score_candidate(graph, candidate_types, enem_team):
    """Score a candidate type against the enemy team."""
    score = 0
    for enemy in enem_team:
        if isinstance(candidate_types, str):
            candidate_list = (candidate_types,)
        else:
            candidate_list = candidate_types
        off_eff = max(
            get_attacking_effectiveness(graph, c, enemy) if isinstance(enemy, str) else get_effectiveness(graph, c,
                                                                                                          enemy) for c
            in candidate_list)
        def_vuln = get_defense_effectiveness(graph, enemy, candidate_list)
        score += off_eff - def_vuln
    return score


def score_assigner(final_dict, enemy_types, graph):
    """assign a given score to each of the types"""
    temp = {}
    for key in final_dict:
        defense_0 = 0
        defense_2 = 0
        defense_5 = 0
        attack_0 = 0
        attack_2 = 0
        attack_5 = 0
        one_point_zero = 0
        key = key.capitalize()
        for type in enemy_types:
            if type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[0.0]}:
                defense_0 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[0.5]}:
                defense_5 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[2.0]}:
                defense_2 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[1.0]}:
                one_point_zero += 1
            elif type in {vertex.item for vertex in graph.vertices[key].outgoing_neighbors[0.0]}:
                attack_0 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].outgoing_neighbors[0.5]}:
                attack_5 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].outgoing_neighbors[2.0]}:
                attack_2 += 1
            elif type in {vertex.item for vertex in graph.vertices[key].incoming_neighbors[1.0]}:
                one_point_zero += 1
        final_score = final_dict[key] * (
                    (30 * defense_0) + (5 * attack_2) + (3 * defense_5) + (0.1 * one_point_zero) - (4.9 * defense_2) - (
                        30 * attack_0) - (2.9 * attack_5))
        temp[key] = final_score
    return temp


def recommend_top_types(enemy_team, file_path='chart.csv', top_x=None):
    """Recommend the top X types against the enemy team."""
    if top_x is None:
        top_x = len(enemy_team)

    graph = graph_builder(file_path)

    strong, weak = strong_weak(enemy_team)
    final_dict = dict_subtraction(strong, weak)

    if not final_dict:
        types = list(graph.vertices.keys())
    else:
        types = list(final_dict.keys())

    # types = list(final_dict.keys())
    single_types = [(t,) for t in types]
    dual_types = [(types[i], types[j]) for i in range(len(types)) for j in range(i + 1, len(types))]
    candidates = single_types + dual_types
    scores = {}
    for cand in candidates:
        scores[cand] = score_candidate(graph, cand, enemy_team)

    sorted_candidates = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    enemy_team_copy = list(enemy_team[:])
    results = []

    if len(sorted_candidates) >= len(enemy_team_copy):
        top_candidates = sorted_candidates[:top_x]

        for cand, score in top_candidates:
            rec_type = cand[0] if len(cand) == 1 else cand
            effectivenesses = [get_overall_effectiveness(graph, rec_type, enemy) for enemy in enemy_team_copy]
            max_eff = max(effectivenesses)
            target_index = effectivenesses.index(max_eff)
            target_enemy = enemy_team_copy.pop(target_index)
            results.append([rec_type, target_enemy])
    else:
        for cand, score in sorted_candidates:
            rec_type = cand[0] if len(cand) == 1 else cand
            effectivenesses = [get_overall_effectiveness(graph, rec_type, enemy) for enemy in enemy_team_copy]
            max_eff = max(effectivenesses)
            target_index = effectivenesses.index(max_eff)
            target_enemy = enemy_team_copy.pop(target_index)
            results.append([rec_type, target_enemy])

        if enemy_team_copy:
            results.extend(recommend_top_types(enemy_team_copy, file_path='chart.csv', top_x=len(enemy_team_copy)))

    results_dict = {enemy: rec for rec, enemy in results}
    ordered_results = [(results_dict[enemy], enemy) for enemy in enemy_team]

    return ordered_results


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E1136', 'W0221'],
        'max-nested-blocks': 4,
        'allowed_modules': ['pygame', 'requests', 'pandas',
                            'io', 'math', 'random', 'pokemon_data_scraper',
                            'graph_algorithm', 'pokemon_final_team', 'pokemon_class', 'pokemon_type_data_scraper']
    })

    results = recommend_top_types(
        ['Water', 'Water', 'Grass', 'Water', ('Ground', 'Fighting'), 'Water'],
        file_path='chart.csv', top_x=6)
    user_team = [item[0] for item in results]
    enemy_team = [item[1] for item in results]
    print("enemy team:", enemy_team)
    print("user team:", user_team)
