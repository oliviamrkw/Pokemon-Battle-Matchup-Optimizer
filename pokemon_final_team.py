"""functions and helpers to get the final team

"""
import csv
import pokemon_data_scraper
from pokemon_class import Pokemon
from graph_algorithm import recommend_top_types
from pokemon_data_scraper import convert_pokemon_to_id


def get_team_bst(team: Pokemon | list[Pokemon]):
    """gets the teams bst category"""
    if isinstance(team, Pokemon):
        return team.bst
    else:
        total_bst = 0
        for pokemon in team:
            total_bst += get_team_bst(pokemon)
        return total_bst // len(team)


def ideal_bst_range(team: Pokemon | list[Pokemon]):
    """get teh ideal bst range for returning team
    """
    enemy_bst = get_team_bst(team)
    if isinstance(team, Pokemon) or all([team[i - 1].bst == team[i].bst for i in range(1, len(team))]):
        return [enemy_bst - 20, enemy_bst + 20]
    else:
        max_bst = max([pokemon.bst for pokemon in team])
        min_bst = min([pokemon.bst for pokemon in team])
        return [min_bst, max_bst]


def get_pokemon(team: list[int], file_path='pokemon_data.csv'):
    """get pokemon based on pokemon numbers
    """
    poke_list = []
    # pokemon = Pokemon(0, '', Type('', {'':0.0}), Type('', {}), 0, 0, 0, 0, 0)
    for poke in team:
        data = pokemon_data_scraper.get_pokemon_data([poke], file_path)

        if not data or not data[0]:
            continue

        pokemon = Pokemon(
            pokemon_id=data[0][0],
            name=data[0][1],
            type1=data[0][2],
            type2=data[0][3] if data[0][3] else None,
            attack=data[0][4],
            defense=data[0][5],
            spec_attack=data[0][6],
            spec_defense=data[0][7],
            speed=data[0][8]
        )
        poke_list.append(pokemon)
    return poke_list


def filter_bst_team(team: list[Pokemon], bst_range: list[int]):
    """filter the team based on the ideal bst range
    """
    new_team = []
    for pokemon in team:
        if bst_range[0] <= pokemon.bst <= bst_range[1]:
            new_team.append(pokemon)
    return new_team


def get_types(team: list[Pokemon]):
    """get the types of the given pokemon team
    """
    types = []
    for pokemon in team:
        if pokemon.type2 is None:
            types.append(pokemon.type1)
        else:
            types.append((pokemon.type1, pokemon.type2))
    return tuple(types)


def convert_team_to_ints(team) -> list[int]:
    """return a list of pokemon id's for each pokemon in team
    """
    id_list = []
    for pkmn in team:
        id_list.append(convert_pokemon_to_id(pkmn, "pokemon_data.csv"))
    return id_list


def get_user_pokemon(team: list[Pokemon], file_pokemon='pokemon_data.csv', file_types='chart.csv'):
    """get enemy pokemon based on bst and type"""
    enemy_types = get_types(team)
    top_types = recommend_top_types(enemy_types, file_types, len(team))
    enemy_types = [item[0] for item in top_types]
    enemy_bst_range = ideal_bst_range(team)
    possible_poke = []

    with open(file_pokemon, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            poke_types = (row[2], row[3]) if row[3] else row[2]

            if poke_types in [item[0] for item in top_types] or row[2] in enemy_types:
                possible_poke.append(int(row[0]))

    poke_data = get_pokemon(possible_poke, file_pokemon)
    po_data = filter_bst_team(poke_data, enemy_bst_range)

    if len(po_data) < 6:  # case where multiple of the same pokemon are inputted
        remaining_needed = 6 - len(po_data)
        additional_pokemon = [poke for poke in poke_data if poke not in po_data][:remaining_needed]
        po_data.extend(additional_pokemon)

    pok_sorted = sorted(po_data, key=lambda x: x.bst, reverse=True)[:6]

    return [pokemon.name for pokemon in pok_sorted][:6], top_types


if __name__ == '__main__':
    g = get_user_pokemon(get_pokemon([54, 60, 114, 116, 984, 90], 'pokemon_data.csv'), 'pokemon_data.csv', 'chart.csv')
    print("user team", g[0], "\n")
    print("user team types", get_types(get_pokemon(convert_team_to_ints(g[0]), 'pokemon_data.csv')))
    print("type matchups", g[1])  # user, enemy
