typedef unsigned char vector128_bytes __attribute__((vector_size(16)));
typedef short vector128_words __attribute__((vector_size(16)));
typedef long vector128_qwords __attribute__((vector_size(16)));

__attribute__((noinline)) static vector128_bytes compare_bytes(vector128_bytes left, vector128_bytes right) {
    vector128_bytes result;
    __asm__ volatile("vpcmpeqb %2, %1, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

__attribute__((noinline)) static vector128_bytes compare_bytes_greater(vector128_bytes left, vector128_bytes right) {
    vector128_bytes result;
    __asm__ volatile("vpcmpgtb %2, %1, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

__attribute__((noinline)) static vector128_words compare_words(vector128_words left, vector128_words right) {
    vector128_words result;
    __asm__ volatile("vpcmpgtw %2, %1, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

__attribute__((noinline)) static vector128_words compare_words_equal(vector128_words left, vector128_words right) {
    vector128_words result;
    __asm__ volatile("vpcmpeqw %2, %1, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

__attribute__((noinline)) static vector128_qwords compare_qwords(vector128_qwords left, vector128_qwords right) {
    vector128_qwords result;
    __asm__ volatile("vpcmpgtq %2, %1, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

__attribute__((noinline)) static vector128_qwords compare_qwords_equal(vector128_qwords left, vector128_qwords right) {
    vector128_qwords result;
    __asm__ volatile("vpcmpeqq %2, %1, %0" : "=x"(result) : "x"(left), "x"(right));
    return result;
}

int main(void) {
    vector128_bytes bytes_left = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    vector128_bytes bytes_right = {1, 0, 3, 0, 5, 0, 7, 0, 9, 0, 11, 0, 13, 0, 15, 0};
    vector128_words words_left = {1, 2, 3, 4, 5, 6, 7, 8};
    vector128_words words_right = {0, 2, 1, 4, 4, 6, 6, 8};
    vector128_qwords qwords_left = {1, 2};
    vector128_qwords qwords_right = {0, 2};
    vector128_bytes bytes = compare_bytes(bytes_left, bytes_right);
    vector128_bytes bytes_greater = compare_bytes_greater(bytes_left, bytes_right);
    vector128_words words = compare_words(words_left, words_right);
    vector128_words words_equal = compare_words_equal(words_left, words_right);
    vector128_qwords qwords = compare_qwords(qwords_left, qwords_right);
    vector128_qwords qwords_equal = compare_qwords_equal(qwords_left, qwords_right);
    return bytes[0] == 255 && bytes[1] == 0 && bytes_greater[0] == 0 && bytes_greater[1] == 255
                   && words[0] == -1 && words[1] == 0 && words_equal[0] == 0 && words_equal[1] == -1
                   && qwords[0] == -1 && qwords[1] == 0 && qwords_equal[0] == 0 && qwords_equal[1] == -1
               ? 42
               : 1;
}
