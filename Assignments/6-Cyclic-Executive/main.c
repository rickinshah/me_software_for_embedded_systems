#include "button.h"
#include "delay.h"
#include "gpio.h"
#include "stm32f4xx.h"
#include "task.h"
#include "uart.h"

int main() {
    SystemInit();
    SysTick_Init();
    GPIO_Init();
    EXTI_Init();
    UART2_Init();

    scheduler();
    while (1) {
    }
}
