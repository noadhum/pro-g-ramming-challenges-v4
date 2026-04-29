# -- PuzzleState's Utilities
def to_index(row, col, order):
    """
    Converting a coordinate (row, col) into index.
    """
    return (row * order) + col

def to_grid_coordinate(index, order):
    """
    Converting index into coordinate (row, col)
    """
    return divmod(index, order)

def in_bounds(row, col, order):
    """
    Check if coordinate is in the bounds.
    """
    return (row >= 0 and row < order) and (col >= 0 and col < order)