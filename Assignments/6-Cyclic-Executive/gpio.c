#include "gpio.h"
#include "stm32f4xx.h"

void GPIO_Init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIODEN;

    GPIOA->MODER &= ~(3 << (0 * 2));
    GPIOD->MODER &= ~(3 << (12 * 2));
    GPIOD->MODER |= (1 << (12 * 2));
}
