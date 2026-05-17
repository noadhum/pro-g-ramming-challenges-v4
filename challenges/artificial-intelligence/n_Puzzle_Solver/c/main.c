#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "puzzle.h"

int main() {
    srand(time(NULL));

    int i = 0;
    int j = i++;

    printf("%d", j);

    return 0;
}