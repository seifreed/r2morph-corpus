typedef float vector256 __attribute__((vector_size(32)));
typedef double double_vector256 __attribute__((vector_size(32)));

__attribute__((noinline)) static vector256 shuffle_float(vector256 left, vector256 right) {
    vector256 result;
    __asm__ volatile("vshufps $0x1b, %2, %1, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

__attribute__((noinline)) static double_vector256 shuffle_double(
    double_vector256 left, double_vector256 right
) {
    double_vector256 result;
    __asm__ volatile("vshufpd $0x05, %2, %1, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

int main(void) {
    vector256 float_left = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f};
    vector256 float_right = {11.0f, 12.0f, 13.0f, 14.0f, 15.0f, 16.0f, 17.0f, 18.0f};
    double_vector256 double_left = {1.0, 2.0, 3.0, 4.0};
    double_vector256 double_right = {11.0, 12.0, 13.0, 14.0};
    vector256 float_result = shuffle_float(float_left, float_right);
    double_vector256 double_result = shuffle_double(double_left, double_right);
    return float_result[0] == 4.0f && float_result[7] == 15.0f
        && double_result[0] == 2.0 && double_result[3] == 13.0 ? 42 : 1;
}
