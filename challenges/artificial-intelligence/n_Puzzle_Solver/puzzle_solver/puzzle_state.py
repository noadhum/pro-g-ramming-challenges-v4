import random

from typing import List, Tuple

from puzzle_solver.grid import to_index, to_grid_coordinate

class PuzzleState:
    def __init__(self, order: int) -> None:
        self.order = order
        self.current_tiles = list(range(1, order ** 2)) + [0]
        self.goal_state = self.current_tiles.copy()
        self.shuffle()

        self.directions = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
    
    def is_solved(self):
        """
        Check if current state is solved.
        """
        return self.current_tiles == self.goal_state
    
    def in_bounds(self, row: int, col: int):
        """
        Check if grid coordinate is in bounds.
        """
        return (0 <= row < self.order) and (0 <= col < self.order)
    
    def can_move(self, direction: str):
        """
        Check if current state can move to direction given.
        """
        if direction.lower() not in self.directions:
            return False

        new_row, new_col = self.get_target_position(direction)

        if self.in_bounds(new_row, new_col):
            return True
        return False
    
    def find_empty(self) -> Tuple[int, int]:
        """
        Find the empty tile (0) in current state.
        """
        index = self.current_tiles.index(0)
        return to_grid_coordinate(index, self.order)
    
    def get_target_position(self, direction: str) -> Tuple[int, int]:
        """
        Get the target position of direction given.
        """
        delta_row, delta_col = self.directions[direction.lower()]
        empty_row, empty_col = self.find_empty()

        new_row = empty_row + delta_row
        new_col = empty_col + delta_col
        return new_row, new_col
    
    def swap(self, index1: int, index2: int):
        """
        Swap between two tiles.
        """
        self.current_tiles[index1], self.current_tiles[index2] = self.current_tiles[index2], self.current_tiles[index1]
    
    def move(self, direction: str):
        """
        Moving empty tile (0) to direction given.
        """
        if direction.lower() not in self.directions:
            return False

        if not self.can_move(direction):
            return False
        
        empty_row, empty_col = self.find_empty()
        new_row, new_col = self.get_target_position(direction.lower())

        self.swap(
            to_index(empty_row, empty_col, self.order),
            to_index(new_row, new_col, self.order)
        )
        return True
    
    def shuffle(self):
        """
        Shuffle the board.
        """
        shuffle_moves = self.order * self.order * 10
        last_move = None

        reverse = {
            'up': 'down',
            'down': 'up',
            'left': 'right',
            'right': 'left',
        }

        for _ in range(shuffle_moves):
            possible_moves: List[str] = []

            for direction in self.directions:
                if not last_move or direction != reverse[last_move]:
                    if self.can_move(direction):
                        possible_moves.append(direction)
            
            current_move = random.choice(possible_moves)
            self.move(current_move)
            last_move = current_move