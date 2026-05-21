#ifndef STRUTILS_HEADER
#define STRUTILS_HEADER

//-----------------------------------------------
// Functions
//-----------------------------------------------

void ToUppercase(const char *src, char *dest);
void ToLowercase(const char *src, char *dest);
bool Match(const char *str, const char *const flags[]);

#endif