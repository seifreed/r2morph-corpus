#include <stdint.h>

__attribute__((noinline)) static int shuffle_256(int selector) {
    const uint32_t input[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    uint32_t output[8] = {0};
    __asm__ volatile(
        "vmovdqu (%0), %%ymm0\n"
        "vpshufd $0x1b, %%ymm0, %%ymm1\n"
        "vmovdqu %%ymm1, (%1)\n"
        :
        : "r"(input), "r"(output), "r"(selector)
        : "ymm0", "ymm1", "memory"
    );
    return output[0] == 4 && output[1] == 3 && output[2] == 2 && output[3] == 1 &&
                   output[4] == 8 && output[5] == 7 && output[6] == 6 && output[7] == 5
               ? 42 + selector
               : 1;
}

int main(int argc, char **argv) {
    return shuffle_256(argc > 1 ? 1 : 0);
}
