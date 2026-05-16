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

typedef enum {
    UP, DOWN, LEFT, RIGHT
} Move;

typedef struct {
    int row;
    int col;
} Coordinate;

const Coordinate DIRECTIONS[] = {
    [UP] = {-1, 0},
    [DOWN] = {1, 0},
    [LEFT] = {0, -1},
    [RIGHT] = {0, 1}
};

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

static inline int to_board_size(int board_length) {
    return (int) sqrt(board_length);
}

static inline int to_board_length(int board_size) {
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

static int get_tile_index(int *state, int board_length, int tile) {
    for (int i = 0; i < board_length; i++) {
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
static Coordinate get_tile_coord(int *state, int board_length, int tile) {
    int tile_index = get_tile_index(state, board_length, tile);
    return to_coord(
        to_board_size(board_length),
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
    Coordinate empty_coord = get_tile_coord(state, board_size * board_size, 0);

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

/****************************************
 * Main Functions
 ****************************************/

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

    Coordinate empty_coord = get_tile_coord(state, board_size * board_size, 0);
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
    int shuffle_amount = board_size * board_size * random_number(9, 18);
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

