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
#include <unistd.h>

#include <pthread.h>
#define LENGTH 6 * 1024 * 1024
#define SET_NUM 8192
#define ASSOC 12
#define SAMPLE = 5000
#define NUM_THREADS 128
#define PAGE_NUM 128
#define SET_PER_PAGE 64
#define SET_PER_PROC 16
#define DEFENSE_TIME 10000
#define P 25
void probe(void *page);
void prime(void *page);
void random_probe_page(void *page);
void delay(int ms);
void prepare(void *l3_buffer);
void four_proc(void *l3_buffer);
void eight_proc(void *l3_buffer);
void one_proc(void *l3_buffer);
void two_proc(void *l3_buffer);
int probability(int pro);
void four_random(void *l3_buffer);

struct st
{
    char data[40];
    int id;
    int page_offset;
    int set_offset;
    int line_offset;
    struct st *next;
};

int probability(int pro)
{
    srand(time(0));
    int upper = 99;
    int lower = 0;
    int num = (rand() % (upper - lower + 1)) + lower;
    if (num > 100 - pro)
        return 1;
    else
        return 0;
}

void prepare(void *l3_buffer)
{
    struct st *tmp, *set;
    int line_id = 0;
    struct st *buffer = l3_buffer;
    for (int i = 0; i < PAGE_NUM; i++)
    {
        for (int j = 0; j < SET_PER_PAGE; j++)
        {
            for (int k = 0; k < ASSOC; k++)
            {

                set = &buffer[line_id];

                if (line_id == ((i + 1) * SET_PER_PAGE * ASSOC - 1))
                {
                    buffer[line_id].next = &buffer[i * SET_PER_PAGE * ASSOC];
                    tmp = &buffer[0];
                }
                else
                {
                    buffer[line_id].next = &buffer[line_id + 1];
                }

                buffer[line_id].id = line_id;
                buffer[line_id].page_offset = i;
                buffer[line_id].set_offset = j;
                buffer[line_id].line_offset = k;
                strcpy(buffer[line_id].data, "1");
                line_id++;
            }
        }
    }
}

void delay(int us)
{
    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    while (1)
    {
        clock_gettime(CLOCK_MONOTONIC_RAW, &end);
        uint64_t total_time = (end.tv_sec - start.tv_sec) * 1000000 + (end.tv_nsec - start.tv_nsec) / 1000;
        if (total_time >= us)
        {
            break;
        }
    }
}
void prime(void *page)
{
    struct st *tmp;
    tmp = page;
    struct timespec start, end;

    char file_name[20] = "src_data/";
    char index[10];
    char sd[5];
    sprintf(index, "%d", tmp->page_offset);
    // sprintf(index, "%d", n);
    // strcat("data/", file_name);
    strcat(index, ".txt");
    strcat(file_name, index);
    FILE *ff = fopen(file_name, "r");

    do
    {

        fscanf(ff, "%s", sd);
        strcpy(tmp->data, sd);
        tmp = tmp->next;
        memset(sd, 0, sizeof(sd));
        // delay(10);
        // printf("%d, %d\n",tmp->id, tmp->next->id);
    } while (tmp->next != page);
    fclose(ff);
    // fprintf(f, "%s", 'a');
}
void probe(void *page)
{

    struct st *tmp;
    tmp = page;
    struct timespec start, end;

    char file_name[20] = "cache_data/";
    char index[10];
    int idx = (tmp->page_offset)/32;
    sprintf(index, "%d", idx);
    // sprintf(index, "%d", n);
    // strcat("data/", file_name);
    strcat(index, ".txt");
    strcat(file_name, index);
    FILE *f = fopen(file_name, "a");
    // if (probability(P))
    {
    do
    {
        fprintf(f, "%s", tmp->data);
        tmp = tmp->next;
        // delay(200000);
        // printf("%d, %d\n",tmp->id, tmp->next->id);
    } while (tmp->next != page);
    }
    // else
    // {
    //     // do
    //     // {
    //     //     // fprintf(f, "%s", tmp->data);
    //     //     tmp = tmp->next;
    //         // delay(200000);
    //         // printf("%d, %d\n",tmp->id, tmp->next->id);
    //     // } while (tmp->next != page);
    // }
    

    fseek(f, 0L, SEEK_END);
    long int res = ftell(f);
    fclose(f);
    // int del = remove(file_name);
    if (res > 10 * 1024 * 1024)
    {
        // int del = remove(file_name);
    }
}

void random_probe_page(void *page)
{

    struct st *tmp;
    tmp = page;
    struct timespec start, end;

    char file_name[20] = "cache_data/";
    char index[10];
    sprintf(index, "%d", tmp->page_offset);

    strcat(index, ".txt");
    strcat(file_name, index);
    FILE *f = fopen(file_name, "a");

    if (probability(P))
    {
        do
        {
            fprintf(f, "%c", tmp->data[0]);
            tmp = tmp->next;
            // delay(25);
            // delayloop(40000U);
            // printf("%d, %d\n",tmp->id, tmp->next->id);
        } while (tmp->next != page);
    }
    else
    {
        delay(25);
        // delayloop(1700000U);
    }

    // fprintf(f, "%s", 'a');

    fseek(f, 0L, SEEK_END);
    long int res = ftell(f);
    fclose(f);
    // int del = remove(file_name);
    if (res > 10 * 1024 * 1024)
    {
        int del = remove(file_name);
    }
    // delayloop(1700000000U);
    // delay(10);
    //
}

void one_proc(void *l3_buffer)
{
    struct st *buffer = l3_buffer;
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    // int n1 = fork();
    // int n1 = 1;

    while (1)
    {
        for (int i = 0; i < 128; i++)
        {
            struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
            // prime((void *)page);
            probe((void *)page);
            // random_probe_page((void *)page);
        }

        clock_gettime(CLOCK_MONOTONIC_RAW, &end);
        uint64_t total_time = (end.tv_sec - start.tv_sec) * 1000 + (end.tv_nsec - start.tv_nsec) / 1000000;
        if (total_time > DEFENSE_TIME)
        {
            // printf("%ld\n", total_time);

            // break;
        }
    }
}

void two_proc(void *l3_buffer)
{
    struct st *buffer = l3_buffer;
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    int n1 = fork();

    while (1)
    {
        if (n1 > 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = 0; i < SET_PER_PROC * 2; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // random_probe_page((void *)page);
            }
        }
        else
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 6; i < SET_PER_PROC * 8; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // random_probe_page((void *)page);
            }
        }

        clock_gettime(CLOCK_MONOTONIC_RAW, &end);
        uint64_t total_time = (end.tv_sec - start.tv_sec) * 1000 + (end.tv_nsec - start.tv_nsec) / 1000000;
        if (total_time > DEFENSE_TIME)
        {
            // printf("%ld\n", total_time);

            break;
        }
    }
}

void four_proc(void *l3_buffer)
{
    struct st *buffer = l3_buffer;
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    int n1 = fork();
    int n2 = fork();

    while (1)
    {
        if (n1 > 0 && n2 > 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = 0; i < SET_PER_PROC * 2; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                // prime((void *)page);
                probe((void *)page);
                // random_probe_page((void *)page);
            }
        }
        else if (n1 == 0 && n2 > 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 2; i < SET_PER_PROC * 4; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                // prime((void *)page);
                probe((void *)page);
                // random_probe_page((void *)page);
            }
        }
        else if (n1 > 0 && n2 == 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 4; i < SET_PER_PROC * 6; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                // prime((void *)page);
                probe((void *)page);
                // random_probe_page((void *)page);
            }
        }
        else
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 6; i < SET_PER_PROC * 8; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                // prime((void *)page);
                probe((void *)page);
                // random_probe_page((void *)page);
            }
        }

        clock_gettime(CLOCK_MONOTONIC_RAW, &end);
        uint64_t total_time = (end.tv_sec - start.tv_sec) * 1000 + (end.tv_nsec - start.tv_nsec) / 1000000;
        if (total_time > DEFENSE_TIME)
        {
            // printf("%ld\n", total_time);

            break;
        }
    }
}

void four_random(void *l3_buffer)
{
    struct st *buffer = l3_buffer;
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    int n1 = fork();
    int n2 = fork();

    while (1)
    {
        if(probability(P))
        {
            if (n1 > 0 && n2 > 0)
            {
                // printf(" my id is %d \n", getpid());
                // for (int i = 0; i < SET_PER_PROC * 2; i++)
                for (int i = 0; i < 128; i++)
                {
                    struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                    // prime((void *)page);
                    probe((void *)page);
                    // random_probe_page((void *)page);
                    delay(200000);
                }
            }
            else if (n1 == 0 && n2 > 0)
            {
                // printf(" my id is %d \n", getpid());
                // for (int i = SET_PER_PROC * 2; i < SET_PER_PROC * 4; i++)
                for (int i = 0; i < 128; i++)
                {
                    struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                    // prime((void *)page);
                    probe((void *)page);
                    // random_probe_page((void *)page);
                    delay(200000);
                }
            }
            else if (n1 > 0 && n2 == 0)
            {
                // printf(" my id is %d \n", getpid());
                // for (int i = SET_PER_PROC * 4; i < SET_PER_PROC * 6; i++)
                for (int i = 0; i < 128; i++)
                {
                    struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                    // prime((void *)page);
                    probe((void *)page);
                    // random_probe_page((void *)page);
                    delay(200000);
                }
            }
            else
            {
                // printf(" my id is %d \n", getpid());
                // for (int i = SET_PER_PROC * 6; i < SET_PER_PROC * 8; i++)
                for (int i = 0; i < 128; i++)
                {
                    struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                    // prime((void *)page);
                    probe((void *)page);
                    // random_probe_page((void *)page);
                    delay(200000);
                }
            }
        }
        // else
        // {
        delay(200000);
        // }

        clock_gettime(CLOCK_MONOTONIC_RAW, &end);
        uint64_t total_time = (end.tv_sec - start.tv_sec) * 1000 + (end.tv_nsec - start.tv_nsec) / 1000000;
        if (total_time > DEFENSE_TIME)
        {
            // printf("%ld\n", total_time);

            break;
        }
    }
}

void eight_proc(void *l3_buffer)
{
    struct st *buffer = l3_buffer;
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    int n1 = fork();
    int n2 = fork();
    int n3 = fork();

    while (1)
    {
        if (n1 > 0 && n2 > 0 && n3 > 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = 0; i < SET_PER_PROC * 2; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // w(i);
            }
        }
        else if (n1 == 0 && n2 > 0 && n3 > 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 2; i < SET_PER_PROC * 4; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // w(i);
            }
        }
        else if (n1 > 0 && n2 == 0 && n2 > 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 4; i < SET_PER_PROC * 6; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // w(i);
            }
        }
        else if (n1 > 0 && n2 > 0 && n3 == 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 6; i < SET_PER_PROC * 8; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // w(i);
            }
        }
        else if (n1 > 0 && n2 == 0 && n3 == 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 0; i < SET_PER_PROC * 2; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // w(i);
            }
        }
        else if (n1 == 0 && n2 > 0 && n3 == 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 2; i < SET_PER_PROC * 4; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // w(i);
            }
        }
        else if (n1 == 0 && n2 == 0 && n3 > 0)
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 4; i < SET_PER_PROC * 6; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // w(i);
            }
        }
        else
        {
            // printf(" my id is %d \n", getpid());
            // for (int i = SET_PER_PROC * 6; i < SET_PER_PROC * 8; i++)
            for (int i = 0; i < 128; i++)
            {
                struct st *page = &buffer[i * SET_PER_PAGE * ASSOC];
                prime((void *)page);
                probe((void *)page);
                // w(i);
            }
        }

        clock_gettime(CLOCK_MONOTONIC_RAW, &end);
        uint64_t total_time = (end.tv_sec - start.tv_sec) * 1000 + (end.tv_nsec - start.tv_nsec) / 1000000;
        if (total_time > DEFENSE_TIME)
        {
            // printf("%ld\n", total_time);

            break;
        }
    }
}

int main()
{
    int bufsize;
    struct st *buffer;
    bufsize = LENGTH;
    buffer = mmap(NULL, bufsize, PROT_READ | PROT_WRITE, MAP_ANON | MAP_PRIVATE, -1, 0);
    prepare(buffer);
    // two_proc((void *)buffer);
    four_proc((void *)buffer);
    // four_random((void *)buffer);
    // eight_proc((void *)buffer);
    // one_proc((void *)buffer);
    return 0;
}
