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

    Args:
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
        Check if board state matches the goal state.

        Args:
            state (List[int]): A board state
            goal_state (List[int]): The board's goal state.

        Returns:
            bool: True if state matches the goal state, otherwise False
        """
        return state == goal_state

    @staticmethod
    def get_neighbors(state: List[int]) -> List[Tuple[List[int], str]]:
        """
        Get valid neighbors from given state.

        Args:
            state (List[int]): A board state.
        
        Returns:
            List[Tuple[List[int], str]]: A list containing valid moves and their resulting states.
        """

        # Example:
        # Input:
        #  [1, 2, 3,
        #   4, 5, 6,
        #   7, 8, 0]
        #   
        # Output:
        # [
        #   ([1, 2, 3
        #     4, 5, 0,
        #     7, 8, 6], 'up'),
        #
        #   ([1, 2, 3,
        #     4, 5, 6,
        #     7, 0, 8], 'left')
        # ]

        neighbors: List[Tuple[List[int], str]] = []
        for direction in DIRECTIONS:
            new_state = state.copy()

            if PuzzleLogic.move(new_state, direction):
                neighbors.append((new_state, direction))
        return neighbors
    
    @staticmethod
    def heuristic(state: List[int]):
        """
        Get the heuristic (h) cost of a state using Manhattan Distance and Linear Conflict.

        Args:
            state (List[int]): A board state.
        
        Returns:
            int: The state heuristic (h) cost.
        """
        return PuzzleLogic.manhattan(state) + 2 * PuzzleLogic.linear_conflict(state)
    
    @staticmethod
    def manhattan(state: List[int]) -> int:
        """
        Find how far a board is from its goal (Manhattan Distance).

        Args:
            state (List[int]): A board state.
        
        Returns:
            int: The manhattan distance of a board.
        """
        total = 0
        for index, tile in enumerate(state):
            if tile != 0:
                total += PuzzleLogic.manhattan_tile(state, tile, index)
        return total
    
    @staticmethod
    def manhattan_tile(state: List[int], tile: int, current_tile_index: int) -> int:
        """
        Find how far a tile is from its goal (Manhattan Distance).

        Args:
            state (List[int]): A board state.
            tile (int): The number on the tile.
            current_tile_index: Where the is at right now.
        
        Returns:
            int: The manhattan distance of a tile.
        """
        size = get_board_size(state)

        row, col = index_to_grid_coordinate(current_tile_index, size)
        goal_row, goal_col = PuzzleLogic.get_goal_coordinate(tile, size)
        return abs(row - goal_row) + abs(col - goal_col)
    
    @staticmethod
    def linear_conflict(state: List[int]) -> int:
        """
        Get the linear conflict from given state.

        Args:
            state (List[int]): A board state.
        
        Returns:
            int: The conflict amount of a state
        """
        size = get_board_size(state)
        return PuzzleLogic._row_conflict(state, size) + PuzzleLogic._col_conflict(state, size)

    @staticmethod
    def _row_conflict(state: List[int], size: int) -> int:
        """
        Get the linear conflict from given row state:

        Args:
            state (List[int]): A board state.
            size (int): The board size.
        
        Returns:
            int: The conflict amount of a row state.
        """
        row_conflict = 0

        for row in range(size):
            valid_row_tiles: List[int] = []

            for col in range(size):
                current_index = grid_coordinate_to_index(row, col, size)
                tile = state[current_index]

                if tile == 0:
                    continue

                goal_row, goal_col = PuzzleLogic.get_goal_coordinate(tile, size)

                if goal_row == row:
                    valid_row_tiles.append(goal_col)
        
            for current_index, current_goal_col in enumerate(valid_row_tiles):
                for next_goal_col in valid_row_tiles[current_index+1:]:
                    if current_goal_col > next_goal_col:
                        row_conflict += 1
        return row_conflict

    @staticmethod
    def _col_conflict(state: List[int], size: int) -> int:
        """
        Get the linear conflict from given column state.

        Args:
            state (List[int]): A board state.
            size (int): The board size.
        
        Returns:
            int: The conflict amount of a column state.
        """
        column_conflict = 0

        for col in range(size):
            valid_col_tiles: List[int] = []

            for row in range(size):
                current_index = grid_coordinate_to_index(row, col, size)
                tile = state[current_index]

                if tile == 0:
                    continue

                goal_row, goal_col = PuzzleLogic.get_goal_coordinate(tile, size)

                if goal_col == col:
                    valid_col_tiles.append(goal_row)

            for current_index, current_goal_row in enumerate(valid_col_tiles):
                for next_goal_row in valid_col_tiles[current_index+1:]:
                    if current_goal_row > next_goal_row:
                        column_conflict += 1
        return column_conflict
    
    @staticmethod
    def get_goal_coordinate(tile: int, size: int) -> Tuple[int, int]:
        """
        Get the goal position of a tile.
        """
        if tile == 0:
            raise ValueError('Empty tile (0) does not have a goal coordinate.')

        return index_to_grid_coordinate(tile - 1, size)

    @staticmethod
    def shuffle(state: List[int]) -> List[int]:
        """
        Generates a new solvable shuffled board.

        Args:
            state (List[int]): A board to shuffle, eg. [1, 2, 3, 0]
        
        Returns:
            List[int]: A new list containing shuffled tiles.
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
        Moving an empty tile in a state to given direction.

        Args:
            state (List[int]): A board state.
            direction (str): A direction in ['up', 'down', 'left', 'right'].
        
        Returns:
            bool: True if empty tile successfully move into that direction, otherwise False
        """
        size = get_board_size(state)
        return PuzzleLogic._move(state, direction, size)

    @staticmethod
    def _move(state: List[int], direction: str, size: int):
        """
        Move an empty tile into its direction.
        """
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