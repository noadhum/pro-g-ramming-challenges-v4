/**
 * @file solver.c
 * @brief A file containing N-Puzzle solver logic using A* algorithm.
 * 
 */

 /****************************************
 * Includes
 ****************************************/

 #include <assert.h>
#include <stdbool.h>
#include <stdlib.h>

#include "puzzle.h"

 /****************************************
 * Types
 ****************************************/

typedef struct Node
{
    int *state;   // An N-Puzzle board state, eg. {1, 2, 3, ..., 0}.
    struct Node *parent; // 
    int g;        // The depth of node/Total moves of empty tile (0).
} Node;

/****************************************
 * Inline functions/Utilities
 ****************************************/

 /**
  * @brief Return the heuristic (h) cost of given node.
  * 
  * @param node An A* node structure.
  * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
  * @return int 
  */
static int get_node_h(Node *node, int board_size) {
    return get_heuristic(node->state, board_size);
}

/**
 * @brief Return the f cost of given node.
 * 
 * @param node An A* node structure.
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @return int 
 */
static int get_node_f(Node *node, int board_size) {
    return node->g + get_node_h(node, board_size);
}

/**
 * @brief Check if node matches the goal state, eg. {1, 2, 3, 4, 5, 6, 7, 8, 0} for 8-Puzzle.
 * 
 * @param node An A* node structure.
 * @param board_size The N-Puzzle board size, eg. 3 for an 8-Puzzle.
 * @return true 
 * @return false 
 */
static bool node_is_solved(Node *node, int board_size) {
    int board_length = to_board_length(board_size);

    for (int i = 0; i < board_length; i++) {
        if (node->state[i] != i + 1 && node->state[i] != 0) {
            return false;
        }
    }
    return true;
}

static int get_node_neighbors(Node *node, int board_size, Node *neighbors) {
    int board_length = to_board_length(board_size);
    int counter = 0;
    
    for (int i = 0; i < 4; i++) {
        int new_state[] = malloc(board_length * sizeof(int));
        if (new_state == NULL) {
            return counter;
        }

        for (int j = 0; j < board_length; j++) {
            new_state[j] = node->state[j];
        }
        
        if (move(new_state, board_size, i)) {
            neighbors[counter++] = (Node) {
                .state = new_state,
                .parent = node,
                .g = node->g + 1
            };
        } else {
            free(new_state);
        }

    return counter;
}

