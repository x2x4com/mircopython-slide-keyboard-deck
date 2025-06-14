import machine
import utime


class RunTime:
    limited_close: machine.Pin
    limited_open: machine.Pin
    trigger_close: machine.Pin
    trigger_open: machine.Pin
    led: machine.Pin
    motor_pwm: machine.PWM
    motor_pin1: machine.Pin
    motor_pin2: machine.Pin
    _is_motor_running: bool = False

    def close(self):
        print(f"Start close keyboard deck... {self.limited_open.value()}")
        # 运行电机拉回直到碰到限位开关
        # IN1 低 IN2 高，电机正转
        while self.limited_close.value() == 0:
            print(f"closing... {self.limited_close.value()}")
            self.led.toggle()
            self.motor_start("close")
        print("Keyboard deck closed.")
        self.led.off()

    def open(self):
        print(f"Start open keyboard deck... {self.limited_open.value()}")
        # 运行电机推开直到碰到限位开关
        # IN1 高 IN2 低，电机反转
        while self.limited_open.value() == 0:
            print(f"opening... {self.limited_open.value()}")
            self.led.toggle()
            self.motor_start("open")
        print("Keyboard deck opened.")
        self.led.off()

    def motor_stop(self):
        if self._is_motor_running:
            print("Stopping motor.")
            self.motor_pin1.off()
            self.motor_pin2.off()
            self.motor_pwm.duty_u16(0)
            self._is_motor_running = False
    
    def motor_start(self, direction: str):
        if not self._is_motor_running:
            self.motor_pwm.duty_u16(20000)
            if direction == "close":
                print("Starting motor to close.")
                self.motor_pin1.on()
                self.motor_pin2.off()
            elif direction == "open":
                print("Starting motor to open.")
                self.motor_pin1.off()
                self.motor_pin2.on()
            self._is_motor_running = True
        if self._is_motor_running:
            if self.limited_close.value() == 1 and direction == "close":
                # 碰到限位开关，停止电机
                print("Motor stopped due to limit switch.")
                self.motor_stop()
            elif self.limited_open.value() == 1 and direction == "open":
                # 碰到限位开关，停止电机
                print("Motor stopped due to limit switch.")
                self.motor_stop()

    def run(self):
        # 实时检测联动开关状态
        pass
    
rt = RunTime()
# PULL_UP 上拉电阻， 低电平触发, 这时候按下为value 0, 松开为1
rt.limited_close = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)
rt.limited_open = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)
rt.trigger_close = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)
rt.trigger_open = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
rt.led = machine.Pin("LED", machine.Pin.OUT)
rt.motor_pwm = machine.PWM(machine.Pin(10), freq=1000, duty_u16=0)  # PWM pin for motor control
rt.motor_pin1 = machine.Pin(12, machine.Pin.OUT)
rt.motor_pin2 = machine.Pin(13, machine.Pin.OUT)

rt.motor_pin1.off()
rt.motor_pin2.off()
rt.led.off()

def limited_close_callback(pin):
    global rt
    print(f"limited_close pressed!, current value: {pin.value()}")
    rt.motor_stop()

def limited_open_callback(pin):
    global rt
    print(f"limited_open pressed!, current value: {pin.value()}")
    rt.motor_stop()

def trigger_close_callback(pin):
    global rt
    print(f"trigger_close pressed!, current value: {pin.value()}")
    rt.close()

def trigger_open_callback(pin):
    global rt
    print(f"trigger_open pressed!, current value: {pin.value()}")
    rt.open()

#rt.limited_close.irq(trigger=machine.Pin.IRQ_RISING, handler=limited_close_callback)
#rt.limited_open.irq(trigger=machine.Pin.IRQ_RISING, handler=limited_open_callback)
rt.trigger_close.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_close_callback)
rt.trigger_open.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_open_callback)

print("System is ready. Press buttons to trigger events.")
while True:
    rt.run()
    utime.sleep(0.25) 