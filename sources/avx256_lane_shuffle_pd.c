typedef double vector256 __attribute__((vector_size(32)));

__attribute__((noinline)) static vector256 shuffle256(vector256 input) {
    vector256 result;
    __asm__ volatile("vpermilpd $0x05, %1, %0" : "=x"(result) : "x"(input));
    return result;
}

int main(void) {
    vector256 input = {1.0, 2.0, 3.0, 4.0};
    vector256 result = shuffle256(input);
    return result[0] == 2.0 && result[3] == 3.0 ? 42 : 1;
}
