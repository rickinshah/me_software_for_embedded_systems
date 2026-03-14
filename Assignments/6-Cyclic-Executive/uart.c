#include "uart.h"
#include "stm32f4xx.h"

void UART2_Init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;

    GPIOA->MODER |= (2 << (2 * 2)) | (2 << (3 * 2));
    GPIOA->AFR[0] |= (7 << (2 * 4)) | (7 << (3 * 4));

    USART2->BRR = 0x683; /* 9600 baud @ 16MHz APB1*/
    USART2->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
}

void UART_SendByte(uint8_t data) {
    while (!(USART2->SR & USART_SR_TXE));
    USART2->DR = data;
}

void UART_SendArray(uint8_t* buf, uint16_t len) {
    uint16_t i;
    for (i = 0; i < len; i++) UART_SendByte(buf[i]);
}

void UART_SendNumber(uint32_t num) {
    char buf[10];
    int  i = 0;

    if (num == 0) {
        UART_SendByte('0');
        return;
    }

    while (num > 0) {
        buf[i++] = '0' + (num % 10);
        num /= 10;
    }

    while (i--) {
        UART_SendByte(buf[i]);
    }
}
