#include <immintrin.h>

__attribute__((noinline)) static __m256 permute_float(__m256 value, __m256i controls) {
    return _mm256_permutevar_ps(value, controls);
}

__attribute__((noinline)) static __m256d permute_double(__m256d value, __m256i controls) {
    return _mm256_permutevar_pd(value, controls);
}

int main(void) {
    const __m256 float_value = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
    const __m256i float_controls = _mm256_set_epi32(3, 2, 1, 0, 0, 1, 2, 3);
    const __m256d double_value = {1.0, 2.0, 3.0, 4.0};
    const __m256i double_controls = _mm256_set_epi64x(0, 2, 0, 2);
    const __m256 float_result = permute_float(float_value, float_controls);
    const __m256d double_result = permute_double(double_value, double_controls);
    return float_result[0] == 4.0f && float_result[3] == 1.0f
        && float_result[4] == 5.0f && float_result[7] == 8.0f
        && double_result[0] == 2.0 && double_result[1] == 1.0
        && double_result[2] == 4.0 && double_result[3] == 3.0 ? 42 : 1;
}
