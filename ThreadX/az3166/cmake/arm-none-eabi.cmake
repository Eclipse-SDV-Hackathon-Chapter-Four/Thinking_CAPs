# SPDX-License-Identifier: Apache-2.0
# GNU Arm Embedded toolchain for the MXChip AZ3166 (STM32F412RG, Cortex-M4).
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)
set(CMAKE_C_COMPILER arm-none-eabi-gcc)
set(CMAKE_ASM_COMPILER arm-none-eabi-gcc)
set(CMAKE_OBJCOPY arm-none-eabi-objcopy CACHE FILEPATH "objcopy")
set(CMAKE_SIZE arm-none-eabi-size CACHE FILEPATH "size")
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

# The application uses no floating point, so the FPU stays disabled and the
# ThreadX port does not need to preserve FPU context.
set(MCU_FLAGS "-mcpu=cortex-m4 -mthumb -mfloat-abi=soft")
set(CMAKE_C_FLAGS_INIT "${MCU_FLAGS} -ffunction-sections -fdata-sections")
set(CMAKE_ASM_FLAGS_INIT "${MCU_FLAGS} -x assembler-with-cpp")
set(CMAKE_EXE_LINKER_FLAGS_INIT "${MCU_FLAGS} -Wl,--gc-sections --specs=nano.specs --specs=nosys.specs")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
