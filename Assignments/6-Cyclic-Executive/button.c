#include "button.h"
#include "delay.h"
#include "stm32f4xx.h"
#include "task.h"
#include "uart.h"

volatile uint32_t last_press = 0;

void EXTI_Init(void) {
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

    SYSCFG->EXTICR[0] &= ~(0xF << 0);
    EXTI->RTSR |= (1 << 0);
    EXTI->IMR |= (1 << 0);
    NVIC_EnableIRQ(EXTI0_IRQn);
}

void EXTI0_IRQHandler(void) {
    uint8_t* str = "Sporadic entered!";
    if (EXTI->PR & (1 << 0)) {
        EXTI->PR |= (1 << 0);

        if ((ticks - last_press) > 250) {
            sporadic++;
            UART_SendArray(str, 17);
            UART_SendByte('\r');
            UART_SendByte('\n');

            GPIOD->ODR ^= (1 << 12);
            last_press = ticks;
        }
    }
}
