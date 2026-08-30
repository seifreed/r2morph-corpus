#include <pthread.h>
#include <stdint.h>

static volatile unsigned counter;

__attribute__((noinline)) static void *worker(void *argument) {
    unsigned iterations = (unsigned)(uintptr_t)argument;
    for (unsigned index = 0; index < iterations; ++index) {
        unsigned delta = 1;
#if defined(__x86_64__)
        __asm__ volatile("lock xaddl %1, %0" : "+m"(counter), "+r"(delta) : : "memory", "cc");
#else
        __atomic_fetch_add(&counter, delta, __ATOMIC_SEQ_CST);
#endif
    }
    return 0;
}

int main(void) {
    pthread_t threads[4];
    for (unsigned index = 0; index < 4; ++index) {
        if (pthread_create(&threads[index], 0, worker, (void *)(uintptr_t)1000) != 0) {
            return 1;
        }
    }
    for (unsigned index = 0; index < 4; ++index) {
        if (pthread_join(threads[index], 0) != 0) {
            return 2;
        }
    }
    return counter == 4000 ? 23 : 3;
}
