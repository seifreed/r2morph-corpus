#include <stddef.h>

typedef int (*transform_fn)(int);

__attribute__((noinline)) static int add_three(int value) {
    return value + 3;
}

__attribute__((noinline)) static int double_value(int value) {
    return value * 2;
}

static transform_fn volatile transform_table[2] = {add_three, double_value};

static int parse_value(const char *text) {
    int sign = 1;
    int value = 0;
    if (*text == '-') {
        sign = -1;
        ++text;
    }
    while (*text >= '0' && *text <= '9') {
        value = value * 10 + (*text - '0');
        ++text;
    }
    return sign * value;
}

__attribute__((noinline)) static int dispatch(int value, size_t selector) {
    transform_fn function = transform_table[selector & 1U];
    return function(value);
}

int main(int argc, char **argv) {
    int value = argc > 1 ? parse_value(argv[1]) : 0;
    return dispatch(value, (size_t)value) & 127;
}
