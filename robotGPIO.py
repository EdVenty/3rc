from dataclasses import dataclass
from loguru import logger
try:
    import pigpio
except ModuleNotFoundError:
    import fake_pigpio as pigpio
    logger.debug("Using fake pigpio in robotGPIO module.")

def arduino_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def constrain(x, out_min, out_max):
    return out_min if x < out_min else out_max if x > out_max else x

class Component:
    def start(self):
        raise NotImplementedError('Method "start" must be implemented.')

    def stop(self):
        raise NotImplementedError('Method "stop" must be implemented.')

    def cleanup(self):
        raise NotImplementedError('Method "cleanup" must be implemented.')

    def read(self):
        raise NotImplementedError('Method "read" must be implemented for reading.')

    def write(self):
        raise NotImplementedError('Method "write" must be implemented for writing.')

class Motor(Component):
    def __init__(self, pi, pin_CW: int, pin_CCW: int, pin_PWM: int) -> None:
        self.pi = pi
        self.pin_CW = pin_CW
        self.pin_CCW = pin_CCW
        self.pin_PWM = pin_PWM

    def start(self):
        self.pi.set_mode(self.pin_CW, pigpio.OUTPUT)
        self.pi.set_mode(self.pin_CCW, pigpio.OUTPUT)
        self.pi.set_mode(self.pin_PWM, pigpio.OUTPUT)
        self.write(0)

    def write(self, force: int):
        if force > 0:
            self.pi.write(self.pin_CCW, 0)
            self.pi.write(self.pin_CW, 1)
        else:
            self.pi.write(self.pin_CW, 0)
            self.pi.write(self.pin_CCW, 1)
        self.pi.set_PWM_dutycycle(self.pin_PWM, constrain(abs(force), 0, 255))

    def stop(self):
        pass

    def cleanup(self):
        pass

@dataclass
class ChassisPins:
    left_motor_CW_pin: int
    left_motor_CCW_pin: int
    left_motor_PWM_pin: int
    right_motor_CW_pin: int
    right_motor_CCW_pin: int
    right_motor_PWM_pin: int

class Chassis(Component):
    def __init__(self, pi, pins: ChassisPins) -> None:
        self.pi = pi
        self.pins = pins
        self.left_motor = Motor(
            self.pi, 
            self.pins.left_motor_CW_pin, 
            self.pins.left_motor_CCW_pin,
            self.pins.left_motor_PWM_pin
        )
        self.right_motor = Motor(
            self.pi,
            self.pins.right_motor_CW_pin,
            self.pins.right_motor_CCW_pin,
            self.pins.right_motor_PWM_pin
        )

    def start(self):
        self.left_motor.start()
        self.right_motor.start()

    def write(self, left_force: int, right_force: int):
        self.left_motor.write(left_force)
        self.right_motor.write(right_force)

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

    def cleanup(self):
        self.left_motor.cleanup()
        self.right_motor.cleanup()

class Servo(Component):
    def __init__(self, pi, pin: int) -> None:
        self.pi = pi
        self.pin = pin

    def start(self):
        self.write(0)

    def write(self, angle: int):
        pwm = constrain(arduino_map(angle + 90, 0, 180, 500, 2500), 0, 2500)
        self.pi.set_servo_pulsewidth(self.pin, pwm)

    def stop(self):
        pass

    def cleanup(self):
        pass

@dataclass
class GimbalPins:
    vertical_servo_pin: int
    horizontal_servo_pin: int

class Gimbal(Component):
    def __init__(self, pi, pins: GimbalPins) -> None:
        self.pi = pi
        self.pins = pins
        self.vertical_servo = Servo(self.pi, self.pins.vertical_servo_pin)
        self.horizontal_servo = Servo(self.pi, self.pins.horizontal_servo_pin)

    def start(self):
        self.vertical_servo.start()
        self.horizontal_servo.start()

    def write(self, horizontal_angle: int, vertical_angle: int):
        self.horizontal_servo.write(horizontal_angle)
        self.vertical_servo.write(vertical_angle)

    def stop(self):
        self.horizontal_servo.stop()
        self.vertical_servo.stop()

    def cleanup(self):
        self.horizontal_servo.cleanup()
        self.vertical_servo.cleanup()

class Led(Component):
    def __init__(self, pi, pin: int) -> None:
        self.pi = pi
        self.pin = pin

    def start(self):
        self.pi.set_mode(self.pin, pigpio.OUTPUT)

    def write(self, duty: int):
        self.pi.set_PWM_dutycycle(self.pin, duty)

    def stop(self):
        pass

    def cleanup(self):
        pass
