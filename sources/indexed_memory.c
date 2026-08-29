#include <stddef.h>

static const unsigned long values[4] = {5UL, 7UL, 11UL, 13UL};
static volatile unsigned long scratch[4];

__attribute__((noinline)) static unsigned long load_value(size_t index) {
    return values[index & 3U];
}

__attribute__((noinline)) static unsigned long store_value(size_t index) {
    scratch[index & 3U] = values[2];
    return scratch[0];
}

int main(int argc, char **argv) {
    size_t index = argc > 1 ? (size_t)argv[1][0] : 1U;
    unsigned long loaded = load_value(index);
    unsigned long stored = store_value(index);
    return (int)((loaded + stored) & 127U);
}
