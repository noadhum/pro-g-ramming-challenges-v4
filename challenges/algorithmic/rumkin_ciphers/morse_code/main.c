#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "strutils.h"
#include "morse.h"

//-----------------------------------------------
// Macros
//-----------------------------------------------

#define MODE_INDEX 1
#define ARR_SIZE 2

//-----------------------------------------------
// Types
//-----------------------------------------------

typedef enum {
    HELP,
    ENCODE,
    DECODE,
    MORSE
} Mode;

typedef enum {
    SUCCESS = 0,
    FAILURE = 1,
    INVALID_INPUT = 2,
    INVALID_FLAGS = 3,
} StatusCode;

typedef struct {
    StatusCode statusCode;
    char *name;
    char *description;
    char *suggestion;
} ErrorInfo;

typedef struct {
    bool help;
    bool encode;
    bool decode;
    bool morse;
} Flags;

typedef struct {
    Mode mode;
    const char *flags[3];
    char *description;
} FlagInfo;

//-----------------------------------------------
// Constants
//-----------------------------------------------

const char ERROR_MESSAGE[] = "[ERROR: %s] %s \n%s\n";
char USAGE_TEMPLATE[] = "Usage: './main {mode} {codecType} {input}'\nExample: './main --encode --morse Hello World'";
char FLAG_PRINT_TEMPLATE[] = "%-4s %-12s %s\n";

const ErrorInfo ERRORS_ARR[] = {
    {
        FAILURE,
        "FAILURE",
        "Oops, something went wrong.",
        "Please try again later."
    },
    {
        INVALID_INPUT,
        "INVALID_INPUT",
        "The given input is NULL or invalid.",
        USAGE_TEMPLATE
    },
    {
        INVALID_FLAGS,
        "INVALID_FLAGS",
        "The given flag is invalid.",
        USAGE_TEMPLATE
    }

};

const FlagInfo FLAGS_ARR[] = {
    {HELP, {"-h", "--help", NULL}, "Open the help page."},
    {ENCODE, {"-e", "--encode", NULL}, "Encode given input into ['Morse']."},
    {DECODE, {"-d", "--decode", NULL}, "Decode given input into text."},
    {MORSE, {"-m", "--morse", NULL}, "A flag represents morse code mode."}
};

const int ERROR_ARR_LENGTH = sizeof(ERRORS_ARR) / sizeof(ERRORS_ARR[0]);
const int FLAGS_ARR_LENGTH = sizeof(FLAGS_ARR) / sizeof(FLAGS_ARR[0]);

//-----------------------------------------------
// Functions
//-----------------------------------------------

void PrintHelp() {
    printf("[HELP]:\n\n");
    printf("Flags:\n");

    for (int index = 0; index < FLAGS_ARR_LENGTH; index++) {
        FlagInfo currentFlag = FLAGS_ARR[index];
        printf
        (
            FLAG_PRINT_TEMPLATE,
            currentFlag.flags[0],
            currentFlag.flags[1],
            currentFlag.description
        );
    }

    printf("%s\n\n", USAGE_TEMPLATE);
}

void PrintErrorMessage(StatusCode errorType) {
    for (int index = 0; index < ERROR_ARR_LENGTH; index++) {
        ErrorInfo error = ERRORS_ARR[index];

        if (errorType == error.statusCode) {
            fprintf(
                stderr,
                ERROR_MESSAGE,
                error.name,
                error.description,
                error.suggestion
            );
            return;
        }
    }

    ErrorInfo failure = ERRORS_ARR[FAILURE];
    fprintf(
        stderr,
        ERROR_MESSAGE,
        failure.name,
        failure.description,
        failure.suggestion
    );
}

Flags GetFlags(int argc, char *argv[]) {
    Flags flags = {false};

    char *mode = (argc > MODE_INDEX) ? argv[MODE_INDEX] : NULL;
    char *codecType = (argc > ARR_SIZE) ? argv[ARR_SIZE] : NULL;

    if (mode && Match(mode, FLAGS_ARR[HELP].flags)) {
        flags.help = true;
    }

    if (mode && Match(mode, FLAGS_ARR[ENCODE].flags)) {
        flags.encode = true;
    }

    if (mode && Match(mode, FLAGS_ARR[DECODE].flags)) {
        flags.decode = true;
    }

    if (codecType && Match(codecType, FLAGS_ARR[MORSE].flags)) {
        flags.morse = true;
    }

    return flags;
}

//-----------------------------------------------

int main(int argc, char *argv[]) {
    if (argc < ARR_SIZE) {
        PrintErrorMessage(INVALID_INPUT);
        return INVALID_INPUT;
    }

    Flags flags = GetFlags(argc, argv);

    if (flags.help) {
        PrintHelp();
        return SUCCESS;

    } else if (flags.encode && flags.morse) {
        Input input = {argc, ARR_SIZE, argv};
        ResultText result = EncodeMorse(input);

        free(result.data);
        return SUCCESS;

    } else if (flags.decode && flags.morse) {
        Input input = {argc, ARR_SIZE, argv};
        ResultText result = DecodeMorse(input);

        free(result.data);
        return SUCCESS;

    } else {
        PrintErrorMessage(INVALID_FLAGS);
        return INVALID_FLAGS;
    }

    PrintErrorMessage(FAILURE);
    return FAILURE;
}