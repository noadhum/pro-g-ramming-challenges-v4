from typing import List, Optional, Tuple

from visual.object import Main

class Node:
    def __init__(self, x: int, y: int, parent: Optional[Node] = None) -> None:
        self.x = x
        self.y = y
        self.parent = parent

        self.f = 0
        self.g = 0
        self.h = 0
    
    def get_neighbors(self):
        neighbors: List[Tuple[int, int]] = []

        direction = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
        ]

        for dx, dy in direction:
            nx = self.x + dx
            ny = self.y + dy
            neighbors.append((nx, ny))
        return neighbors

main = Main()
main.run()