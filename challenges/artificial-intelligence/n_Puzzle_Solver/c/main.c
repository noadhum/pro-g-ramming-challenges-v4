#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "puzzle.h"

int main() {
    srand(time(NULL));

    int my_state[] = {1, 2, 3, 4, 5, 6, 7, 8, 0};
    Puzzle my_puzzle = {my_state, 3};

    shuffle(my_puzzle.state, my_puzzle.board_size);

    for (int i = 0; i < 9; i++) {
        printf("%d", my_puzzle.state[i]);
    }
    printf("\n");

    return 0;
}