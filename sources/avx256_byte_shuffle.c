#include <stdint.h>

typedef uint8_t vector128 __attribute__((vector_size(16)));
typedef uint8_t vector256 __attribute__((vector_size(32)));

__attribute__((noinline)) static vector128 shuffle128(vector128 value, vector128 mask) {
    vector128 result;
    __asm__ volatile("vpshufb %2, %1, %0" : "=x"(result) : "x"(value), "x"(mask));
    return result;
}

__attribute__((noinline)) static vector256 shuffle256(vector256 value, vector256 mask) {
    vector256 result;
    __asm__ volatile("vpshufb %2, %1, %0" : "=x"(result) : "x"(value), "x"(mask));
    return result;
}

int main(int argc, char **argv) {
    const vector128 value128 = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    const vector128 mask128 = {15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0};
    const vector256 value256 = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                                17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32};
    const vector256 mask256 = {15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0,
                               15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0};
    const vector128 result128 = shuffle128(value128, mask128);
    const vector256 result256 = shuffle256(value256, mask256);
    return result128[0] == 16 && result128[15] == 1
            && result256[0] == 16 && result256[15] == 1
            && result256[16] == 32 && result256[31] == 17
        ? 42 + (argc > 1 ? 1 : 0)
        : 1;
}
