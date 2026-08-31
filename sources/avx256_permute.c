typedef float vector256 __attribute__((vector_size(32)));

__attribute__((noinline)) static vector256 permute256(vector256 left, vector256 right) {
    vector256 result;
    __asm__ volatile("vperm2f128 $0x31, %2, %1, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

int main(void) {
    vector256 left = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
    vector256 right = {11.0f, 12.0f, 13.0f, 14.0f, 15.0f, 16.0f, 17.0f, 18.0f};
    vector256 result = permute256(left, right);
    return result[0] == 5.0f && result[7] == 18.0f ? 42 : 1;
}
