#include <stdint.h>

__attribute__((noinline)) static int mixed_state(int selector) {
    const uint32_t input[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    uint32_t output[8] = {0};
    __asm__ volatile(
        "vmovdqu (%0), %%ymm0\n"
        "vpxor %%ymm1, %%ymm1, %%ymm1\n"
        "vpxor %%xmm0, %%xmm0, %%xmm0\n"
        "vpxor %%ymm0, %%ymm1, %%ymm2\n"
        "vmovdqu %%ymm2, (%1)\n"
        :
        : "r"(input), "r"(output), "r"(selector)
        : "ymm0", "ymm1", "ymm2", "memory"
    );
    return output[0] == 0 && output[4] == 0 && output[7] == 0 ? 42 + selector : 1;
}

int main(int argc, char **argv) {
    return mixed_state(argc > 1 ? 1 : 0);
}
