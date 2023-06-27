from loguru import logger

OUTPUT = 'output'
INPUT = 'input'
LOW = 0
HIGH = 1

description = {
    LOW: 'low',
    HIGH: 'high'
}

class Pi:
    def set_mode(self, pin: int, mode):
        logger.debug(f"Setting mode of pin {pin} to a \"{mode}\".")

    def write(self, pin: int, signal: int):
        logger.debug(f"Writing \"{signal}\" ({description[signal]}) to a pin {pin}.")

    def set_PWM_dutycycle(self, pin: int, duty: int):
        logger.debug(f"Setting PWM dutycycle of pin {pin} to a \"{duty}\".")

    def set_servo_pulsewidth(self, pin: int, pulsewidth: int):
        logger.debug(f"Setting pulsewidth of pin {pin} to a {pulsewidth}.")

def pi():
    return Pi()