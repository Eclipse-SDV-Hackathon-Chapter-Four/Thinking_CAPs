/* SPDX-License-Identifier: Apache-2.0 */
/* Pin map from the MXChip AZ3166 schematic / Eclipse ThreadX getting-started
 * board_init.h: Wi-Fi LED PB2, Azure LED PA15, user LED PC13, RGB R/G/B
 * PB4/PB3/PC7 (active high), USART6 TX/RX PA11/PA12 (AF8), I2C1 SCL/SDA
 * PB8/PB9 (AF4), SSD1306 at 0x3C. */
#include "board.h"
#include "board_clock.h"
#include <stdint.h>

#define REG(address) (*(volatile uint32_t *)(address))

#define RCC_BASE       0x40023800U
#define RCC_CR         REG(RCC_BASE + 0x00U)
#define RCC_PLLCFGR    REG(RCC_BASE + 0x04U)
#define RCC_CFGR       REG(RCC_BASE + 0x08U)
#define RCC_AHB1ENR    REG(RCC_BASE + 0x30U)
#define RCC_APB1ENR    REG(RCC_BASE + 0x40U)
#define RCC_APB1RSTR   REG(RCC_BASE + 0x20U)
#define RCC_APB2ENR    REG(RCC_BASE + 0x44U)
#define FLASH_ACR      REG(0x40023C00U)
#define PWR_CR         REG(0x40007000U)

#define GPIOA 0x40020000U
#define GPIOB 0x40020400U
#define GPIOC 0x40020800U
#define GPIO_MODER(port)   REG((port) + 0x00U)
#define GPIO_OTYPER(port)  REG((port) + 0x04U)
#define GPIO_OSPEEDR(port) REG((port) + 0x08U)
#define GPIO_PUPDR(port)   REG((port) + 0x0CU)
#define GPIO_BSRR(port)    REG((port) + 0x18U)
#define GPIO_AFR(port, n)  REG((port) + 0x20U + 4U * (n))

#define USART6_SR   REG(0x40011400U)
#define USART6_DR   REG(0x40011404U)
#define USART6_BRR  REG(0x40011408U)
#define USART6_CR1  REG(0x4001140CU)
#define USART_SR_ORE  (1U << 3)
#define USART_SR_RXNE (1U << 5)
#define USART_SR_TXE  (1U << 7)
#define USART_CR1_RE     (1U << 2)
#define USART_CR1_TE     (1U << 3)
#define USART_CR1_RXNEIE (1U << 5)
#define USART_CR1_TXEIE  (1U << 7)
#define USART_CR1_UE     (1U << 13)
#define USART6_IRQN 71U

#define I2C1_CR1   REG(0x40005400U)
#define I2C1_CR2   REG(0x40005404U)
#define I2C1_DR    REG(0x40005410U)
#define I2C1_SR1   REG(0x40005414U)
#define I2C1_SR2   REG(0x40005418U)
#define I2C1_CCR   REG(0x4000541CU)
#define I2C1_TRISE REG(0x40005420U)
#define OLED_ADDRESS 0x3CU

#define NVIC_ISER(n) REG(0xE000E100U + 4U * (n))
#define NVIC_IPR8(n) (*(volatile uint8_t *)(0xE000E400U + (n)))

static inline uint32_t irq_save(void)
{
    uint32_t primask;
    __asm volatile("mrs %0, primask\n cpsid i" : "=r"(primask) :: "memory");
    return primask;
}

static inline void irq_restore(uint32_t primask)
{
    __asm volatile("msr primask, %0" :: "r"(primask) : "memory");
}

static void pin_mode(uint32_t port, unsigned pin, unsigned mode, unsigned af)
{
    GPIO_MODER(port) = (GPIO_MODER(port) & ~(3U << (pin * 2U))) | (mode << (pin * 2U));
    GPIO_OSPEEDR(port) |= 2U << (pin * 2U);
    if (mode == 2U) {
        volatile uint32_t *afr = &GPIO_AFR(port, pin / 8U);
        *afr = (*afr & ~(0xFU << ((pin % 8U) * 4U))) | (af << ((pin % 8U) * 4U));
    }
}

static void pin_write(uint32_t port, unsigned pin, bool high)
{
    GPIO_BSRR(port) = high ? (1U << pin) : (1U << (pin + 16U));
}

static void clock_init(void)
{
    RCC_APB1ENR |= 1U << 28;                       /* PWR */
    PWR_CR = (PWR_CR & ~(3U << 14)) | (3U << 14);  /* Voltage scale 1 for 96 MHz */
    /* HSI 16 MHz RC (factory trimmed, ±1%) / M16 * N192 = 192 MHz VCO;
     * /P2 = 96 MHz, /Q4 = 48 MHz. */
    RCC_PLLCFGR = 16U | (192U << 6) | (0U << 16) | (4U << 24) | (2U << 28);
    RCC_CR |= 1U << 24;
    while (!(RCC_CR & (1U << 25))) {}
    FLASH_ACR = 3U | (1U << 8) | (1U << 9) | (1U << 10);  /* 3 WS, prefetch, caches */
    while ((FLASH_ACR & 0xFU) != 3U) {}
    RCC_CFGR = (RCC_CFGR & ~0xFCF3U) | (4U << 10) | 2U;  /* AHB /1, APB1 /2, APB2 /1, PLL */
    while (((RCC_CFGR >> 2) & 3U) != 2U) {}
}

void board_init(void)
{
    clock_init();
    RCC_AHB1ENR |= 7U;  /* GPIOA..C */
    pin_mode(GPIOB, 2, 1, 0);
    pin_mode(GPIOA, 15, 1, 0);
    pin_mode(GPIOC, 13, 1, 0);
    pin_mode(GPIOB, 4, 1, 0);
    pin_mode(GPIOB, 3, 1, 0);
    pin_mode(GPIOC, 7, 1, 0);
    board_lamps(false, false);
    board_link_led(false);
    board_heartbeat_led(false);
    pin_write(GPIOB, 3, false);
    pin_write(GPIOC, 7, false);

    RCC_APB2ENR |= 1U << 5;  /* USART6 */
    pin_mode(GPIOA, 11, 2, 8);
    pin_mode(GPIOA, 12, 2, 8);
    GPIO_PUPDR(GPIOA) = (GPIO_PUPDR(GPIOA) & ~(3U << 24)) | (1U << 24);  /* RX pull-up */
    USART6_BRR = (BOARD_APB2_HZ + BOARD_UART_BAUD / 2U) / BOARD_UART_BAUD;
    USART6_CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
}

void board_lamps(bool reverse, bool brake)
{
    pin_write(GPIOB, 4, brake);
    pin_write(GPIOC, 13, reverse);
}

void board_link_led(bool on) { pin_write(GPIOA, 15, on); }
void board_heartbeat_led(bool on) { pin_write(GPIOB, 2, on); }

void board_fault(void)
{
    irq_save();
    board_lamps(false, false);
    board_link_led(false);
    pin_write(GPIOC, 7, true);
    for (;;) {}
}

/* ---- USART6: interrupt-driven RX callback and TX ring ---- */
#define TX_RING 1024U
static unsigned char tx_ring[TX_RING];
static volatile unsigned tx_head, tx_tail;  /* head: threads, tail: ISR */
static void (*rx_callback)(unsigned char);
static volatile unsigned long overruns;

void board_uart_start(void (*on_byte)(unsigned char byte))
{
    rx_callback = on_byte;
    (void)USART6_SR;
    (void)USART6_DR;
    NVIC_IPR8(USART6_IRQN) = 0x80U;  /* Below SysTick (0x40), above PendSV (0xFF) */
    NVIC_ISER(USART6_IRQN / 32U) = 1U << (USART6_IRQN % 32U);
    uint32_t state = irq_save();
    USART6_CR1 |= USART_CR1_RXNEIE;
    irq_restore(state);
}

bool board_uart_write(const char *data, size_t length)
{
    unsigned head = tx_head;
    if (length > TX_RING - 1U - ((head - tx_tail) % TX_RING)) return false;
    for (size_t index = 0; index < length; ++index) {
        tx_ring[head] = (unsigned char)data[index];
        head = (head + 1U) % TX_RING;
    }
    __asm volatile("dmb" ::: "memory");
    tx_head = head;
    uint32_t state = irq_save();
    USART6_CR1 |= USART_CR1_TXEIE;
    irq_restore(state);
    return true;
}

unsigned long board_uart_overruns(void) { return overruns; }

void USART6_IRQHandler(void)
{
    uint32_t status = USART6_SR;
    if (status & (USART_SR_RXNE | USART_SR_ORE)) {
        unsigned char byte = (unsigned char)USART6_DR;  /* SR then DR read clears ORE */
        if (status & USART_SR_ORE) ++overruns;
        if ((status & USART_SR_RXNE) && rx_callback) rx_callback(byte);
    }
    if ((USART6_CR1 & USART_CR1_TXEIE) && (status & USART_SR_TXE)) {
        if (tx_tail == tx_head) {
            USART6_CR1 &= ~USART_CR1_TXEIE;
        } else {
            USART6_DR = tx_ring[tx_tail];
            tx_tail = (tx_tail + 1U) % TX_RING;
        }
    }
}

/* ---- I2C1 master (polling with bounded waits) and SSD1306 ---- */
static bool i2c_wait(uint32_t mask)
{
    for (unsigned spin = 0; spin < 200000U; ++spin) {
        uint32_t status = I2C1_SR1;
        if (status & (1U << 10)) break;  /* AF: no acknowledge */
        if (status & mask) return true;
    }
    I2C1_SR1 = 0;
    I2C1_CR1 |= 1U << 9;  /* STOP */
    return false;
}

static bool i2c_write(unsigned char control, const unsigned char *data, size_t length)
{
    I2C1_CR1 |= 1U << 8;  /* START */
    if (!i2c_wait(1U << 0)) return false;
    I2C1_DR = OLED_ADDRESS << 1;
    if (!i2c_wait(1U << 1)) return false;
    (void)I2C1_SR2;
    I2C1_DR = control;
    for (size_t index = 0; index < length; ++index) {
        if (!i2c_wait(1U << 7)) return false;
        I2C1_DR = data[index];
    }
    if (!i2c_wait(1U << 2)) return false;  /* BTF */
    I2C1_CR1 |= 1U << 9;
    return true;
}

bool board_oled_init(void)
{
    RCC_AHB1ENR |= 1U << 1;
    RCC_APB1ENR |= 1U << 21;  /* I2C1 */
    RCC_APB1RSTR |= 1U << 21;
    RCC_APB1RSTR &= ~(1U << 21);
    for (unsigned pin = 8; pin <= 9; ++pin) {
        GPIO_OTYPER(GPIOB) |= 1U << pin;
        GPIO_PUPDR(GPIOB) = (GPIO_PUPDR(GPIOB) & ~(3U << (pin * 2U))) | (1U << (pin * 2U));
        pin_mode(GPIOB, pin, 2, 4);
    }
    I2C1_CR2 = BOARD_APB1_HZ / 1000000U;
    I2C1_CCR = (1U << 15) | (BOARD_APB1_HZ / (3U * 400000U));  /* Fast mode 400 kHz */
    I2C1_TRISE = BOARD_APB1_HZ / 1000000U * 300U / 1000U + 1U;
    I2C1_CR1 = 1U;  /* PE */
    static const unsigned char init[] = {
        0xAE, 0x20, 0x00, 0xC8, 0x40, 0x81, 0xFF, 0xA1, 0xA6, 0xA8, 0x3F, 0xA4,
        0xD3, 0x00, 0xD5, 0xF0, 0xD9, 0x22, 0xDA, 0x12, 0xDB, 0x20, 0x8D, 0x14, 0xAF};
    return i2c_write(0x00, init, sizeof(init));
}

bool board_oled_page(unsigned page, const unsigned char columns[128])
{
    const unsigned char address[] = {(unsigned char)(0xB0U + page), 0x00, 0x10};
    return page < 8U && i2c_write(0x00, address, sizeof(address)) && i2c_write(0x40, columns, 128);
}
