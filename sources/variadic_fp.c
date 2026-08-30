#include <stdarg.h>
#include <stdlib.h>

__attribute__((noinline)) static double sum_variadic_double(int count, ...) {
    va_list arguments;
    va_start(arguments, count);
    double total = 0.0;
    for (int index = 0; index < count; ++index) {
        total += va_arg(arguments, double);
    }
    va_end(arguments);
    return total;
}

int main(int argc, char **argv) {
    long input = argc > 1 ? strtol(argv[1], NULL, 10) : 0;
    double total = sum_variadic_double(
        10,
        (double)input,
        0.25,
        0.5,
        0.75,
        1.0,
        1.25,
        1.5,
        1.75,
        2.0,
        2.25
    );
    return ((int)(total * 4.0)) & 127;
}
