from __future__ import annotations
from typing import List, Optional, Tuple

import heapq

from .puzzle import PuzzleLogic

class Node:
    """
    Represents an A* (A-star) state.

    Arguments:
    - state: The board state.
    - parent: The state's parent.
    - g: Depth of node/Total move of empty tile (0).
    """
    def __init__(self, state: List[int], parent: Optional[Node] = None, g: int = 0) -> None:
        self.state = tuple(state)
        self.parent = parent

        self.g = g
        self.h = PuzzleLogic.manhattan(list(self.state))
        self.f = self.g + self.h
    
class Solver:
    """
    A n-Puzzle Solver.

    Arguments:
    - initial_state: Initial state of the n-Puzzle's game board.
    """
    def __init__(self, state: List[int]) -> None:
        self.initial_state = state
        self.goal_state = list(range(1, len(self.initial_state))) + [0]

        self.open: List[Tuple[int, int, Node]] = []
        self.closed: set[Tuple[int, ...]] = set()

        start_node = Node(self.initial_state)
        heapq.heappush(self.open, (start_node.f, start_node.h, start_node))
    
    def solve(self):
        pass