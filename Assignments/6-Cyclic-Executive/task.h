#ifndef TASK_H
#define TASK_H
#include <stdint.h>

extern volatile uint8_t sporadic;

void task_init(void);
void scheduler(void);
void task(uint8_t priority, uint8_t id, uint8_t is_sporadic);

#endif
