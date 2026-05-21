//-----------------------------------------------
// Includes
//-----------------------------------------------

#include <ctype.h>
#include <stdbool.h>
#include <string.h>

#include "strutils.h"

//-----------------------------------------------
// Functions
//-----------------------------------------------

void ToUppercase(const char *src, char *dest) {
    int index;
    for (index = 0; src[index] != '\0'; index++) {
        dest[index] = toupper((unsigned char) src[index]); 
    }

    dest[index] = '\0';
}

void ToLowercase(const char *src, char *dest) {
    int index;
    for (index = 0; src[index] != '\0'; index++) {
        dest[index] = tolower((unsigned char) src[index]);
    }

    dest[index] = '\0';
}

bool Match(const char *str, const char *const flags[]) {
    for (int index = 0; flags[index] != NULL; index++) {
        if (strcmp(flags[index], str) == 0) {
            return true;
        }
    }

    return false;
}