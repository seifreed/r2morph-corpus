#include <immintrin.h>
#include <stdio.h>
#include <stdlib.h>

__attribute__((noinline)) static __m128 vector_square_root(__m128 value) {
    return _mm_sqrt_ps(value);
}

__attribute__((noinline)) static float scalar_square_root(float value) {
    return _mm_cvtss_f32(_mm_sqrt_ss(_mm_set_ss(value)));
}

static int compute(int input) {
    float root_base = (float)(input * input + 1);
    __m128 root_input = _mm_set_ps(root_base + 24.0f, root_base + 15.0f, root_base + 8.0f, root_base + 3.0f);
    __m128 root = vector_square_root(root_input);
    __m128 left = _mm_set_ps(9.0f, 7.0f, 5.0f, 20.0f);
    __m128 right = _mm_set_ps(-2.0f, 3.0f, 37.0f, 22.0f);
    __m128 offset = _mm_set1_ps(1.0f);
    __m128 result = _mm_add_ps(left, right);
    result = _mm_add_ps(result, root);
    result = _mm_min_ps(result, right);
    result = _mm_max_ps(result, left);
    result = _mm_sub_ps(result, offset);
    result = _mm_add_ps(result, offset);

    float lanes[4];
    _mm_storeu_ps(lanes, result);
    return (int)lanes[0] + (int)lanes[1] - (int)lanes[2] + (int)lanes[3] + (int)scalar_square_root(root_base) + input;
}

int main(int argc, char **argv) {
    int input = argc > 1 ? atoi(argv[1]) : 0;
    int result = compute(input);
    printf("%d\n", result);
    return result & 0x7f;
}
