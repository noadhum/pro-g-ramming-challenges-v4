/**
 * @file morse.c
 * @brief A file containing morse code encoding/decoding logic.
 * 
 */

//-----------------------------------------------
// Includes
//-----------------------------------------------

#include <assert.h>
#include <ctype.h>
#include <stdbool.h>
#include <stdlib.h>

#include "morse.h"
#include "strutils.h"

//-----------------------------------------------
// Macros
//-----------------------------------------------

#define MAX_STR_BUFFER_SIZE 137

//-----------------------------------------------
// Types and Structures
//-----------------------------------------------

typedef struct {
    const char *key;
    const char *morse;
} Morse;

//-----------------------------------------------
// Constants
//-----------------------------------------------

const Morse MORSE_LOOKUP[] = {
    {"A", ".-"},
    {"B", "-..."},
    {"C", "-.-."},
    {"D", "-.."},
    {"E", "."},
    {"F", "..-."},
    {"G", "--."},
    {"H", "...."},
    {"I", ".."},
    {"J", ".---"},
    {"K", "-.-"},
    {"L", ".-.."},
    {"M", "--"},
    {"N", "-."},
    {"O", "---"},
    {"P", ".--."},
    {"Q", "--.-"},
    {"R", ".-."},
    {"S", "..."},
    {"T", "-"},
    {"U", "..-"},
    {"V", "...-"},
    {"W", ".--"},
    {"X", "-..-"},
    {"Y", "-.--"},
    {"Z", "--.."},

    {"0", "-----"},
    {"1", ".----"},
    {"2", "..---"},
    {"3", "...--"},
    {"4", "....-"},
    {"5", "....."},
    {"6", "-...."},
    {"7", "--..."},
    {"8", "---.."},
    {"9", "----."},

    {".", ".-.-.-"},
    {",", "--..--"},
    {"?", "..--.."},
    {"'", ".----."},
    {"!", "-.-.--"},
    {"/", "-..-."},
    {"(", "-.--."},
    {")", "-.--.-"},
    {"&", ".-..."},
    {":", "---..."},
    {";", "-.-.-."},
    {"=", "-...-"},
    {"-", "-....-"},
    {"+", ".-.-."},
    {"_", "..--.-"},
    {"\"", ".-..-."},
    {"$", "...-..-"},
    {"@", ".--.-."},
    {" ", "/"},
    
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

const int LOOKUP_LENGTH = sizeof(MORSE_LOOKUP) / sizeof(MORSE_LOOKUP[0]);

//-----------------------------------------------
// Helper Functions
//-----------------------------------------------

static ResultText TextInit() {
    size_t initCapacity = 16;

    char *textData = malloc(initCapacity);
    textData[0] = '\0';

    return (ResultText) {
        .data = textData,
        .size = 0,
        .capacity = initCapacity
    };
}

static void TextResize(ResultText *text) {
    void *temp = realloc(text->data, text->capacity * 2);
    if (temp != NULL) {
        text->data = temp;
        text->capacity *= 2;
    }
}

static void TextAppend(ResultText *text, const char *str, const char *separator)
{
    size_t itemLength = strlen(str);
    size_t seperatorLength = strlen(separator);
    size_t totalLength = itemLength + seperatorLength;

    while (text->size + totalLength + 1 > text->capacity) {
        TextResize(text);
    }

    memcpy(text->data + text->size, str, itemLength);
    text->size += itemLength;

    memcpy(text->data + text->size, separator, seperatorLength);
    text->size += seperatorLength;

    text->data[text->size] = '\0';
}

//-----------------------------------------------

static int IsProsign(const char *str) {
    return (str[0] == '[');
}

//-----------------------------------------------

static const char* ToMorse(const char *str) {
    if (str[0] == '\0') {
        assert(false && "Invalid str.");
        return NULL;
    }

    char uppercaseBuffer[MAX_STR_BUFFER_SIZE];
    ToUppercase(str, uppercaseBuffer);

    for (int index = 0; index < LOOKUP_LENGTH; index++) {
        if (strcmp(MORSE_LOOKUP[index].key, uppercaseBuffer) == 0) {
            return MORSE_LOOKUP[index].morse;
        }
    }

    assert(false && "Character or procedural signal not found.");
    return NULL;
}

static const char* ToText(const char* str) {
    if (str[0] == '\0') {
        assert(false && "Invalid str.");
        return NULL;
    }

    for (int index = 0; index < LOOKUP_LENGTH; index++) {
        if (strcmp(MORSE_LOOKUP[index].morse, str) == 0) {

        }
    }

    assert(false && "Morse code not found.");
    return NULL;
}

//-----------------------------------------------
// Main Functions
//-----------------------------------------------

ResultText EncodeMorse(Input input) {
    if (input.arrSize < 1) {
        assert(false && "Invalid array size.");
    }

    ResultText text = TextInit();

    for (int arrIndex = input.arrStart; arrIndex < input.arrSize; arrIndex++) {
        char *currentWord = input.arr[arrIndex];
        int wordLength = strlen(currentWord);

        for (int letterIndex = 0; letterIndex < wordLength; letterIndex++) {
            char currentLetter = currentWord[letterIndex];

            char *separator = (
                letterIndex != wordLength - 1 ||
                arrIndex == input.arrSize - 1) ? " " : " / ";

            if (letterIndex == 0 && IsProsign(currentWord)) {
                TextAppend(&text, ToMorse(currentWord), separator);
                break;
            } else {
                char letter[] = {currentLetter, '\0'};
                TextAppend(&text, ToMorse(letter), separator);
            }
        }
    }

    return text;
}

ResultText DecodeMorse(Input input) {
    if (input.arrSize < 1) {
        assert(false && "Invalid array size.");
    }

    ResultText text = TextInit();

    for (int arrIndex = 0; arrIndex < input.arrSize; arrIndex++) {
        char *currentMorse = input.arr[arrIndex];

        TextAppend(&text, ToText(currentMorse), "");
    }   

    return text;
}