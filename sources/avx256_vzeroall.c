#include <stdint.h>

__attribute__((noinline)) static int clear_all(int selector) {
    const uint32_t input[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    uint32_t output[8] = {0};
    __asm__ volatile(
        "vmovdqu (%0), %%ymm0\n"
        "vzeroall\n"
        "vmovdqu %%ymm0, (%1)\n"
        :
        : "r"(input), "r"(output), "r"(selector)
        : "ymm0", "memory"
    );
    return output[0] == 0 && output[4] == 0 ? 42 + selector : 1;
}

int main(int argc, char **argv) {
    return clear_all(argc > 1 ? 1 : 0);
}
