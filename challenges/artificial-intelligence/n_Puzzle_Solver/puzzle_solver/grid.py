from typing import Tuple

def to_index(row: int, col: int, order: int) -> int:
    """
    Converting a coordinate (row, col) into index.
    """
    return (row * order) + col

def to_grid_coordinate(index: int, order: int) -> Tuple[int, int]:
    """
    Converting index into coordinate (row, col)
    """
    return divmod(index, order)

def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])