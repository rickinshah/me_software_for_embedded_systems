#include "gpio.h"
#include "stm32f4xx.h"

void GPIO_Init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIODEN;

    GPIOA->MODER &= ~(3 << (0 * 2));

    GPIOA->MODER &= ~(3 << (1 * 2));
    GPIOA->PUPDR &= ~(3 << (1 * 2));
    GPIOA->PUPDR |= (1 << (1 * 2));  // 01 = pull-up

    GPIOA->MODER &= ~(3 << (4 * 2));
    GPIOA->PUPDR &= ~(3 << (4 * 2));
    GPIOA->PUPDR |= (1 << (4 * 2));  // 01 = pull-up

    // GPIOD->MODER &= ~(3 << (12 * 2));
    // GPIOD->MODER |= (1 << (12 * 2));
    //
    // GPIOD->MODER &= ~(3 << (13 * 2));
    // GPIOD->MODER |= (1 << (13 * 2));
    //
    // GPIOD->MODER &= ~(3 << (14 * 2));
    // GPIOD->MODER |= (1 << (14 * 2));
}
