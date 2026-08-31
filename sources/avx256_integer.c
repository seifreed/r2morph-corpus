#include <stdint.h>

__attribute__((noinline)) static void shift256(
    const int32_t *values,
    const uint32_t *counts,
    int32_t *left,
    uint32_t *logical,
    int32_t *arithmetic,
    int32_t *immediate_left,
    int32_t *immediate_arithmetic
) {
    __asm__ volatile(
        "vmovdqu (%0), %%ymm1\n"
        "vmovdqu (%1), %%ymm2\n"
        "vpsllvd %%ymm2, %%ymm1, %%ymm0\n"
        "vpsrlvd %%ymm2, %%ymm1, %%ymm3\n"
        "vpsravd %%ymm2, %%ymm1, %%ymm4\n"
        "vmovdqu %%ymm0, (%2)\n"
        "vmovdqu %%ymm3, (%3)\n"
        "vmovdqu %%ymm4, (%4)\n"
        "vpslld $1, %%ymm1, %%ymm3\n"
        "vpsrad $1, %%ymm1, %%ymm4\n"
        "vmovdqu %%ymm3, (%5)\n"
        "vmovdqu %%ymm4, (%6)\n"
        :
        : "r"(values), "r"(counts), "r"(left), "r"(logical), "r"(arithmetic),
          "r"(immediate_left), "r"(immediate_arithmetic)
        : "ymm0", "ymm1", "ymm2", "ymm3", "ymm4", "memory"
    );
}

int main(void) {
    const int32_t values[8] = {1, -2, 3, -4, 5, -6, 7, -8};
    const uint32_t counts[8] = {1, 1, 1, 1, 1, 1, 1, 1};
    int32_t left[8] = {0};
    uint32_t logical[8] = {0};
    int32_t arithmetic[8] = {0};
    int32_t immediate_left[8] = {0};
    int32_t immediate_arithmetic[8] = {0};
    shift256(values, counts, left, logical, arithmetic, immediate_left, immediate_arithmetic);
    return left[0] == 2 && left[7] == -16 && logical[1] == 2147483647U && arithmetic[1] == -1 &&
                   immediate_left[0] == 2 && immediate_left[7] == -16 && immediate_arithmetic[1] == -1
               ? 42
               : 1;
}
