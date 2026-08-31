typedef float vector256 __attribute__((vector_size(32)));

__attribute__((noinline)) static vector256 shuffle256(vector256 input) {
    vector256 result;
    __asm__ volatile("vpermilps $0x1b, %1, %0" : "=x"(result) : "x"(input));
    return result;
}

int main(void) {
    vector256 input = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
    vector256 result = shuffle256(input);
    return result[0] == 4.0f && result[7] == 5.0f ? 42 : 1;
}
