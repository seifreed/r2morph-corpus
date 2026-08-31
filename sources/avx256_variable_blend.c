#include <immintrin.h>

__attribute__((noinline)) static __m256 blend_float(__m256 left, __m256 right, __m256 mask) {
    return _mm256_blendv_ps(left, right, mask);
}

__attribute__((noinline)) static __m256d blend_double(__m256d left, __m256d right, __m256d mask) {
    return _mm256_blendv_pd(left, right, mask);
}

int main(void) {
    const __m256 float_left = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
    const __m256 float_right = {11.0f, 12.0f, 13.0f, 14.0f, 15.0f, 16.0f, 17.0f, 18.0f};
    const __m256 float_mask = {-1.0f, 0.0f, -1.0f, 0.0f, -1.0f, 0.0f, -1.0f, 0.0f};
    const __m256d double_left = {1.0, 2.0, 3.0, 4.0};
    const __m256d double_right = {11.0, 12.0, 13.0, 14.0};
    const __m256d double_mask = {-1.0, 0.0, -1.0, 0.0};
    const __m256 float_result = blend_float(float_left, float_right, float_mask);
    const __m256d double_result = blend_double(double_left, double_right, double_mask);
    return float_result[0] == 11.0f && float_result[1] == 2.0f
        && float_result[6] == 17.0f && float_result[7] == 8.0f
        && double_result[0] == 11.0 && double_result[1] == 2.0
        && double_result[2] == 13.0 && double_result[3] == 4.0 ? 42 : 1;
}
