#include "config.h"
#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <strings.h>
#include <sys/mman.h>
#include <time.h>
#include <util.h>
#include <low.h>
#include <string.h>
#include <errno.h>
#include <pthread.h>
#define LENGTH 6 * 1024 * 1024
#define SET_NUM 8192
#define ASSOC 12
#define SAMPLES 15000
#define NUM_THREADS 128
#define PAGE_NUM 128
#define SET_PER_PAGE 64
#define LINE_NUM SET_NUM *ASSOC
#define DETECTION_TIME 30000000

struct l_l3
{
    char data[40];
    int id;
    int page_offset;
    int set_offset;
    int line_offset;
    struct l_l3 *next;
};

int seq_probe(void *l3_buffer);
void part_prime(void *l3_buffer);
void whole_prime(void *l3_buffer);
void part_probe(void *l3_buffer);
void whole_probe(void *l3_buffer);
void shuffle(int *array, size_t n);

void shuffle(int *array, size_t n)
{
    if (n > 1)
    {
        size_t i;
        for (i = 0; i < n - 1; i++)
        {
            size_t j = i + rand() / (RAND_MAX / (n - i) + 1);
            int t = array[j];
            array[j] = array[i];
            array[i] = t;
        }
    }
}

int seq_probe(void *set_head)
{
    struct l_l3 *tmp = set_head;
    struct l_l3 *head = set_head;
    int rv = 0;
    int n = 0;
    do
    {
        n++;
        uint32_t s = rdtscp();
        tmp = tmp->next;
        s = rdtscp() - s;
        if (s > L3_THRESHOLD)
            rv++;
    } while (tmp->next != head);
    // printf("num: %d\n",n);
    return rv;
}

void part_probe(void *buf)
{
    struct l_l3 *set;
    struct l_l3 *buffer = buf;
    int line_id = 0;
    for (int i = 0; i < LINE_NUM; i += ASSOC * 32)
    {
        for (int j = 0; j < ASSOC; j++)
        {
            line_id = i + j;
            set = &buffer[line_id];

            if (j == ASSOC - 1)
            {
                buffer[line_id].id = line_id;
                buffer[line_id].next = &buffer[i];
            }
            else
            {
                buffer[line_id].id = line_id;
                buffer[line_id].next = &buffer[line_id + 1];
            }
        }
    }
}

void part_prime(void *buf)
{
    struct l_l3 *buffer, *set_head;
    uint16_t *result = calloc(SAMPLES * SET_NUM, sizeof(uint16_t));

    for (int i = 0; i < SAMPLES * SET_NUM; i += 4096 / sizeof(uint16_t))
        result[i] = 1;

    part_probe((void *)buffer);
    for (int i = 0; i < SAMPLES; i++)
    {
        for (int j = 0; j < SET_NUM; j++)
        {
            set_head = &buffer[j * ASSOC];
            result[i * SET_NUM + j] = seq_probe((void *)set_head);
        }
    }

    char file_name[] = "demo/data/browser_test.txt";
    for (int i = 0; i < SAMPLES; i++)
    {
        for (int j = 0; j < SET_NUM; j++)
        {
            // printf("%4d ", res[i*nmonitored + j]);

            FILE *f = fopen(file_name, "a");
            fprintf(f, "%d", result[i * SET_NUM + j]);
            fprintf(f, "%c", ',');
            fclose(f);
        }
        // putchar('\n');
        FILE *f = fopen(file_name, "a");
        fprintf(f, "%c", '\n');
        fclose(f);
    }
}

void whole_prime(void *buf)
{
    struct l_l3 *set;
    struct l_l3 *buffer = buf;
    int line_id = 0;

    for (int i = 0; i < SET_NUM; i++)
    {

        for (int j = 0; j < ASSOC; j++)
        {
            line_id = i * ASSOC + j;
            set = &buffer[line_id];
            if (j == ASSOC - 1)
            {
                buffer[line_id].id = line_id;
                buffer[line_id].next = &buffer[i * ASSOC];
            }
            else
            {
                buffer[line_id].id = line_id;
                buffer[line_id].next = &buffer[line_id + 1];
            }
        }
    }
}

void whole_probe(void *buf)
{

    struct l_l3 *set_head;
    struct l_l3 *buffer = buf;
    uint16_t *result = calloc(SAMPLES, sizeof(uint16_t));

    // for (int i = 0; i < SAMPLES; i += 4096 / sizeof(uint16_t))
    //     result[i] = 1;

    whole_prime((void *)buffer);

    int *arr = calloc(SET_NUM, sizeof(int));
    for (int i = 0; i < SET_NUM; i++)
        arr[i] = i;
    shuffle(arr, SET_NUM);

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC_RAW, &start);
    int bufsize;
    for (int i = 0; i < SAMPLES; i++)
    {
        int Rv = 0;
        int r = 0;
        for (int j = 0; j < SET_NUM; j++)
        {
            // printf("head: %d\t",arr[j]);
            set_head = &buffer[arr[j] * ASSOC];
            r = seq_probe((void *)set_head);
            Rv += r;
        }
        result[i] = Rv;
        clock_gettime(CLOCK_MONOTONIC_RAW, &end);
        uint64_t delta_s1 = (end.tv_sec - start.tv_sec) * 1000 + (end.tv_nsec - start.tv_nsec) / 1000000;
        // if (delta_s1 > DETECTION_TIME)
            // break;
    }

    // printf("end in %lu s\n", delta_s1);

    char file_name[] = "data/malicious_random1.txt";
    
    for (int i = 0; i < SAMPLES; i++)
    {

        FILE *f = fopen(file_name, "a");
        fprintf(f, "%d", result[i]);
        fprintf(f, "%c", ',');
        fclose(f);
    }
    FILE *f = fopen(file_name, "a");
    // fprintf(f, "%c", '\n');
    fclose(f);
    clock_gettime(CLOCK_MONOTONIC_RAW, &end);
    uint64_t delta_s2 = (end.tv_sec - start.tv_sec);
    // printf("end in %lu s\n", delta_s2);
}

int main()
{
    int bufsize;
    struct l_l3 *buffer;
    bufsize = LENGTH;
    buffer = mmap(NULL, bufsize, PROT_READ | PROT_WRITE, MAP_ANON | MAP_PRIVATE, -1, 0);
    // int a = sizeof(uint16_t);
    while(1)
        whole_probe((void *)buffer);
}