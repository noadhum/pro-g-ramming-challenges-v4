/**
 * @file puzzle.c
 * @brief A file containing N-Puzzle's logic.
 * 
 * Index/Coordinate conversion, Tile Movements,
 * Heuristics (Manhattan Distance and Linear Conflict).
 * 
 */

/****************************************
 * Includes
 ****************************************/

#include <assert.h>
#include <math.h>
#include <stdbool.h>
#include <stdlib.h>

#include "puzzle.h"

/****************************************
 * Types, Constants
 ****************************************/

const Move REVERSED_DIRECTIONS[] = {
    [UP] = DOWN,
    [DOWN] = UP,
    [LEFT] = RIGHT,
    [RIGHT] = LEFT
};

/****************************************
 * Inline functions/Utilities
 ****************************************/

static inline int random_number(int min, int max) {
    return ((rand() % (max - min + 1) + min));
}

inline int to_board_size(int board_length) {
    return (int) sqrt(board_length);
}

inline int to_board_length(int board_size) {
    return board_size * board_size;
}

static inline int to_index(int board_size, Coordinate coord) {
    return (coord.row * board_size) + coord.col;
}

static inline Coordinate to_coord(int board_size, int index) {
    return (Coordinate) {
        .row = index / board_size,
        .col = index % board_size
    };
}

static int get_tile_index(int *state, int board_size, int tile) {
    for (int i = 0; i < to_board_length(board_size); i++) {
        if (state[i] == tile) {
            return i;
        }
    }

    assert(false && "Tile index not found.");
    return -1;
}

/**
 * @brief Check if coordinate is in bounds.
 * 
 * @param coord The coordinate (row, col).
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @return true 
 * @return false 
 */
static bool coord_in_bounds(Coordinate coord, int board_size) {
    return (
        (coord.row >= 0 && coord.row < board_size) &&
        (coord.col >= 0 && coord.col < board_size)
    );
}

/**
 * @brief Return the tile coordinate in given state.
 * 
 * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
 * @param board_length The N-Puzzle board length, eg. 8-Puzzle have a board length of 9,
 *                     or board_size * board_size
 * @param tile The number of the target tile.
 * @return Coordinate 
 */
static Coordinate get_tile_coord(int *state, int board_size, int tile) {
    int tile_index = get_tile_index(state, board_size, tile);
    return to_coord(
        board_size,
        tile_index
    );
}

/**
 * @brief Return the given tile's goal coordinate.
 * 
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @param tile The number of the target tile.
 * @return Coordinate 
 */
static Coordinate get_tile_goal_coord(int board_size, int tile) {
    return to_coord(board_size, tile - 1);
}

/**
 * @brief Return the destination coordinate of given direction.
 * 
 * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @param direction A directon between [UP, DOWN, LEFT, RIGHT].
 * @return Coordinate 
 */
static Coordinate get_empty_destination_coord(int *state, int board_size, Move direction) {
    Coordinate delta = DIRECTIONS[direction];
    Coordinate empty_coord = get_tile_coord(state, board_size, 0);

    return (Coordinate) {
        .row = empty_coord.row + delta.row,
        .col = empty_coord.col + delta.col
    };
}

/**
 * @brief Check if given state can move to given direction.
 * 
 * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @param direction A directon between [UP, DOWN, LEFT, RIGHT].
 * @return true 
 * @return false 
 */
static bool can_move(int *state, int board_size, Move direction) {
    Coordinate empty_destination_coord = get_empty_destination_coord(state, board_size, direction);
    return coord_in_bounds(empty_destination_coord, board_size);
}

/**
 * @brief Swapping two tiles in the given state.
 * 
 * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
 * @param index_i The index of the tile i.
 * @param index_j The index of the tile j.
 */
static void swap(int *state, int index_i, int index_j) {
    int temp = state[index_i];
    state[index_i] = state[index_j];
    state[index_j] = temp;
}

/**
 * @brief Return the Manhattan Distance from given tile and tile index.
 * 
 * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @param tile_index The index of the tile in the state.
 * @param tile The number of the tile.
 * @return int 
 */
static int get_manhattan_tile(int *state, int board_size, int tile_index, int tile) {
    Coordinate current_coord = to_coord(board_size, tile_index);
    Coordinate goal_coord = get_tile_goal_coord(board_size, tile);

    return abs(current_coord.row - goal_coord.row) + abs(current_coord.col - goal_coord.col);
}

/**
 * @brief Return the Manhattan Distance of given state.
 * 
 * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @return int 
 */
static int get_manhattan(int *state, int board_size) {
    int total = 0;

    for (int i = 0; i < to_board_length(board_size); i++) {
        int current_tile = state[i];

        if (current_tile != 0) {
            total += get_manhattan_tile(state, board_size, i, current_tile);
        }
    }
    return total;
}

/**
 * @brief Return the total row conflict of given state.
 * 
 * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @return int 
 */
static int count_row_conflict(int *state, int board_size) {
    int row_conflicts = 0;

    for (int row = 0; row < board_size; row++) {
        int valid_row_tiles[board_size];
        int counter = 0;

        for (int col = 0; col < board_size; col++) {
            int current_index = to_index(board_size, (Coordinate){row, col});
            int current_tile = state[current_index];

            if (current_tile == 0) {
                continue;
            }

            Coordinate current_tile_goal_coord = get_tile_goal_coord(board_size, current_tile);

            if (current_tile_goal_coord.row == row) {
                valid_row_tiles[counter++] = current_tile_goal_coord.col;
            }

        }

        for (int i = 0; i < counter; i++) {
            for (int j = i + 1; j < counter; j++) {
                if (valid_row_tiles[i] > valid_row_tiles[j]) {
                    row_conflicts++;
                }
            }
        }
    }

    return row_conflicts;
}

/**
 * @brief Return the total col conflict of given state.
 * 
 * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @return int 
 */
static int count_col_conflict(int *state, int board_size) {
    int col_conflicts = 0;

    for (int col = 0; col < board_size; col++) {
        int valid_col_tiles[board_size];
        int counter = 0;

        for (int row = 0; row < board_size; row++) {
            int current_index = to_index(board_size, (Coordinate){row, col});
            int current_tile = state[current_index];

            if (current_tile == 0) {
                continue;
            }

            Coordinate current_tile_goal_coord = get_tile_goal_coord(board_size, current_tile);

            if (current_tile_goal_coord.col == col) {
                valid_col_tiles[counter++] = current_tile_goal_coord.row;
            }
        }

        for (int i = 0; i < counter; i++) {
            for (int j = i + 1; j < counter; j++) {
                if (valid_col_tiles[i] > valid_col_tiles[j]) {
                    col_conflicts++;
                }
            }
        }
    }

    return col_conflicts;
}

static int get_linear_conflict(int *state, int board_size) {
    return count_row_conflict(state, board_size) + count_col_conflict(state, board_size);
}

/****************************************
 * Main Functions
 ****************************************/

 /**
  * @brief Return the heuristic (f) score of given state.
  * 
  * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
  * @param board_size he N-Puzzle board size, eg. 3 for an 8-Puzzle.
  * @return int 
  */
int get_heuristic(int *state, int board_size) {
    return get_manhattan(state, board_size) + 2 * get_linear_conflict(state, board_size);
}

 /**
  * @brief Moving empty tile in given state to given direction,
  *        return true if move successful, otherwise false.
  * 
  * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
  * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
  * @param direction A directon between [UP, DOWN, LEFT, RIGHT].
  * @return true
  * @return false 
  */
bool move(int *state, int board_size, Move direction) {
    if (!can_move(state, board_size, direction)) {
        return false;
    }

    Coordinate empty_coord = get_tile_coord(state, board_size, 0);
    Coordinate empty_destination_coord = get_empty_destination_coord(state, board_size, direction);

    swap(state,
        to_index(board_size, empty_coord),
        to_index(board_size, empty_destination_coord)
    );
    return true;
}

/**
 * @brief Randomize the given board state.
 * 
 * @param state An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 */
void shuffle(int *state, int board_size) {
    int shuffle_amount = to_board_length(board_size) * random_number(9, 18);
    int last_move = -1;

    for (int i = 0; i < shuffle_amount; i++) {
        int possible_moves[4];
        int counter = 0;

        for (int direction = 0; direction < 4; direction++) {
            if (last_move == -1 || direction != REVERSED_DIRECTIONS[last_move]) {
                if (can_move(state, board_size, direction)) {
                    possible_moves[counter++] = direction;
                }
            }
        }

        int current_move = possible_moves[random_number(0, counter - 1)];
        move(state, board_size, current_move);
        last_move = current_move;
    }
}

