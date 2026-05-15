from typing import Optional, List

from .logic import puzzle_logic

class Puzzle:
    """
    Represents a n-Puzzle board.

    Args:
    - size: The board (row and col) size.
    """
    def __init__(self, size: int, state: Optional[List[int]] = None) -> None:
        self.size = size
        self.state = state or puzzle_logic.shuffle(list(range(1, self.size ** 2)) + [0])
    
    def __str__(self) -> str:
        return str(self.state)

    def solved(self):
        return puzzle_logic.is_solved(self.state)

    def move(self, direction: str):
        return puzzle_logic.move(self.state, direction)
    
    def shuffle(self):
        self.state = puzzle_logic.shuffle(self.state)
