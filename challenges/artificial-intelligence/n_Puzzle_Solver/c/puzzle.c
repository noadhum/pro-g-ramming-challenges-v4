/**
 * A file containing N-Puzzle's logic.
 */
#include <stdio.h>
#include <stdbool.h>

#include "puzzle.h"

#define INDEX_TO_ROW(index, board_size) ((index) / (board_size))
#define INDEX_TO_COL(index, board_size) ((index) % (board_size))
#define COORD_TO_INDEX(row, col, board_size) (((row) * (board_size)) + (col))

typedef struct
{
    int *tiles;
    int size;
} Puzzle;

typedef enum {
    U, // up
    D, // down
    R, // right
    L // left
} Move;

typedef struct {
    int row;
    int col;
} Coordinate;

const Coordinate DIRECTIONS[] = {
    [U] = {-1, 0},
    [D] = {1, 0},
    [R] = {0, 1},
    [L] = {0, -1}
};

const Coordinate REVERSED_DIRECTIONS[] = {
    [U] = {1, 0},
    [D] = {-1, 0},
    [R] = {0, -1},
    [L] = {0, 1}
};

static int get_tile_index(int state[], int board_size, int tile) {
    for (int i = 0; i < board_size; i++) {
        if (state[i] == tile) {
            return i;
        }
    }
    return -1;
}
static Coordinate get_tile_coord(int *state, int board_size, int tile) {
    int tile_index = get_tile_index(state, board_size, tile);
    Coordinate tile_coordinate = {
        INDEX_TO_ROW(tile_index, board_size),
        INDEX_TO_COL(tile_index, board_size)
    };

    return tile_coordinate;
}

static Coordinate get_destination_coord(int *state, int board_size, Move direction) {
    Coordinate delta = DIRECTIONS[direction];
    Coordinate empty_coord = get_tile_coord(state, board_size, 0);
}

bool move(int *state, Move direction, int board_size) {
    if (direction < U || direction > L) {
        return false;
    }

    // if can move to given direction
}

bool can_move(int* state, int board_size, Move direction) {

}

