#ifndef MORSE_HEADER
#define MORSE_HEADER

//-----------------------------------------------
// Includes
//-----------------------------------------------

#include <string.h>

//-----------------------------------------------
// Types and Structures
//-----------------------------------------------

typedef struct {
    int arrSize;
    int arrStart;
    char **arr;
} Input;

typedef struct {
    char *data;
    size_t size;
    size_t capacity;
} ResultText;

//-----------------------------------------------
// Functions
//-----------------------------------------------

ResultText EncodeMorse(Input input);
ResultText DecodeMorse(Input input);

#endif