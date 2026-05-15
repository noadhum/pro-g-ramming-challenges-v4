from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import heapq

from .logic import puzzle_logic

@dataclass(slots=True, frozen=True)
class Node:
    """
    Represents an A* (A-star) state.

    Args:
        state: The board state.
        parent: The state's parent.
        move: Move taken to reach this state.
        g: Depth of node/Total move of empty tile (0).
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
        return (self.f, self.h, self.g) < (other.f, other.h, other.g)
    
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
        start: Initial state of the n-Puzzle's game board.
    """
    def __init__(self, start: List[int]) -> None:
        self.start = start
    
    def solve(self) -> List[str]:
        """
        Solve a intial state to goal state.

        Returns:
    
        """
        self.open_set = NodeQueue()
        self.closed_set: set[Sequence[int]] = set()
        self.g_score: Dict[Sequence[int], int] = {}

        start_node = Node(self.start)
        self.open_set.push(start_node)
        self.g_score[start_node.state] = 0

        while self.open_set:
            current_node = self.open_set.pop()
            if current_node.state in self.closed_set:
                continue
            
            self.closed_set.add(current_node.state)

            if current_node.solved:
                return self._reconstruct_path(current_node)
            
            for neighbor in current_node.neighbors:
                if neighbor.state in self.closed_set:
                    continue

                if neighbor.state not in self.g_score or neighbor.g < self.g_score[neighbor.state]:
                    self.g_score[neighbor.state] = neighbor.g
                    self.open_set.push(neighbor)
        return []
    
    @staticmethod
    def _reconstruct_path(goal_node: Node):
        path: List[str] = []

        node = goal_node
        while node.parent:
            if node.move:
                path.append(node.move)
                node = node.parent
        path.reverse()
        return path