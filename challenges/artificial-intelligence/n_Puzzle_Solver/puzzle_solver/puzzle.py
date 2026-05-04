import random

from typing import List, Tuple

DIRECTIONS = {
    'up': (-1, 0),
    'down': (1, 0),
    'left': (0, -1),
    'right': (0, 1)
}

class Puzzle:
    """
    Represents a n-Puzzle board.

    Arguments:
    - board_size: The board (row and col) size.
    """
    def __init__(self, board_size: int) -> None:
        self.size = board_size
        self.state = list(range(1, self.size ** 2)) + [0]
        self.shuffle()

    def move(self, direction: str):
        return PuzzleLogic.move(self.state, direction, self.size)
    
    def shuffle(self):
        PuzzleLogic.shuffle(self.state, self.size)
        
class PuzzleLogic:
    """
    A n-Puzzle board logic.
    """
    @staticmethod
    def get_neighbors(state: List[int], size: int) -> List[Tuple[List[int], str]]:
        neighbors: List[Tuple[List[int], str]] = []
        for direction in DIRECTIONS:
            new_state = state.copy()

            if PuzzleLogic.move(new_state, direction, size):
                neighbors.append((new_state, direction))
        return neighbors

    @staticmethod
    def shuffle(state: List[int], size: int):
        """
        Shuffle the board state.
        """
        shuffle_amount = size ** 2 * 10
        last_move = None

        reverse = {
            'up': 'down',
            'down': 'up',
            'left': 'right',
            'right': 'left'
        }

        for _ in range(shuffle_amount):
            possible_moves: List[str] = []
            for direction in DIRECTIONS:
                if not last_move or direction != reverse[last_move]:
                    if PuzzleLogic._can_move(state, direction, size):
                        possible_moves.append(direction)
        
            current_move = random.choice(possible_moves)
            PuzzleLogic.move(state, current_move, size)
            last_move = current_move

    @staticmethod
    def move(state: List[int], direction: str, size: int):
        """
        Moving empty tile in state tp direction given.
        """
        direction = direction.lower()
        if direction not in DIRECTIONS:
            return False

        if not PuzzleLogic._can_move(state, direction, size):
            return False
        
        empty_row, empty_col = PuzzleLogic._get_empty_coordinate(state, size)
        delta_row, delta_col = DIRECTIONS[direction]
        new_row, new_col = empty_row + delta_row, empty_col + delta_col

        swap(
            state,
            grid_coordinate_to_index(empty_row, empty_col, size),
            grid_coordinate_to_index(new_row, new_col, size)
        )
        return True
    
    @staticmethod
    def _can_move(state: List[int], direction: str, size: int):
        """
        Check if state can move to direction given.
        """
        new_row, new_col = PuzzleLogic._get_target_coordinate(state, direction, size)
        return in_bounds(new_row, new_col, size)
    
    @staticmethod
    def _get_target_coordinate(state: List[int], direction: str, size: int) -> Tuple[int, int]:
        """
        Get the target coordinate (row, col) of direction given.
        """
        delta_row, delta_col = DIRECTIONS[direction]
        empty_row, empty_col = PuzzleLogic._get_empty_coordinate(state, size)
        new_row, new_col = empty_row + delta_row, empty_col + delta_col

        return new_row, new_col

    @staticmethod
    def _get_empty_coordinate(state: List[int], size: int) -> Tuple[int, int]:
        """
        Get the empty tile (0) coordinate (row, col).
        """
        empty_index = state.index(0)
        return index_to_grid_coordinate(empty_index, size)

# -- Helper --
def index_to_grid_coordinate(index: int, board_size: int) -> Tuple[int, int]:
    """
    Converting an index into grid coordinate (row, col).
    """
    return divmod(index, board_size)

def grid_coordinate_to_index(row: int, col: int, board_size: int) -> int:
    """
    Converting a grid coordinate (row, col) into index.
    """
    return (row * board_size) + col

def swap(state: List[int], index1: int, index2: int):
    """
    Swap between two index.
    """
    state[index1], state[index2] = state[index2], state[index1]

def in_bounds(row: int, col: int, board_size: int):
    """
    Check if coordinate (row, col) is in bounds.
    """
    return (0 <= row < board_size) and (0 <= col < board_size)
