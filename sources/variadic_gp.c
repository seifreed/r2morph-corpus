#include <stdarg.h>
#include <stdlib.h>

__attribute__((noinline)) static long sum_variadic_long(int count, ...) {
    va_list arguments;
    va_start(arguments, count);
    long total = 0;
    for (int index = 0; index < count; ++index) {
        total += va_arg(arguments, long);
    }
    va_end(arguments);
    return total;
}

int main(int argc, char **argv) {
    long input = argc > 1 ? strtol(argv[1], NULL, 10) : 0;
    long total = sum_variadic_long(10, input, 1L, 2L, 3L, 4L, 5L, 6L, 7L, 8L, 9L);
    return (int)((unsigned long)total & 127UL);
}
