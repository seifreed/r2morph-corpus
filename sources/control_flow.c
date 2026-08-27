#include <stdio.h>
#include <stdlib.h>

static _Thread_local int tls_bias = 3;

static int recurse(int value) {
    if (value <= 1) return value;
    return recurse(value - 1) + recurse(value - 2);
}

static int select_value(int value) {
    switch (value % 4) {
        case 0: return value + 7;
        case 1: return value * 2;
        case 2: return value - 5;
        default: return value ^ 0x33;
    }
}

int main(int argc, char **argv) {
    int input = argc > 1 ? atoi(argv[1]) : 0;
    int values[] = {2 + input, 5 - input, 8 + input, 11 - input};
    int *cursor = values;
    int total = tls_bias;
    for (int index = 0; index < 4; ++index) {
        total += select_value(cursor[index]) + recurse(index + 3);
    }
    printf("%d\n", total);
    return total & 0x7f;
}
