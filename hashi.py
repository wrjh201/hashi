import itertools as it
from typing import Iterator, Optional


Pos = tuple[int, int]
Line = tuple[Pos, Pos]

def proper_order(p1: Pos, p2: Pos) -> tuple[Pos, Pos]:
    return (p1, p2) if p2 >= p1 else (p2, p1)

def parallel_to_y(l: Line) -> bool:
    return l[0][1] == l[1][1]
def parallel_to_x(l: Line) -> bool:
    return l[0][0] == l[1][0]
def paralell_to_axis(l: Line) -> bool:
    return parallel_to_x(l) or parallel_to_y(l)

def lines_insersect(l1 : Line, l2: Line) -> bool:
    assert paralell_to_axis(l1)
    assert paralell_to_axis(l1)
    if parallel_to_x(l1):
        # x11 <= x21 = x22 <= x12
        v1 = l1[0][0] <= l2[0][0] <= l1[1][0]
        # y21 <= y11 = y12 <= y22
        v2 = l2[0][1] <= l1[0][1] <= l2[1][1]
        return v1 and v2
    else:
        v1 = l1[0][1] <= l2[0][1] <= l1[1][1]
        v2 = l2[0][0] <= l1[0][0] <= l2[1][0]
        return v1 and v2

class NESW:

    def __init__(self,
                 north: int = 2,
                 east: int = 2,
                 south: int = 2,
                 west: int = 2,
                 ):
        self.north = north
        self.east = east
        self.south = south
        self.west = west

    def __repr__(self) -> str:
        return f"(n:{self.north}, e:{self.east}, s:{self.south}, w:{self.west})"

    def intersect(self, other ):
        self.north = min(self.north, other.north)
        self.east = min(self.east, other.east)
        self.south = min(self.south, other.south)
        self.west = min(self.west, other.west)

    def union(self, other):
        self.north = max(self.north, other.north)
        self.east = max(self.east, other.east)
        self.south = max(self.south, other.south)
        self.west = max(self.west, other.west)

    def total(self):
        return self.north + self.east + self.south + self.west
                 


class Hashi:

    def __init__(self) -> None:
        self.nodes: dict[Pos, int] = {}
        self.nesw: dict[Pos, NESW] = {}
        self.bridges : dict[Line, int] = {}

    def connected_bridges(self, node: Pos) -> Iterator[tuple[Line, int]]:
        for (p1, p2), w in self.bridges.items():
            if node in (p1, p2):
                yield ((p1, p2), w)

    def north_adjacent(self, node: Pos) -> Optional[Pos]:
        return min(
            filter(lambda n: n[1] > node[1] and n[0] == node[0], self.nodes.keys()),
            key = lambda x: x[1],
            default=None)

    def south_adjacent(self, node: Pos) -> Optional[Pos]:
        return max(
            filter(lambda n: n[1] < node[1] and n[0] == node[0], self.nodes.keys()),
            key = lambda x: x[1],
            default=None)

    def east_adjacent(self, node: Pos) -> Optional[Pos]:
        return min(
            filter(lambda n: n[0] > node[0] and n[1] == node[1], self.nodes.keys()),
            key = lambda x: x[0],
            default= None)

    def west_adjacent(self, node: Pos) -> Optional[Pos]:
        return max(
            filter(lambda n: n[0] < node[0] and n[1] == node[1], self.nodes.keys()),
            key = lambda x: x[0],
            default = None)
    def adjacent_nodes(self, node: Pos) -> Iterator[Pos]:
        yplus = self.north_adjacent(node)
        yminus = self.south_adjacent(node)
        xplus = self.east_adjacent(node)
        xminus = self.west_adjacent(node)
        if yplus:
            yield yplus
        if yminus:
            yield yminus
        if xplus:
            yield xplus
        if xminus:
            yield xminus

    def add_node(self, pos: Pos, weight: int) -> None:
        assert 1 <= weight <= 8
        self.nodes[pos] = weight

    def add_bridge(self, p1: Pos, p2: Pos, weight: int) -> None:
        assert 0 <= weight <= 2
        assert paralell_to_axis((p1, p2))
        p1, p2 = proper_order(p1, p2)
        if weight == 0:
            # silently delete without exception
            self.bridges.pop((p1, p2), None) 
        else:
            self.bridges[(p1, p2)] = weight

    def check_intersections(self) -> bool:
        """Check all bridges for intersections. Returns True if one is found."""
        return any(lines_insersect(p1, p2) for p1, p2 in it.combinations(self.bridges.keys(), 2))

    def check_weights(self) -> bool:
        """Check each node has a number of bridges connected less than or equal to its weight."""
        for n,w in self.nodes.items():
            weight_sum = 0
            for (p1, p2), bw in self.connected_bridges(n):
                weight_sum += bw
            if weight_sum >= w:
                return False
        return True
                

    def valid_board(self) -> bool:
        """Returns True if the board obeys all the rules of Hashi.
        A valid board is not necessarily a solution but all solutions are valod.
        """
        if self.check_intersections():
            return False
        if not self.check_weights():
            return False

        return True

    def solve_fill(self):
        """Give each node a NESW instance."""
        for node, weight in self.nodes.items():
            temp = max(weight, 2)
            nesw = NESW(temp, temp, temp, temp)

            north = self.north_adjacent(node)
            if north:
                nesw.north = min(2, self.nodes[north])
            else:
                nesw.north = 0

            east = self.east_adjacent(node)
            if east:
                nesw.east = min(2, self.nodes[east])
            else:
                nesw.east = 0

            south = self.south_adjacent(node)
            if south:
                nesw.south = min(2, self.nodes[south])
            else:
                nesw.south = 0

            west = self.west_adjacent(node)
            if west:
                nesw.west = min(2, self.nodes[west])
            else:
                nesw.west = 0
            print(node, nesw)
            self.nesw[node] = nesw

            
            
    def generate_dot(self, filename):
        with open(filename, "w") as f:
            f.write("graph {\n")
            for (x,y), w in self.nodes.items():
                f.write(f"\"{x},{y}\" [label={w} pos=\"{x},{y}!\" shape=circle];\n")
            for ((x1,y1),(x2,y2)), w in self.bridges.items():
                f.write(f"\"{x1},{y1}\" -- \"{x2},{y2}\"")
            f.write("}")

    
t1 = [
    0,0,4,
    2,0,5,
    5,0,3,
    1,1,1,
    3,1,2,
    0,2,2,
    2,2,2,
    1,3,3,
    3,3,5,
    5,3,5,
    0,5,1,
    5,5,3
]
assert len(t1) % 3 == 0
h = Hashi()
for i in range(len(t1)//3):
    h.add_node((t1[3*i], t1[3*i+1]), t1[3*i+2])

h.solve_fill()
    
h.adjacent_nodes((3,1))
h.generate_dot("graph.dot")
