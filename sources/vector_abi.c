#include <stdio.h>
#include <stdlib.h>

typedef int vector4 __attribute__((vector_size(16)));
typedef int (*unary_function)(int);

static int increment(int value) {
    return value + 1;
}

static int invoke(unary_function function, int value) {
    return function(value);
}

int main(int argc, char **argv) {
    int input = argc > 1 ? atoi(argv[1]) : 0;
    vector4 left = {input, 2, -3, 4};
    vector4 right = {1, 3, 5, -2};
    vector4 sum = left + right;
    int total = sum[0] + sum[1] - sum[2] + sum[3];

    total += invoke(increment, input);
    printf("%d\n", total);
    return total & 0x7f;
}
