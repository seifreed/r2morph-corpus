#include <stdlib.h>

__attribute__((noinline)) static long sum_ten(
    long first,
    long second,
    long third,
    long fourth,
    long fifth,
    long sixth,
    long seventh,
    long eighth,
    long ninth,
    long tenth
) {
    return first + second + third + fourth + fifth + sixth + seventh + eighth + ninth + tenth;
}

int main(int argc, char **argv) {
    long input = argc > 1 ? strtol(argv[1], NULL, 10) : 0;
    return (int)((unsigned long)sum_ten(input, 1, 2, 3, 4, 5, 6, 7, 8, 9) & 127UL);
}
