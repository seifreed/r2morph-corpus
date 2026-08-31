#include <immintrin.h>
#include <stdint.h>
#include <stdlib.h>

__attribute__((noinline)) static uint32_t shift128(int input) {
    const uint32_t values[4] = {1U + (uint32_t)input, 2U, 3U, 4U};
    const uint32_t counts[4] = {(uint32_t)input & 31U, 1U, 2U, 3U};
    const __m128i value_vector = _mm_loadu_si128((const __m128i *)values);
    const __m128i count_vector = _mm_loadu_si128((const __m128i *)counts);
    const __m128i result = _mm_sllv_epi32(value_vector, count_vector);
    uint32_t output[4];
    _mm_storeu_si128((__m128i *)output, result);
    return output[0] ^ output[1] ^ output[2] ^ output[3];
}

__attribute__((noinline)) static uint32_t shift256(int input) {
    const uint32_t values[8] = {1U + (uint32_t)input, 2U, 3U, 4U, 5U, 6U, 7U, 8U};
    const uint32_t counts[8] = {(uint32_t)input & 31U, 1U, 2U, 3U, 4U, 5U, 6U, 7U};
    const __m256i value_vector = _mm256_loadu_si256((const __m256i *)values);
    const __m256i count_vector = _mm256_loadu_si256((const __m256i *)counts);
    const __m256i result = _mm256_sllv_epi32(value_vector, count_vector);
    uint32_t output[8];
    _mm256_storeu_si256((__m256i *)output, result);
    return output[0] ^ output[1] ^ output[2] ^ output[3] ^ output[4] ^ output[5] ^ output[6] ^ output[7];
}

int main(int argc, char **argv) {
    const int input = argc > 1 ? atoi(argv[1]) : 0;
    return (int)((shift128(input) ^ shift256(input)) & 0x7fU);
}
