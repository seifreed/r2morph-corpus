#include <stdint.h>
#include <stdlib.h>

__attribute__((noinline)) static uint32_t mask128_legacy(const uint8_t *source) {
    uint32_t result;
    __asm__ volatile(
        "vmovdqu (%1), %%xmm0\n"
        "pmovmskb %%xmm0, %0\n"
        : "=r"(result)
        : "r"(source)
        : "xmm0", "memory");
    return result;
}

__attribute__((noinline)) static uint32_t mask128_vex(const uint8_t *source) {
    uint32_t result;
    __asm__ volatile(
        "vmovdqu (%1), %%xmm0\n"
        "vpmovmskb %%xmm0, %0\n"
        : "=r"(result)
        : "r"(source)
        : "xmm0", "memory");
    return result;
}

__attribute__((noinline)) static uint32_t mask256_vex(const uint8_t *source) {
    uint32_t result;
    __asm__ volatile(
        "vmovdqu (%1), %%ymm0\n"
        "vpmovmskb %%ymm0, %0\n"
        : "=r"(result)
        : "r"(source)
        : "ymm0", "memory");
    return result;
}

int main(int argc, char **argv) {
    const unsigned input = (unsigned)(argc > 1 ? atoi(argv[1]) : 0);
    uint8_t values128[16] = {0};
    uint8_t values256[32] = {0};
    values128[input & 15U] = 0x80U;
    values256[input & 31U] = 0x80U;
    const uint32_t result = mask128_legacy(values128) ^ mask128_vex(values128) ^ mask256_vex(values256);
    return (int)(result & 0x7fU);
}
