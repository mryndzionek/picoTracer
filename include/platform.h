#ifndef PLATFORM_H_INCLUDED
#define PLATFORM_H_INCLUDED

#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <time.h>

static uint32_t print_current_time_with_ms (void)
{
    uint32_t        ms; // Milliseconds
    time_t          s;  // Seconds
    struct timespec spec;

    clock_gettime(CLOCK_REALTIME, &spec);

    s  = spec.tv_sec;
    ms = round(spec.tv_nsec / 1.0e6); // Convert nanoseconds to milliseconds

    return 1000*s + ms;
}

#define GET_TIMESTAMP print_current_time_with_ms();

#endif // PLATFORM_H_INCLUDED
