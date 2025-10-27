#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_ATTEMPTS 10
#define TIME_WINDOW 60
#define CLEANUP_INTERVAL 300

typedef struct {
    char ip[16];
    time_t timestamps[MAX_ATTEMPTS];
    int count;
} AttemptRecord;

typedef struct {
    AttemptRecord* records;
    int size;
    pthread_mutex_t lock;
} RateLimiter;

RateLimiter* create_rate_limiter() {
    RateLimiter* limiter = malloc(sizeof(RateLimiter));
    limiter->records = NULL;
    limiter->size = 0;
    pthread_mutex_init(&limiter->lock, NULL);
    return limiter;
}

int is_allowed(RateLimiter* limiter, const char* ip) {
    pthread_mutex_lock(&limiter->lock);
    
    time_t now = time(NULL);
    int found = 0;
    
    for (int i = 0; i < limiter->size; i++) {
        if (strcmp(limiter->records[i].ip, ip) == 0) {
            found = 1;
            
            // Remove expired attempts
            int j = 0;
            for (; j < limiter->records[i].count; j++) {
                if (now - limiter->records[i].timestamps[j] > TIME_WINDOW) {
                    break;
                }
            }
            
            memmove(
                &limiter->records[i].timestamps[0],
                &limiter->records[i].timestamps[j],
                sizeof(time_t) * (limiter->records[i].count - j)
            );
            
            limiter->records[i].count -= j;
            
            if (limiter->records[i].count >= MAX_ATTEMPTS) {
                pthread_mutex_unlock(&limiter->lock);
                return 0;
            }
            
            limiter->records[i].timestamps[limiter->records[i].count++] = now;
            break;
        }
    }
    
    if (!found) {
        limiter->size++;
        limiter->records = realloc(
            limiter->records,
            sizeof(AttemptRecord) * limiter->size
        );
        
        strcpy(limiter->records[limiter->size - 1].ip, ip);
        limiter->records[limiter->size - 1].count = 1;
        limiter->records[limiter->size - 1].timestamps[0] = now;
    }
    
    pthread_mutex_unlock(&limiter->lock);
    return 1;
}

void* cleanup_thread(void* arg) {
    RateLimiter* limiter = (RateLimiter*)arg;
    
    while (1) {
        sleep(CLEANUP_INTERVAL);
        pthread_mutex_lock(&limiter->lock);
        
        time_t now = time(NULL);
        
        for (int i = 0; i < limiter->size; i++) {
            int j = 0;
            for (; j < limiter->records[i].count; j++) {
                if (now - limiter->records[i].timestamps[j] > TIME_WINDOW) {
                    break;
                }
            }
            
            if (j > 0) {
                memmove(
                    &limiter->records[i].timestamps[0],
                    &limiter->records[i].timestamps[j],
                    sizeof(time_t) * (limiter->records[i].count - j)
                );
                
                limiter->records[i].count -= j;
            }
        }
        
        pthread_mutex_unlock(&limiter->lock);
    }
    
    return NULL;
}