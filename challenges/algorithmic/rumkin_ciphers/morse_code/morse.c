/**
 * @file morse.c
 * @brief A file containing morse code encoding/decoding logic.
 * 
 */

 /****************************************
  * Includes
  ****************************************/

#include <assert.h>
#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "morse.h"

/****************************************
* Types and Constants
****************************************/

typedef enum {
    CHARACTER,
    PROSIGN,
} MorseArray;

typedef struct {
    char character;
    char *morse;
} Character;

typedef struct {
    char *prosign;
    char *morse;
} Prosign;

const Character MORSE_CHARACTER_LOOKUP[] = {
    {'A', ".-"},
    {'B', "-..."},
    {'C', "-.-."},
    {'D', "-.."},
    {'E', "."},
    {'F', "..-."},
    {'G', "--."},
    {'H', "...."},
    {'I', ".."},
    {'J', ".---"},
    {'K', "-.-"},
    {'L', ".-.."},
    {'M', "--"},
    {'N', "-."},
    {'O', "---"},
    {'P', ".--."},
    {'Q', "--.-"},
    {'R', ".-."},
    {'S', "..."},
    {'T', "-"},
    {'U', "..-"},
    {'V', "...-"},
    {'W', ".--"},
    {'X', "-..-"},
    {'Y', "-.--"},
    {'Z', "--.."},
    {'0', "-----"},
    {'1', ".----"},
    {'2', "..---"},
    {'3', "...--"},
    {'4', "....-"},
    {'5', "....."},
    {'6', "-...."},
    {'7', "--..."},
    {'8', "---.."},
    {'9', "----."},
    {'.', ".-.-.-"},
    {',', "--..--"},
    {'?', "..--.."},
    {'\'', ".----."},
    {'!', "-.-.--"},
    {'/', "-..-."},
    {'(', "-.--."},
    {')', "-.--.-"},
    {'&', ".-..."},
    {':', "---..."},
    {';', "-.-.-."},
    {'=', "-...-"},
    {'-', "-....-"},
    {'+', ".-.-."},
    {'_', "..--.-"},
    {'"', ".-..-."},
    {'$', "...-..-"},
    {'@', ".--.-."},
    {' ', "/"}
};

const Prosign MORSE_PROSIGN_LOOKUP[] = {
    {"[CORRECT]", "-.-."},
    {"[AFFIRMATIVE]", "-.-."},
    {"[OVER]", "-.-"},
    {"[INVITE TO TRANSMIT]", "-.-"},
    {"[INVITATION TO TRANSMIT]", "-.-"},
    {"[NEGATIVE]", "-."},
    {"[ROGER]", ".-."},
    {"[REPEAT]", "..--.."},
    {"[PLEASE SAY AGAIN]", "..--.."},
    {"[INVITE NAMED STATION TO TRANSMIT]", "-.--."},
    {"[WAIT]", ".-..."},
    {"[NEW SECTION]", "-...-"},
    {"[NEW PARAGRAPH]", "-...-"},
    {"[BREAK]", "-...-"},
    {"[NEW PAGE]", ".-.-."},
    {"[OUT]", ".-.-."},
    {"[EOW]", "...-.-"},
    {"[END OF CONTACT]", "...-.-"},
    {"[END OF WORK]", "...-.-"},
    {"[END]", "...-.-"},
    {"[ERR]", "........"},
    {"[ERROR]", "........"},
    {"[CORRECTION]", "........"},
    {"[START]", "-.-.-"},
    {"[ATTENTION]", "-.-.-"},
    {"[UNKNOWN STATION]", ".-.-"},
    {"[NEW LINE]", ".-.-"},
    {"[UNDERSTOOD]", "...-."},
    {"[VERIFIED]", "...-."},
    {"[INT]", "..-.-"},
    {"[INTERROGATIVE]", "..-.-"},
    {"[SHIFT TO WABUN CODE]", "-..---"},
    {"[SOS]", "...---..."}
};

const int CHAR_LOOKUP_LENGTH = sizeof(MORSE_CHARACTER_LOOKUP) / sizeof(MORSE_CHARACTER_LOOKUP[0]);
const int PROSIGN_LOOKUP_LENGTH = sizeof(MORSE_PROSIGN_LOOKUP) / sizeof(MORSE_PROSIGN_LOOKUP[0]);

/****************************************
* Helper Function
****************************************/

/**
 * @brief Return the index of target character.
 * 
 * @param character The target character, eg. 'A', 'B'.
 * @return int 
 */
static int get_char_idx(char character) {
    for (int idx = 0; idx < CHAR_LOOKUP_LENGTH; idx++) {
        if (MORSE_CHARACTER_LOOKUP[idx].character == toupper(character)) {
            return idx;
        }
    }

    assert(false && "Character not found.");
    return -1;
}

static inline int is_prosign(char *text) {
    return text && text[0] == '[';
}

int get_prosign_idx(char *prosign) {
    if (!is_prosign(prosign)) {
        assert(false && "Invalid prodecural signal.");
    }

    for (int idx = 0; idx < PROSIGN_LOOKUP_LENGTH; idx++) {
        if (strcmp(MORSE_PROSIGN_LOOKUP[idx].prosign, prosign) == 0) {
            return idx;
        }
    }

    assert(false && "Prodecural signal not found.");
    return -1;
}

/**
 * @brief Return the index of target morse code.
 * 
 * @param morse The target morse code, eg. "-.-.", "-...", ".-".
 * @return int 
 */
static int get_char_morse_idx(char *morse) {
    for (int idx = 0; idx < CHAR_LOOKUP_LENGTH; idx++) {
        if (strcmp(MORSE_CHARACTER_LOOKUP[idx].morse, morse) == 0) {
            return idx;
        }
    }

    return -1;
}

static int get_prosign_morse_idx(char *morse) {
    for (int idx = 0; idx < PROSIGN_LOOKUP_LENGTH; idx++) {
        if (strcmp(MORSE_PROSIGN_LOOKUP[idx].morse, morse) == 0) {
            return idx;
        }
    }

    return -1;
}

/****************************************
* Main Functions
****************************************/

/**
 * @brief Encode the given array of strings to morse code.
 * 
 * @param arr An array containing strings, eg. {"Hello", "World"}.
 * @param arr_size The size of given array.
 * @return char* 
 */
char* encode_morse(char *arr[], int arr_size) {
    if (arr_size <= 2) {
        assert(false && "Array length should be more than 2.");
        return NULL;
    }

    char *morse_text = malloc(2048); 
    char *text_pointer = morse_text;
    *text_pointer = '\0';

    for (int arg_idx = 2; arg_idx < arr_size; arg_idx++) {
        int arg_length = strlen(arr[arg_idx]);
        char *current_arg = arr[arg_idx];

        for (int char_idx = 0; char_idx < arg_length; char_idx++) {
            char current_char = arr[arg_idx][char_idx];
            char *seperator;

            if (char_idx != arg_length - 1 || arg_idx == arr_size - 1) {
                seperator = " ";
            } else {
                seperator = " / ";
            }

            if (char_idx == 0 && is_prosign(current_arg)) {
                char *morse = MORSE_PROSIGN_LOOKUP[get_prosign_idx(current_arg)].morse;
                text_pointer += sprintf(text_pointer, "%s%s", morse, seperator);
                break;
            } else {
                char *morse = MORSE_CHARACTER_LOOKUP[get_char_idx(current_char)].morse;
                text_pointer += sprintf(text_pointer, "%s%s", morse, seperator);
            }
        }
    }

    return morse_text;
}

/**
 * @brief Decode the given array of morse code to text.
 * 
 * @param arr An array containing morse codes, eg. {".----", "....-", "...--"}.
 * @param arr_size The size of given array.
 * @return char* 
 */
char* decode_morse(char *arr[], int arr_size) {
    if (arr_size <= 2) {
        assert(false && "Array length should be more than 2.");
        return NULL;
    }

    char *text = malloc(2048);
    char *text_pointer = text;
    *text_pointer = '\0';

    for (int arg_idx = 0; arg_idx < arr_size; arg_idx++) {
        char *current_morse = arr[arg_idx];

        bool found = false;
        int morse_array = -1;
        int morse_idx = -1;

        morse_idx = get_char_morse_idx(current_morse);
        if (morse_idx > -1) {
            morse_array = CHARACTER;
            found = true;
        }

        if (!found) {
            morse_idx = get_prosign_morse_idx(current_morse);
            if (morse_idx > -1) {
                morse_array = PROSIGN;
                found = true;
            }
        }

        if (found) {
            if (morse_array == CHARACTER) {
                text_pointer += sprintf(text_pointer, "%c", MORSE_CHARACTER_LOOKUP[morse_idx].character);
            } else if (morse_array == PROSIGN) {
                text_pointer += sprintf(text_pointer, "%s", MORSE_PROSIGN_LOOKUP[morse_idx].prosign);
            }
        } else {
            assert(false && "Invalid morse code, Please put real morse code.");
        }
    }

    return text;
}