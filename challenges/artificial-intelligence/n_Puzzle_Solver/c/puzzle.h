#ifndef PUZZLE_H
#define PUZZLE_H

/****************************************
 * Includes
 ****************************************/

#include <stdbool.h>

/****************************************
 * Types, Constants
 ****************************************/

typedef struct {
    int *state;
    int board_size;
} Puzzle;

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

/****************************************
 * Functions
 ****************************************/

int get_heuristic(int *state, int board_size);
inline int to_board_length(int board_size);
bool move(int *state, int board_size, Move direction);

#endif