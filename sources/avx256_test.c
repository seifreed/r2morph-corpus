#include <immintrin.h>

__attribute__((noinline)) static int test_vectors(const __m256i left, const __m256i right) {
    return _mm256_testz_si256(left, right);
}

int main(void) {
    const __m256i left = _mm256_set_epi64x(0, 0, 0, 1);
    const __m256i right = _mm256_set_epi64x(0, 0, 0, 1);
    return test_vectors(left, right) == 0 ? 42 : 1;
}
