#ifndef PUZZLE_H
#define PUZZLE_H

typedef struct {
    int *state;
    int board_size;
} Puzzle;

void shuffle(int *state, int board_size);

#endif