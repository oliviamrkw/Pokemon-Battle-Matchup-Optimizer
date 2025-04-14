import csv

def read_effectiveness(file_path):
    """
    Reads a Pokémon type effectiveness CSV file and stores it into a 2D array.

    Args:
        file_path (str): Path to the downloaded CSV file.

    Returns:
        tuple: Contains:
            - types (list): List of type names (e.g., ['Normal', 'Fire', ...]).
            - effectiveness (list of lists): 2D array where effectiveness[i][j] is the
              effectiveness of attacking type types[i] against defending type types[j].
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header row
        types = header[1:]    # Extract defending type names, skipping the first column

        effectiveness = []
        for row in reader:
            values = row[1:]  # Skip the attacking type name in the first column
            effectiveness.append([float(val) for val in values])  # Convert values to floats

    return types, effectiveness
    