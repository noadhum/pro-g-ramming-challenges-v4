from typing import List, Tuple

import random

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
    - size: The board (row and col) size.
    """
    def __init__(self, size: int) -> None:
        self.size = size
        self.state = PuzzleLogic.shuffle(list(range(1, self.size ** 2)) + [0])

    def move(self, direction: str):
        return PuzzleLogic.move(self.state, direction)
    
    def shuffle(self):
        self.state = PuzzleLogic.shuffle(self.state)
        
class PuzzleLogic:
    """
    A n-Puzzle board logic.
    """
    @staticmethod
    def is_solved(state: List[int], goal_state: List[int]):
        """
        Check if given state is solved.
        """
        return state == goal_state

    @staticmethod
    def get_neighbors(state: List[int]) -> List[Tuple[List[int], str]]:
        """
        Return all valid moves and their resulting states from the given state.
        """
        neighbors: List[Tuple[List[int], str]] = []
        for direction in DIRECTIONS:
            new_state = state.copy()

            if PuzzleLogic.move(new_state, direction):
                neighbors.append((new_state, direction))
        return neighbors
    
    @staticmethod
    def manhattan(state: List[int]) -> int:
        """
        Get the manhattan distance from given state to goal state.
        """
        size = get_board_size(state)

        total = 0
        for index, tile in enumerate(state):
            if tile != 0:
                row, col = index_to_grid_coordinate(index, size)
                goal_row, goal_col = index_to_grid_coordinate(tile - 1, size)
                total += abs(row - goal_row) + abs(col - goal_col)
        return total

    @staticmethod
    def shuffle(state: List[int]):
        """
        Returns a new shuffled board state.
        """
        size = get_board_size(state)

        new_state = state.copy()
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
                    if PuzzleLogic._can_move(new_state, direction, size):
                        possible_moves.append(direction)
        
            current_move = random.choice(possible_moves)
            PuzzleLogic._move(new_state, current_move, size)
            last_move = current_move
        return new_state

    @staticmethod
    def move(state: List[int], direction: str):
        """
        Moving empty tile in state to given direction.
        """
        size = get_board_size(state)
        return PuzzleLogic._move(state, direction, size)

    @staticmethod
    def _move(state: List[int], direction: str, size: int):
        direction = direction.lower()
        if direction not in DIRECTIONS:
            return False

        if not PuzzleLogic._can_move(state, direction, size):
            return False
        
        empty_row, empty_col = PuzzleLogic._get_empty_coordinate(state, size)
        target_row, target_col = PuzzleLogic._get_target_coordinate(state, direction, size)

        swap(
            state,
            grid_coordinate_to_index(empty_row, empty_col, size),
            grid_coordinate_to_index(target_row, target_col, size)
        )
        return True
    
    @staticmethod
    def _can_move(state: List[int], direction: str, size: int):
        """
        Check if state can move to given direction.
        """
        row, col = PuzzleLogic._get_target_coordinate(state, direction, size)
        return in_bounds(row, col, size)
    
    @staticmethod
    def _get_target_coordinate(state: List[int], direction: str, size: int) -> Tuple[int, int]:
        """
        Get the target coordinate (row, col) of given direction.
        """
        delta_row, delta_col = DIRECTIONS[direction]
        empty_row, empty_col = PuzzleLogic._get_empty_coordinate(state, size)
        target_row, target_col = empty_row + delta_row, empty_col + delta_col

        return target_row, target_col

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

def get_board_size(state: List[int]):
    """
    Returns a board size.
    """
    return int(len(state) ** 0.5)