#include <stdio.h>
#include <stdlib.h>

typedef float vector256 __attribute__((vector_size(32)));

__attribute__((noinline)) static vector256 add256(vector256 left, vector256 right) {
    return left + right;
}

static int compute(int input) {
    vector256 left = {1.0f + input, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
    vector256 right = {8.0f, 7.0f, 6.0f, 5.0f, 4.0f, 3.0f, 2.0f, 1.0f};
    vector256 result = add256(left, right);
    float lanes[8];
    __builtin_memcpy(lanes, &result, sizeof(result));
    return (int)lanes[0] + (int)lanes[1] - (int)lanes[2] + (int)lanes[7] + input;
}

int main(int argc, char **argv) {
    int input = argc > 1 ? atoi(argv[1]) : 0;
    int result = compute(input);
    printf("%d\n", result);
    return result & 0x7f;
}
