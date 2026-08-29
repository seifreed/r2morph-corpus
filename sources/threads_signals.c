#include <pthread.h>
#include <signal.h>
#include <stddef.h>

static volatile sig_atomic_t signal_seen;
static _Thread_local volatile unsigned long thread_value;

static void on_signal(int signal_number) {
    (void)signal_number;
    signal_seen = 1;
    thread_value += 3UL;
}

__attribute__((noinline)) static void *thread_entry(void *argument) {
    thread_value = (unsigned long)(size_t)argument;
    return NULL;
}

int main(int argc, char **argv) {
    pthread_t thread;
    thread_value = 9UL;
    signal(SIGUSR1, on_signal);
    if (pthread_create(&thread, NULL, thread_entry, (void *)5UL) != 0) {
        return 1;
    }
    if (pthread_join(thread, NULL) != 0) {
        return 2;
    }
    raise(SIGUSR1);
    return (int)(thread_value + (unsigned long)signal_seen +
                 (unsigned)(argc > 1 ? argv[1][0] & 1 : 0)) & 127;
}
