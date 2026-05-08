from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import heapq

from .logic import puzzle_logic

@dataclass(slots=True, frozen=True)
class Node:
    """
    Represents an A* (A-star) state.

    Args:
    - state: The board state.
    - parent: The state's parent.
    - move: Move taken to reach this state.
    - g: Depth of node/Total move of empty tile (0).
    """
    state: Sequence[int]
    parent: Optional[Node] = None
    move: Optional[str] = None
    g: int = 0

    def __post_init__(self):
        object.__setattr__(self, 'state', tuple(self.state))

    @property
    def h(self) -> int:
        return puzzle_logic.heuristic(self.state)
    
    @property
    def f(self) -> int:
        return self.g + self.h
    
    @property
    def solved(self):
        return puzzle_logic.is_solved(self.state)
    
    @property
    def neighbors(self) -> List[Node]:
        node_neighbors: List[Node] = []
        for state, direction in puzzle_logic.get_neighbors(self.state):
            node_neighbors.append(Node(state, self, direction, self.g + 1))
        return node_neighbors
    
    def __lt__(self, other: Node):
        return self.f < other.f or self.h < other.h
    
    def __repr__(self) -> str:
        return f"Node(f={self.f}, g={self.g}, h={self.h}, state={self.state}, move='{self.move}')"

class NodeQueue:
    def __init__(self) -> None:
        self.queue: List[Tuple[int, int, Node]] = []
    
    def push(self, node: Node):
        heapq.heappush(self.queue, (node.f, node.h, node))
    
    def pop(self):
        return heapq.heappop(self.queue)[2]
    
    def __bool__(self):
        return bool(self.queue)
    
    def __contains__(self, item: Node):
        return any(item == node[-1] for node in self.queue)
    
    def __repr__(self) -> str:
        if not self.queue:
            return 'NodeQueue([])'
        
        body = ''.join(f'    {node}\n' for _, _, node in self.queue)
        return f'NodeQueue([\n{body}])'
    
class Solver:
    """
    A n-Puzzle Solver.
    Using A* Search Algorithm to solve a n-Puzzle.

    Args:
    - start: Initial state of the n-Puzzle's game board.
    """
    def __init__(self, start: List[int]) -> None:
        self.start = start
    
    def solve(self):
        self.pending = NodeQueue()
        self.proccessed: set[Sequence[int]] = set()

        self.pending.push(Node(self.start))

        while self.pending:
            current_node = self.pending.pop()
            self.proccessed.add(current_node.state)

            if current_node.solved:
                return # return the moves to reach goal state
            
            for neighbor in current_node.neighbors:
                if neighbor.state in self.proccessed:
                    continue

                if current_node > neighbor or neighbor not in self.pending:
                    if neighbor not in self.pending:
                        self.pending.push(neighbor)