from __future__ import annotations
from typing import List, Optional, Tuple

class Node:
    """
    Represents an A* (A-star) state.

    Arguments:
    - state: The board state.
    - move: The move taken to this state.
    - parent: The state's parent.
    - g: Total empty tile's (0) move.
    - h: Total of misplaced tiles.
    """
    def __init__(self, state: List[int], move: Optional[str], parent: Optional[Node], g: int = 0, h: int = 0) -> None:
        self.state = tuple(state)
        self.move = move
        self.parent = parent

        self.f = g + h
        self.g = g
        self.h = h

class Solver:
    """
    A n-Puzzle Solver.

    Arguments:
    - initial_state: Initial state of the n-Puzzle's game board.
    """
    def __init__(self, initial_state: List[int]) -> None:
        self.initial_state = initial_state
        self.goal_state = list(range(1, len(initial_state))) + [0]

        self.open = []
        self.closed: set[Tuple[int, ...]] = set()
    
    def solve(self):
        pass