"""contains all of our classes and methods for type class and pokemon class

"""
from __future__ import annotations

from typing import Optional
from typing import Any


class Type:
    """
    A Pokemon type.

    Instance Attributes:
        - name: name of the type
        - effectiveness: a dictionary mapping types to effectiveness
        (2.0 = super effective, 0.5 = not very effective, 0.0 = immune)
    """
    name: str
    effectiveness: dict[str, float]

    def __init__(self, name: str, effectiveness: dict[str, float]):
        self.name = name
        self.effectiveness = {}

    def set_effectiveness(self, effectiveness_dict: dict[str, float]) -> None:
        """Set the effectiveness of this type for other types."""
        self.effectiveness = effectiveness_dict


class Pokemon:
    """
    A class to represent a Pokemon.

    Instance Attributes:
        - pokemon_id: the unique Pokemon id
        - name: the name of the Pokemon
        - type1: the primary type of the Pokemon
        - type2: the secondary type of the Pokemon
        - stats: a tuple containing the stats of the Pokemon (HP, Attack, Defense, Special Attack, Special Defense,
        Speed)
        - bst: the base stat total of the Pokemon
    """
    pokemon_id: int
    name: str
    type1: Type
    type2: Optional[Type]
    stats: list[int]
    bst: int

    def __init__(self, pokemon_id: int, name: str, type1: Type, type2: Optional[Type], attack: int, defense: int,
                 spec_attack: int, spec_defense: int, speed: int):
        """Initialize a new Pokemon instance."""
        self.pokemon_id = pokemon_id
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.stats = [attack, defense, spec_attack, spec_defense, speed]
        self.bst = sum(self.stats)


class TypeVertex:
    """
    A class to represent a vertex in a directed graph of Pokémon types.

    Instance Attributes:
        - item: The type of the Pokémon (e.g., 'Fire', 'Water').
        - outgoing_neighbors: A dictionary where keys are weights (2.0, 1.0, 0.5, 0.0)
                             and values are sets of TypeVertex objects this type attacks.
        - incoming_neighbors: A dictionary where keys are weights (2.0, 1.0, 0.5, 0.0)
                             and values are sets of TypeVertex objects this type attacks.
    """
    item: Any
    outgoing_neighbors: dict[float, set[TypeVertex]]
    incoming_neighbors: dict[float, set[TypeVertex]]

    def __init__(self, item: Any, outgoing_neighbors: dict, incoming_neighbors: set) -> None:
        """
        Initialize a TypeVertex with an item and empty neighbor dictionaries.

        Args:
            item: The Pokémon type (e.g., 'Fire').
        """
        self.item = item
        # Initialize with possible weights for outgoing edges
        self.outgoing_neighbors = {0.0: set(), 0.5: set(), 1.0: set(), 2.0: set()}
        # Initialize with no incoming type vertices
        self.incoming_neighbors = {0.0: set(), 0.5: set(), 1.0: set(), 2.0: set()}


class TypeGraph:
    """
        A class to represent the types and the interactions.

        Instance Attributes:
            - verticies: a dictionary representing the graphs verticies
        """
    vertices: dict[Any, TypeVertex]

    def __init__(self) -> None:
        self.vertices = {}  # Initialize Empty Graph

    def add_vertex(self, item: Any) -> None:
        """add incoming and outcoming neighbours to vertices in graph
        """
        self.vertices[item] = TypeVertex(item, {0.0: set(), 0.5: set(), 1.0: set(), 2.0: set()},
                                         {0.0: set(), 0.5: set(), 1.0: set(), 2.0: set()})

    def add_attacking_edge(self, item1: Any, item2: Any, weight: float) -> None:
        """
        Adds an edge between two pokemon types in the graph such that item1 -> item2

        :param item1: Type of attacking pokemon
        :param item2: Type of recieving pokemon
        :param weight: The effectiveness of the attack (2.0,1.0,0.5,0)
        :return: None
        """
        if item1 in self.vertices and item2 in self.vertices:
            if item1 != item2:
                self.vertices[item1].outgoing_neighbors[weight].add(self.vertices[item2])
                self.vertices[item2].incoming_neighbors[weight].add(self.vertices[item1])
            if item1 == item2:
                self.vertices[item1].outgoing_neighbors[weight].add(self.vertices[item2])
                self.vertices[item1].incoming_neighbors[weight].add(self.vertices[item2])

    def spesific_vertex_connections(self, item1: Any):
        """specify specific vertex connections
        """
        one_half_attacks = []
        one_half_incoming = []
        two_attacks = []
        two_incoming = []
        one_attacks = []
        one_incoming = []
        zero_attacks = []
        zero_incoming = []
        if item1 in self.vertices:
            for weight, outgoing_connections in self.vertices[item1].outgoing_neighbors.items():
                if weight == 2.0:
                    two_attacks.extend([elem.item for elem in outgoing_connections])
                elif weight == 1.0:
                    one_attacks.extend([elem.item for elem in outgoing_connections])
                elif weight == 0.5:
                    one_half_attacks.extend([elem.item for elem in outgoing_connections])
                else:
                    zero_attacks.append(outgoing_connections)
            for weight, incoming_connections in self.vertices[item1].incoming_neighbors.items():
                if weight == 2.0:
                    two_incoming.extend([elem.item for elem in incoming_connections])
                elif weight == 1.0:
                    one_incoming.extend([elem.item for elem in incoming_connections])
                elif weight == 0.5:
                    one_half_incoming.extend([elem.item for elem in incoming_connections])
                else:
                    zero_incoming.extend([elem.item for elem in incoming_connections])
        return (one_half_attacks, one_half_incoming, one_attacks, one_incoming, two_attacks, two_incoming,
                zero_attacks, zero_incoming)
