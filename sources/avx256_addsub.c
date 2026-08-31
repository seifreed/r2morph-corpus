#include <immintrin.h>

__attribute__((noinline)) static __m256 addsub_float(__m256 left, __m256 right) {
    return _mm256_addsub_ps(left, right);
}

__attribute__((noinline)) static __m256d addsub_double(__m256d left, __m256d right) {
    return _mm256_addsub_pd(left, right);
}

int main(void) {
    const __m256 float_left = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
    const __m256 float_right = {10.0f, 20.0f, 30.0f, 40.0f, 50.0f, 60.0f, 70.0f, 80.0f};
    const __m256d double_left = {1.0, 2.0, 3.0, 4.0};
    const __m256d double_right = {10.0, 20.0, 30.0, 40.0};
    const __m256 float_result = addsub_float(float_left, float_right);
    const __m256d double_result = addsub_double(double_left, double_right);
    return float_result[0] == 11.0f && float_result[1] == -18.0f
        && float_result[6] == 77.0f && float_result[7] == -72.0f
        && double_result[0] == 11.0 && double_result[1] == -18.0
        && double_result[2] == 33.0 && double_result[3] == -36.0 ? 42 : 1;
}
