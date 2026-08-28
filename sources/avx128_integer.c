#include <immintrin.h>
#include <stdio.h>
#include <stdlib.h>

static int compute(int input) {
    __m128i left = _mm_set_epi32(input + 4, input + 3, input + 2, input + 1);
    __m128i right = _mm_set_epi32(40, 30, 20, 10);
    __m128i result = _mm_add_epi32(left, right);
    result = _mm_sub_epi32(result, right);
    result = _mm_mullo_epi32(result, right);
    result = _mm_min_epi32(result, right);
    result = _mm_max_epi32(result, left);
    result = _mm_cmpeq_epi32(result, left);
    result = _mm_adds_epu8(result, _mm_set1_epi8(1));
    result = _mm_packus_epi16(result, right);
    result = _mm_unpacklo_epi8(result, right);

    int lanes[4];
    _mm_storeu_si128((__m128i *)lanes, result);
    return lanes[0] + lanes[1] - lanes[2] + lanes[3] + input;
}

int main(int argc, char **argv) {
    int input = argc > 1 ? atoi(argv[1]) : 0;
    int result = compute(input);
    printf("%d\n", result);
    return result & 0x7f;
}
