/* SPDX-License-Identifier: Apache-2.0 */
/* STM32F412RG on the MXChip AZ3166: 1 MiB flash, 256 KiB SRAM. The ST-LINK
 * drag-and-drop programmer writes the binary at the start of flash. */
ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 1024K
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 256K
}

/* Main stack used by reset code and by ThreadX for interrupts. */
_main_stack_size = 4K;

SECTIONS
{
    .isr_vector : ALIGN(4)
    {
        _vectors = .;
        KEEP(*(.isr_vector))
    } > FLASH

    .text : ALIGN(4)
    {
        *(.text*)
        *(.rodata*)
        KEEP(*(.identity))
        KEEP(*(.init))
        KEEP(*(.fini))
        . = ALIGN(4);
    } > FLASH

    .ARM.exidx : { *(.ARM.exidx* .gnu.linkonce.armexidx.*) } > FLASH

    _sidata = LOADADDR(.data);
    .data : ALIGN(4)
    {
        _sdata = .;
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } > RAM AT > FLASH

    .bss (NOLOAD) : ALIGN(4)
    {
        _sbss = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > RAM

    .stack (NOLOAD) : ALIGN(8)
    {
        . += _main_stack_size;
        _estack = .;
    } > RAM

    /* First address after static RAM use; handed to ThreadX as free memory. */
    __RAM_segment_used_end__ = .;
    end = .;
    _end = .;
}
