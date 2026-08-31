#include <immintrin.h>

__attribute__((noinline)) static __m128 compare_float128(__m128 left, __m128 right) {
    return _mm_cmp_ps(left, right, _CMP_EQ_OQ);
}

__attribute__((noinline)) static __m128d compare_double128(__m128d left, __m128d right) {
    return _mm_cmp_pd(left, right, _CMP_GT_OQ);
}

__attribute__((noinline)) static __m256 compare_float256(__m256 left, __m256 right) {
    return _mm256_cmp_ps(left, right, _CMP_EQ_OQ);
}

__attribute__((noinline)) static __m256d compare_double256(__m256d left, __m256d right) {
    return _mm256_cmp_pd(left, right, _CMP_GT_OQ);
}

__attribute__((noinline)) static __m256 compare_float_memory(__m256 left, const float *right) {
    return _mm256_cmp_ps(left, _mm256_loadu_ps(right), _CMP_EQ_OQ);
}

__attribute__((noinline)) static int test_float128(__m128 left, __m128 right) {
    return _mm_testz_ps(left, right);
}

__attribute__((noinline)) static int test_double128(__m128d left, __m128d right) {
    return _mm_testc_pd(left, right);
}

__attribute__((noinline)) static int test_float256(__m256 left, __m256 right) {
    return _mm256_testz_ps(left, right);
}

__attribute__((noinline)) static int test_double256(__m256d left, __m256d right) {
    return _mm256_testc_pd(left, right);
}

int main(void) {
    const __m128 float128_left = {1.0f, 2.0f, 3.0f, 4.0f};
    const __m128 float128_right = {1.0f, 3.0f, 3.0f, 5.0f};
    const __m128d double128_left = {1.0, 4.0};
    const __m128d double128_right = {0.0, 3.0};
    const __m256 float256_left = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
    const __m256 float256_right = {1.0f, 3.0f, 3.0f, 5.0f, 5.0f, 7.0f, 7.0f, 9.0f};
    const __m256d double256_left = {1.0, 4.0, 3.0, 8.0};
    const __m256d double256_right = {0.0, 5.0, 3.0, 9.0};
    const int float128_mask = _mm_movemask_ps(compare_float128(float128_left, float128_right));
    const int double128_mask = _mm_movemask_pd(compare_double128(double128_left, double128_right));
    const int float256_mask = _mm256_movemask_ps(compare_float256(float256_left, float256_right));
    const int double256_mask = _mm256_movemask_pd(compare_double256(double256_left, double256_right));
    const int memory_mask = _mm256_movemask_ps(compare_float_memory(float256_left, float256_right));
    const __m128 float128_values = {1.0f, 2.0f, 3.0f, 4.0f};
    const __m128d double128_values = {1.0, 2.0};
    const __m256 float256_values = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
    const __m256d double256_values = {1.0, 2.0, 3.0, 4.0};
    return float128_mask == 5 && double128_mask == 3 && float256_mask == 85 && double256_mask == 1
            && memory_mask == 85
            && test_float128(_mm_setzero_ps(), float128_values) == 1
            && test_double128(double128_values, double128_values) == 1
            && test_float256(_mm256_setzero_ps(), float256_values) == 1
            && test_double256(double256_values, double256_values) == 1
        ? 42
        : 1;
}
