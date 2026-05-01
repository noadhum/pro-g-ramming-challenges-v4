import heapq

from typing import List, Tuple, Optional

class Node:
    """
    Represents a A* state.
    
    Arguments:
    - state: Tuple representation of the puzzle board.
    - move: The moves taken to reach this state.
    - parent: The parent of the node.
    - g: Depth of Node/Total move.
    - h: Total of misplaced tiles.
    - f: Total cost of g + h.
    """
    def __init__(self, state: List[int], move: Optional[str] = None, parent: Optional[Node] = None, g: int = 0, h: int = 0) -> None:
        self.state = tuple(state)
        self.move = move
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g + h

class Solver:
    """
    A n-Puzzle Solver.
    
    Arguments:
    - initial_state: Initial state of the board
    """
    def __init__(self, initial_state: List[int]) -> None:
        self.initial_state = initial_state

        self.open = []
        self.closed: set[Tuple[int, ...]] = set()