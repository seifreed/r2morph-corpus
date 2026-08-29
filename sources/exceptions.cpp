#include <iostream>
#include <stdexcept>
#include <cstdlib>

static int recurse(int value) {
    if (value <= 1) return value;
    return recurse(value - 1) + recurse(value - 2);
}

__attribute__((noinline)) static int safe_arithmetic(int value) {
    return value * 3 + 1;
}

static int checked(int value) {
    if (value < 0) throw std::runtime_error("negative");
    return value * 3 + recurse(value % 5);
}

int main(int argc, char **argv) {
    try {
        int input = argc > 1 ? std::atoi(argv[1]) : 0;
        int values[] = {1 + input, 4, 7};
        int *cursor = values;
        int total = safe_arithmetic(input);
        for (int index = 0; index < 3; ++index) total += checked(cursor[index]);
        std::cout << total << "\n";
        return total & 0x7f;
    } catch (const std::exception &) {
        return 99;
    }
}
