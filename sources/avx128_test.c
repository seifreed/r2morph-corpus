typedef unsigned long long vector128_qwords __attribute__((vector_size(16)));

__attribute__((noinline)) static unsigned char test_zero(vector128_qwords left, vector128_qwords right) {
    unsigned char result;
    __asm__ volatile("vptest %2, %1\n sete %0" : "=q"(result) : "x"(left), "x"(right) : "cc");
    return result;
}

int main(void) {
    vector128_qwords nonzero = {1, 0};
    vector128_qwords zero = {0, 0};
    return test_zero(nonzero, nonzero) == 0 && test_zero(nonzero, zero) == 1 ? 42 : 1;
}
