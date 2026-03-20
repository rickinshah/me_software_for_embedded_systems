#include "task.h"
#include <stdint.h>
#include "delay.h"
#include "uart.h"

#define TOTAL_PRIORITY        10
#define TASKS_IN_PRIORITY     5
#define SPORADIC_PRIORITY     4
#define SPORADIC_PRIORITY_PA1 7
#define SPORADIC_PRIORITY_PA4 9

volatile uint8_t sporadic             = 0;
volatile uint8_t sporadic_pa1         = 0;
volatile uint8_t sporadic_pa4         = 0;
uint8_t          sporadic_pending     = 0;
uint8_t          sporadic_pending_pa1 = 0;
uint8_t          sporadic_pending_pa4 = 0;

void scheduler() {
    uint8_t index = 0;
    while (1) {
        for (uint8_t curr_priority = 0; curr_priority < TOTAL_PRIORITY; curr_priority++) {
            if (curr_priority == SPORADIC_PRIORITY) {
                sporadic_pending = sporadic;
                sporadic         = 0;
            } else if (curr_priority == SPORADIC_PRIORITY_PA1) {
                sporadic_pending_pa1 = sporadic_pa1;
                sporadic_pa1         = 0;
            } else if (curr_priority == SPORADIC_PRIORITY_PA4) {
                sporadic_pending_pa4 = sporadic_pa4;
                sporadic_pa4         = 0;
            }
            if (curr_priority == SPORADIC_PRIORITY && sporadic_pending != 0) {
                for (uint8_t i = 0; i < sporadic_pending; i++) {
                    task(curr_priority, SPORADIC_PRIORITY, 1);
                    delay_ms(100);
                }
                sporadic_pending = 0;
            }
            if (curr_priority == SPORADIC_PRIORITY_PA1 && sporadic_pending_pa1 != 0) {
                for (uint8_t i = 0; i < sporadic_pending_pa1; i++) {
                    task(curr_priority, SPORADIC_PRIORITY_PA1, 1);
                    delay_ms(100);
                }
                sporadic_pending_pa1 = 0;
            }
            if (curr_priority == SPORADIC_PRIORITY_PA4 && sporadic_pending_pa4 != 0) {
                for (uint8_t i = 0; i < sporadic_pending_pa4; i++) {
                    task(curr_priority, SPORADIC_PRIORITY_PA4, 1);
                    delay_ms(100);
                }
                sporadic_pending_pa4 = 0;
            }
            for (uint8_t curr_task = 0; curr_task < TASKS_IN_PRIORITY; curr_task++) {
                task(curr_priority, index, 0);
                index = (index + 1) % (TOTAL_PRIORITY * TASKS_IN_PRIORITY);
                delay_ms(100);
            }
            delay_ms(100);
        }
    }
}

void task(uint8_t priority, uint8_t id, uint8_t is_sporadic) {
    uint8_t* pr_str = (uint8_t*) "[Priority ";
    uint8_t* tk_str = (uint8_t*) "] Task ";
    uint8_t* sp_str = (uint8_t*) "] Sporadic ";
    UART_SendArray(pr_str, 10);
    UART_SendNumber(priority);
    if (!is_sporadic)
        UART_SendArray(tk_str, 7);
    else
        UART_SendArray(sp_str, 11);
    UART_SendNumber(id);
    UART_SendByte('\r');
    UART_SendByte('\n');
}
