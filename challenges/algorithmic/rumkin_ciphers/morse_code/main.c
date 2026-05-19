#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "morse.h"

const char *MODES[] = {
    "-e",
    "-encode",
    "-d",
    "-decode"
};

const int MODES_LENGTH = sizeof(MODES) / sizeof(MODES[0]);

bool valid_mode(char *mode) {
    for (int i = 0; i < MODES_LENGTH; i++) {
        if (strcmp(MODES[i], mode) == 0) {
            return true;
        }
    }

    assert(false && "Mode not found.");
    return false;
}

int main(int argc, char *argv[]) {
    if (argc <= 2) {
        printf("Usage: './main {-encode/-decode} {message}'.\n");
        printf("eg. ./main -encode \"Hello World\".\n");

        return 1;
    }

    if (!valid_mode(argv[1])) {
        printf("Invalid mode: %s", argv[1]);
        return 1;
    }

    if (strcmp(argv[1], "-e") == 0 || strcmp(argv[1], "-encode") == 0) {
        char *text = encode_morse(argv, argc);
        printf("%s\n", text);

        free(text);
    } else if (strcmp(argv[1], "-d") == 0 || strcmp(argv[1], "-decode") == 0) {
        char *text = decode_morse(argv, argc);
        printf("%s\n", text);

        free(text);
    }

    return 0;
}