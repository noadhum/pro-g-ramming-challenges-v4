#ifndef MORSE
#define MORSE

/****************************************
* Functions
****************************************/

int get_prosign_idx(char *prosign);

char* encode_morse(char *arr[], int arr_size);
char* decode_morse(char *arr[], int arr_size);

#endif