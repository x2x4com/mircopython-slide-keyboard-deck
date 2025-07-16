import machine
import utime

MOTOR_SPEED = 65535 # 电机速度
MOTOR_FREQUENCY = 500 # 电机频率
MOTOR_SPEED_OPEN = 60000 # 电机打开速度
MOTOR_SPEED_CLOSE = 30000 # 电机关闭速度

class RunTime:
    limited_close: machine.Pin
    limited_open: machine.Pin
    trigger_close: machine.Pin
    trigger_open: machine.Pin
    linked_power: machine.Pin
    led: machine.Pin
    motor_pwm: machine.PWM
    motor_pin1: machine.Pin
    motor_pin2: machine.Pin
    bling_led: machine.Pin
    _is_motor_running: bool = False
    _is_manual_control: bool = False
    _motor_speed: int = MOTOR_SPEED
    _motor_speed_open: int = MOTOR_SPEED_OPEN
    _motor_speed_close: int = MOTOR_SPEED_CLOSE

    def bling_led_on(self):
        self.bling_led.value(1)

    def bling_led_off(self):
        self.bling_led.value(0)

    def get_manual_control(self):
        return self._is_manual_control
    
    def set_manual_control_on(self):
        if not self._is_manual_control:
            # 如果之前没有手动控制，则开启手动控制
            self._is_manual_control = True
            print("Manual control mode enabled.")
    
    def set_manual_control_off(self):
        if self._is_manual_control:
            self._is_manual_control = False
            print("Manual control mode disabled.")

    def is_closed(self):
        return self.limited_close.value() == 1
    
    def is_opened(self):
        return self.limited_open.value() == 1

    def close(self):
        # 运行电机拉回直到碰到限位开关
        # IN1 低 IN2 高，电机正转
        # if self.is_closed():
        #     # print("Keyboard deck is already closed.")
        #     self.motor_stop()
        #     return
        self.bling_led_on()
        while not self.is_closed():
            #print(f"Start close keyboard deck... limited_close: {self.limited_close.value()}")
            #print(f"closing... {self.limited_close.value()}")
            #self.led.toggle()
            self.motor_start("close")
        #print("Keyboard deck closed.")
        #self.led.off()
        self.motor_stop()
        self.bling_led_off()

    def open(self):
        # 运行电机推开直到碰到限位开关
        # IN1 高 IN2 低，电机反转
        # if self.is_opened():
        #     # print("Keyboard deck is already opened.")
        #     self.motor_stop()
        #     return
        self.bling_led_on()
        while not self.is_opened():
            # print(f"Start open keyboard deck... limited_open: {self.limited_open.value()}")
            # print(f"opening... {self.limited_open.value()}")
            #self.led.toggle()
            self.motor_start("open")
        #print("Keyboard deck opened.")
        #self.led.off()
        self.motor_stop()
        self.bling_led_off()

    def motor_stop(self):
        #if self._is_motor_running:
        print("Stopping motor.")
        self.motor_pin1.off()
        self.motor_pin2.off()
        self.motor_pwm.duty_u16(0)
        self._is_motor_running = False
    
    def motor_start(self, direction: str):
        if self._is_motor_running:
            if self.is_closed() and direction == "close":
                # 碰到限位开关，停止电机
                print("Motor stopped due to limit switch.")
                self.motor_stop()
                self._is_motor_running = False
            elif self.is_opened and direction == "open":
                # 碰到限位开关，停止电机
                print("Motor stopped due to limit switch.")
                self.motor_stop()
                self._is_motor_running = False
        else:
            self._is_motor_running = True
            if direction == "close":
                print("Starting motor to close.")
                self.motor_pin1.on()
                self.motor_pin2.off()
                self.motor_pwm.duty_u16(self._motor_speed_close)
            elif direction == "open":
                print("Starting motor to open.")
                self.motor_pin1.off()
                self.motor_pin2.on()
                self.motor_pwm.duty_u16(self._motor_speed_open)
            

    def run(self):
        # debug
        #print(f"Linked power state: {self.linked_power.value()} | Limited close state: {self.limited_close.value()} | Limited open state: {self.limited_open.value()} | Trigger close state: {self.trigger_close.value()} | Trigger open state: {self.trigger_open.value()}")
        # 实时检测联动开关状态
        #print(f"Linked power state: {self.linked_power.value()}")
        if self.linked_power.value() == 0:
            # 联动开关未接通，关闭
            #self.set_manual_control_off()
            self.close()
            return
        if self.linked_power.value() == 1 and not self.get_manual_control():
            self.open()
            return
        
    
rt = RunTime()
# PULL_UP 上拉电阻， 低电平触发, 这时候按下为value 0, 松开为1
# PULL_DOWN 下拉电阻，高电平触发, 这时候按下为value 1, 松开为0
rt.limited_close = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)
rt.limited_open = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)
rt.linked_power = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_DOWN)  # 联动开关
rt.trigger_close = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_DOWN)
rt.trigger_open = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)
rt.led = machine.Pin("LED", machine.Pin.OUT)
rt.motor_pwm = machine.PWM(machine.Pin(10), freq=MOTOR_FREQUENCY, duty_u16=0)  # PWM pin for motor control
rt.motor_pin1 = machine.Pin(12, machine.Pin.OUT)
rt.motor_pin2 = machine.Pin(13, machine.Pin.OUT)
rt.bling_led = machine.Pin(1, machine.Pin.OUT)

rt.motor_pin1.off()
rt.motor_pin2.off()
rt.led.off()
rt.bling_led.high()

def limited_close_callback(pin):
    global rt
    #_v = pin.value()
    #if pin.value() == 1:
        #print(f"limited_close pressed!, current value: {_v}")
    rt.motor_stop()
 
def limited_open_callback(pin):
    global rt
    #_v = pin.value()
    #if pin.value() == 1:
        #print(f"limited_open pressed!, current value: {_v}")
    rt.motor_stop()

def trigger_close_callback(pin):
    global rt
    #_v = pin.value()
    if pin.value() == 1:  # 按下时触发
        #print(f"trigger_close pressed!, current value: {_v}")
        rt.set_manual_control_on()
        rt.close()

def trigger_open_callback(pin):
    global rt
    #_v = pin.value()
    if pin.value() == 1:  # 按下时触发
        #print(f"trigger_open pressed!, current value: {_v}")
        rt.set_manual_control_on()
        rt.open()

rt.limited_close.irq(trigger=machine.Pin.IRQ_RISING, handler=limited_close_callback)
rt.limited_open.irq(trigger=machine.Pin.IRQ_RISING, handler=limited_open_callback)
rt.trigger_close.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_close_callback)
rt.trigger_open.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_open_callback)

print("System is ready. Press buttons to trigger events.")
while True:
    #rt.run()
    utime.sleep(1) 