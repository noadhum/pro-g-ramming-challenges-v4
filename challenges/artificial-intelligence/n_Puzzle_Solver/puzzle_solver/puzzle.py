from .logic import puzzle_logic

class Puzzle:
    """
    Represents a n-Puzzle board.

    Args:
    - size: The board (row and col) size.
    """
    def __init__(self, size: int) -> None:
        self.size = size
        self.state = puzzle_logic.shuffle(list(range(1, self.size ** 2)) + [0])

    def move(self, direction: str):
        return puzzle_logic.move(self.state, direction)
    
    def shuffle(self):
        self.state = puzzle_logic.shuffle(self.state)
