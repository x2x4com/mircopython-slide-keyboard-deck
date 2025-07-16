import machine
import utime

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

    def run(self):
        # 实时检测联动开关状态
        print(f"Linked power state: {self.linked_power.value()}")
        print(f"Limited close state: {self.limited_close.value()}")
        print(f"Limited open state: {self.limited_open.value()}")
        print(f"Trigger close state: {self.trigger_close.value()}")
        print(f"Trigger open state: {self.trigger_open.value()}")
    
rt = RunTime()
# PULL_UP 上拉电阻， 低电平触发, 这时候按下为value 0, 松开为1
rt.limited_close = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)
rt.limited_open = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)
rt.linked_power = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)  # 联动开关
rt.trigger_close = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)
rt.trigger_open = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
rt.led = machine.Pin("LED", machine.Pin.OUT)


def limited_close_callback(pin):
    global rt
    print(f"limited_close pressed!, current value: {pin.value()}")

def limited_open_callback(pin):
    global rt
    print(f"limited_open pressed!, current value: {pin.value()}")

def trigger_close_callback(pin):
    global rt
    print(f"trigger_close pressed!, current value: {pin.value()}")

def trigger_open_callback(pin):
    global rt
    print(f"trigger_open pressed!, current value: {pin.value()}")

rt.limited_close.irq(trigger=machine.Pin.IRQ_RISING, handler=limited_close_callback)
rt.limited_open.irq(trigger=machine.Pin.IRQ_RISING, handler=limited_open_callback)
rt.trigger_close.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_close_callback)
rt.trigger_open.irq(trigger=machine.Pin.IRQ_RISING, handler=trigger_open_callback)

print("System is ready. Press buttons to trigger events.")
while True:
    rt.run()
    utime.sleep(0.25) 