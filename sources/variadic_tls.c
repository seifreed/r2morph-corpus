#include <stdarg.h>
#include <stddef.h>

static _Thread_local volatile unsigned long tls_values[4] = {5UL, 7UL, 11UL, 13UL};

__attribute__((noinline)) static double sum_variadic_fp(int count, ...) {
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
    size_t index = argc > 1 ? (size_t)argv[1][0] & 3U : 1U;
    tls_values[index] = 7UL;
    int result = (int)sum_variadic_fp(3, 1.0, 2.0, 3.0);
    return (result + (int)tls_values[index]) & 127;
}
