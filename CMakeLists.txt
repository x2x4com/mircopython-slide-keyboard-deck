cmake_minimum_required(VERSION 3.13)

set(PICO_SDK_PATH /Users/jack/Git/pico/embedded/pico-sdk)

# 初始化PICO SDK
include(pico_sdk_import.cmake)

project(slide-keyboard-deck C CXX ASM)

# 初始化SDK
pico_sdk_init()

# 添加可执行文件
add_executable(slide-keyboard-deck 
    main.c
)

# 添加Pico标准库
target_link_libraries(slide-keyboard-deck pico_stdlib hardware_pwm hardware_gpio hardware_irq)

# 创建UF2文件等
pico_add_extra_outputs(slide-keyboard-deck)

# 启用USB输出（可选）
pico_enable_stdio_usb(slide-keyboard-deck 1)
pico_enable_stdio_uart(slide-keyboard-deck 0)