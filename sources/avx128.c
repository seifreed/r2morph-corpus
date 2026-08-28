#include <immintrin.h>
#include <stdio.h>
#include <stdlib.h>

static int compute(int input) {
    __m128 left = _mm_set_ps(9.0f, 7.0f, 5.0f, 20.0f);
    __m128 right = _mm_set_ps(-2.0f, 3.0f, 37.0f, 22.0f);
    __m128 offset = _mm_set1_ps(1.0f);
    __m128 result = _mm_add_ps(left, right);
    result = _mm_min_ps(result, right);
    result = _mm_max_ps(result, left);
    result = _mm_sub_ps(result, offset);
    result = _mm_add_ps(result, offset);

    float lanes[4];
    _mm_storeu_ps(lanes, result);
    return (int)lanes[0] + (int)lanes[1] - (int)lanes[2] + (int)lanes[3] + input;
}

int main(int argc, char **argv) {
    int input = argc > 1 ? atoi(argv[1]) : 0;
    int result = compute(input);
    printf("%d\n", result);
    return result & 0x7f;
}
