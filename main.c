#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/pwm.h"
#include "hardware/irq.h"

// 常量定义
#define MOTOR_SPEED 65535
#define MOTOR_FREQUENCY 500
#define MOTOR_SPEED_OPEN 10000
#define MOTOR_SPEED_CLOSE 10000

// GPIO引脚定义
#define LIMITED_CLOSE_PIN 15
#define LIMITED_OPEN_PIN 14
#define LINKED_POWER_PIN 18
#define TRIGGER_CLOSE_PIN 17
#define TRIGGER_OPEN_PIN 16
#define LED_PIN PICO_DEFAULT_LED_PIN
#define MOTOR_PWM_PIN 10
#define MOTOR_PIN1 12
#define MOTOR_PIN2 13
#define BLING_LED_PIN 1

// 运行状态结构体
typedef struct {
    bool is_motor_running;
    bool is_manual_control;
    uint16_t motor_speed;
    uint16_t motor_speed_open;
    uint16_t motor_speed_close;
} RuntimeState;

RuntimeState rt_state = {
    .is_motor_running = false,
    .is_manual_control = false,
    .motor_speed = MOTOR_SPEED,
    .motor_speed_open = MOTOR_SPEED_OPEN,
    .motor_speed_close = MOTOR_SPEED_CLOSE
};

static char event_str[128];

static const char *gpio_irq_str[] = {
        "LEVEL_LOW",  // 0x1
        "LEVEL_HIGH", // 0x2
        "EDGE_FALL",  // 0x4
        "EDGE_RISE"   // 0x8
};

// 函数声明
void bling_led_on(void);
void bling_led_off(void);
bool get_manual_control(void);
void set_manual_control_on(void);
void set_manual_control_off(void);
bool is_closed(void);
bool is_opened(void);
void close_deck(void);
void open_deck(void);
void motor_stop(void);
// void limited_close_callback(uint gpio, uint32_t events);
// void limited_open_callback(uint gpio, uint32_t events);
// void trigger_close_callback(uint gpio, uint32_t events);
// void trigger_open_callback(uint gpio, uint32_t events);
void limited_close_callback(void);
void limited_open_callback(void);
void trigger_close_callback(void);
void trigger_open_callback(void);
void gpio_event_string(char *buf, uint32_t events);
void gpio_irq_handler(uint gpio, uint32_t events);



// LED控制函数
void bling_led_on(void) {
    gpio_put(BLING_LED_PIN, 1);
}

void bling_led_off(void) {
    gpio_put(BLING_LED_PIN, 0);
}

// 手动控制状态管理
bool get_manual_control(void) {
    return rt_state.is_manual_control;
}

void set_manual_control_on(void) {
    if (!rt_state.is_manual_control) {
        rt_state.is_manual_control = true;
        // printf("Manual control mode enabled.\n");
    }
}

void set_manual_control_off(void) {
    if (rt_state.is_manual_control) {
        rt_state.is_manual_control = false;
        // printf("Manual control mode disabled.\n");
    }
}

// 限位开关检测
bool is_closed(void) {
    //printf("Limited close pin status: %d\n", gpio_get(LIMITED_CLOSE_PIN));
    return gpio_get(LIMITED_CLOSE_PIN);
}

bool is_opened(void) {
    //printf("Limited open pin status: %d\n", gpio_get(LIMITED_OPEN_PIN));
    return gpio_get(LIMITED_OPEN_PIN);
}

// 关闭
void close_deck(void) {
    //bling_led_on();
    //printf("start close motor...%s\n", is_closed() ? "(already closed)" : "");
    
    if (!gpio_get(LIMITED_CLOSE_PIN) && !rt_state.is_motor_running) {
        rt_state.is_motor_running = true;
        printf("Closing motor...\n");
        fflush(stdout);
        gpio_put(MOTOR_PIN1, 1);
        gpio_put(MOTOR_PIN2, 0);
        pwm_set_gpio_level(MOTOR_PWM_PIN, rt_state.motor_speed_close);
        //sleep_ms(100); // 添加小延迟避免过于频繁的循环
    } else {
        printf("Deck is already closed or motor is running.\n");
    }
       
    
    //bling_led_off();
}

// 打开
void open_deck(void) {
    // bling_led_on();
    //printf("start open motor...%s\n", is_opened() ? "(already opened)" : "");

    if (!gpio_get(LIMITED_OPEN_PIN) && !rt_state.is_motor_running) {
        rt_state.is_motor_running = true;
        printf("Opening motor...\n");
        fflush(stdout);
        gpio_put(MOTOR_PIN1, 0);
        gpio_put(MOTOR_PIN2, 1);
        pwm_set_gpio_level(MOTOR_PWM_PIN, rt_state.motor_speed_open);
        //sleep_ms(100); // 添加小延迟避免过于频繁的循环
    } else {
        printf("Deck is already opened or motor is running.\n");
    }
    
    //bling_led_off();
}

// 停止电机
void motor_stop(void) {
    printf("Stopping motor.\n");
    fflush(stdout);
    gpio_put(MOTOR_PIN1, 0);
    gpio_put(MOTOR_PIN2, 0);
    pwm_set_gpio_level(MOTOR_PWM_PIN, 0);
    rt_state.is_motor_running = false;
}


void gpio_irq_handler(uint gpio, uint32_t events) {
    gpio_event_string(event_str, events);
    //sleep_ms(100);
    // printf("GPIO %d %s %s\n", gpio, event_str, gpio_get(gpio) ? "HIGH" : "LOW");
    // printf("LIMITED_CLOSE_PIN: %s\n", gpio_get(LIMITED_CLOSE_PIN) ? "HIGH" : "LOW");
    // fflush(stdout);
    // printf("LIMITED_OPEN_PIN: %s\n", gpio_get(LIMITED_OPEN_PIN) ? "HIGH" : "LOW");
    // fflush(stdout);
    // printf("TRIGGER_CLOSE_PIN: %s\n", gpio_get(TRIGGER_CLOSE_PIN) ? "HIGH" : "LOW");
    // fflush(stdout);
    // printf("TRIGGER_OPEN_PIN: %s\n", gpio_get(TRIGGER_OPEN_PIN) ? "HIGH" : "LOW");
    // fflush(stdout);
    if rt_state.is_motor_running {
        // 如果电机正在运行，忽略中断
        return;
    }
    // 根据GPIO引脚调用相应的回调函数
    if (gpio == LIMITED_CLOSE_PIN && gpio_get(gpio)) {
        motor_stop();
    } else if (gpio == LIMITED_OPEN_PIN && gpio_get(gpio)) {
        motor_stop();
    } else if (gpio == TRIGGER_CLOSE_PIN && !gpio_get(gpio)) {
        close_deck();
    } else if (gpio == TRIGGER_OPEN_PIN && !gpio_get(gpio)) {
        open_deck();
    }
}

// 主运行函数
void run(void) {
    if (!gpio_get(LINKED_POWER_PIN)) {
        // 联动开关未接通，关闭
        close_deck();
        return;
    }
    if (gpio_get(LINKED_POWER_PIN)&& !get_manual_control()) {
        open_deck();
        return;
    }
}

void gpio_event_string(char *buf, uint32_t events) {
    for (uint i = 0; i < 4; i++) {
        uint mask = (1 << i);
        if (events & mask) {
            // Copy this event string into the user string
            const char *event_str = gpio_irq_str[i];
            while (*event_str != '\0') {
                *buf++ = *event_str++;
            }
            events &= ~mask;

            // If more events add ", "
            if (events) {
                *buf++ = ',';
                *buf++ = ' ';
            }
        }
    }
    *buf++ = '\0';
}

int main() {
    rt_state.is_motor_running = false;
    // 初始化标准库
    stdio_init_all();
    
    // 初始化GPIO引脚
    gpio_init(LIMITED_CLOSE_PIN);
    gpio_set_dir(LIMITED_CLOSE_PIN, GPIO_IN);
    gpio_pull_down(LIMITED_CLOSE_PIN);
    
    gpio_init(LIMITED_OPEN_PIN);
    gpio_set_dir(LIMITED_OPEN_PIN, GPIO_IN);
    gpio_pull_down(LIMITED_OPEN_PIN);
    
    gpio_init(LINKED_POWER_PIN);
    gpio_set_dir(LINKED_POWER_PIN, GPIO_IN);
    gpio_pull_down(LINKED_POWER_PIN);
    
    gpio_init(TRIGGER_CLOSE_PIN);
    gpio_set_dir(TRIGGER_CLOSE_PIN, GPIO_IN);
    gpio_pull_down(TRIGGER_CLOSE_PIN);
    
    gpio_init(TRIGGER_OPEN_PIN);
    gpio_set_dir(TRIGGER_OPEN_PIN, GPIO_IN);
    gpio_pull_down(TRIGGER_OPEN_PIN);
    
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    
    gpio_init(MOTOR_PIN1);
    gpio_set_dir(MOTOR_PIN1, GPIO_OUT);
    
    gpio_init(MOTOR_PIN2);
    gpio_set_dir(MOTOR_PIN2, GPIO_OUT);
    
    gpio_init(BLING_LED_PIN);
    gpio_set_dir(BLING_LED_PIN, GPIO_OUT);
    
    // 初始化PWM
    gpio_set_function(MOTOR_PWM_PIN, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(MOTOR_PWM_PIN);
    pwm_set_wrap(slice_num, 3);
    // pwm_set_wrap(slice_num, 65535);
    pwm_set_clkdiv(slice_num, 125.0f / MOTOR_FREQUENCY);
    pwm_set_enabled(slice_num, true);
    
    gpio_set_irq_enabled_with_callback(LIMITED_CLOSE_PIN, GPIO_IRQ_EDGE_RISE, true, &gpio_irq_handler);
    gpio_set_irq_enabled_with_callback(LIMITED_OPEN_PIN, GPIO_IRQ_EDGE_RISE, true, &gpio_irq_handler);
    gpio_set_irq_enabled_with_callback(TRIGGER_CLOSE_PIN, GPIO_IRQ_EDGE_RISE, true, &gpio_irq_handler);
    gpio_set_irq_enabled_with_callback(TRIGGER_OPEN_PIN, GPIO_IRQ_EDGE_RISE, true, &gpio_irq_handler);
    
    // 初始状态设置
    gpio_put(MOTOR_PIN1, 0);
    gpio_put(MOTOR_PIN2, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(BLING_LED_PIN, 1);
    
    printf("System is ready. Press buttons to trigger events.\n");
    
    while (true) {
        // 主循环中可以调用run函数，但根据原代码注释，这里被注释掉了
        // run();
        sleep_ms(1000);
    }
    
    return 0;
}