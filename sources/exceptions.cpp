#include <iostream>
#include <stdexcept>

static int recurse(int value) {
    if (value <= 1) return value;
    return recurse(value - 1) + recurse(value - 2);
}

static int checked(int value) {
    if (value < 0) throw std::runtime_error("negative");
    return value * 3 + recurse(value % 5);
}

int main() {
    try {
        int values[] = {1, 4, 7};
        int *cursor = values;
        int total = 0;
        for (int index = 0; index < 3; ++index) total += checked(cursor[index]);
        std::cout << total << "\n";
        return total & 0x7f;
    } catch (const std::exception &) {
        return 99;
    }
}
