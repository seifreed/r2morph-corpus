#include <stdint.h>

__attribute__((noinline)) static int clear_upper(int selector) {
    const uint32_t input[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    uint32_t output[8] = {0};
    __asm__ volatile(
        "vmovdqu (%0), %%ymm0\n"
        "vzeroupper\n"
        "vmovdqu %%ymm0, (%1)\n"
        :
        : "r"(input), "r"(output), "r"(selector)
        : "ymm0", "memory"
    );
    return (int)(output[0] + output[4] + (uint32_t)selector);
}

int main(int argc, char **argv) {
    return clear_upper(argc > 1 ? 1 : 0) & 127;
}
