#include "button.h"
#include "delay.h"
#include "stm32f4xx.h"
#include "task.h"
#include "uart.h"

volatile uint32_t last_press     = 0;
volatile uint32_t last_press_pa1 = 0;
volatile uint32_t last_press_pa4 = 0;

void EXTI_Init(void) {
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

    SYSCFG->EXTICR[0] &= ~(0xF << 0);
    SYSCFG->EXTICR[0] &= ~(0xF << 4);
    SYSCFG->EXTICR[1] &= ~(0xF << 0);
    EXTI->RTSR |= (1 << 0);
    EXTI->FTSR |= (1 << 1) | (1 << 4);
    EXTI->RTSR &= ~(1 << 1);
    EXTI->RTSR &= ~(1 << 4);
    EXTI->IMR |= (1 << 0) | (1 << 1) | (1 << 4);
    NVIC_EnableIRQ(EXTI0_IRQn);
    NVIC_EnableIRQ(EXTI1_IRQn);
    NVIC_EnableIRQ(EXTI4_IRQn);
}


void EXTI0_IRQHandler(void) {
    uint8_t* str = "Sporadic 4 entered!";
    if (EXTI->PR & (1 << 0)) {
        EXTI->PR |= (1 << 0);

        if ((ticks - last_press) > 250) {
            sporadic++;
            UART_SendArray(str, 19);
            UART_SendByte('\r');
            UART_SendByte('\n');

            // GPIOD->ODR ^= (1 << 12);
            last_press = ticks;
        }
    }
}

void EXTI1_IRQHandler(void) {
    uint8_t* str = "Sporadic 7 entered!";
    if (EXTI->PR & (1 << 1)) {
        EXTI->PR |= (1 << 1);

        if ((ticks - last_press_pa1) > 250) {
            sporadic_pa1++;
            UART_SendArray(str, 19);
            UART_SendByte('\r');
            UART_SendByte('\n');

            // GPIOD->ODR ^= (1 << 12);
            last_press_pa1 = ticks;
        }
    }
}

void EXTI4_IRQHandler(void) {
    uint8_t* str = "Sporadic 9 entered!";
    if (EXTI->PR & (1 << 4)) {
        EXTI->PR |= (1 << 4);

        if ((ticks - last_press_pa4) > 250) {
            sporadic_pa4++;
            UART_SendArray(str, 19);
            UART_SendByte('\r');
            UART_SendByte('\n');

            // GPIOD->ODR ^= (1 << 12);
            last_press_pa4 = ticks;
        }
    }
}
