#include <stdio.h>
#include <stdlib.h>

typedef float vector_float __attribute__((vector_size(16)));
typedef double vector_double __attribute__((vector_size(16)));

__attribute__((noinline)) static vector_float add_single(vector_float left, vector_float right) {
    vector_float result;
    __asm__ volatile("vaddss %1, %2, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

__attribute__((noinline)) static vector_double add_double(vector_double left, vector_double right) {
    vector_double result;
    __asm__ volatile("vaddsd %1, %2, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

static int compute(int input) {
    vector_float single = add_single((vector_float){20.0f + input, 5.0f, 7.0f, 9.0f},
                                     (vector_float){22.0f, 37.0f, 3.0f, 4.0f});
    vector_double double_value = add_double((vector_double){20.0 + input, 5.0}, (vector_double){22.0, 37.0});
    return (int)single[0] + (int)single[1] - (int)single[2] + (int)single[3]
        + (int)double_value[0] - (int)double_value[1] + input;
}

int main(int argc, char **argv) {
    int input = argc > 1 ? atoi(argv[1]) : 0;
    int result = compute(input);
    printf("%d\n", result);
    return result & 0x7f;
}
