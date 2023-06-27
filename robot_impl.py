import time
from robotGPIO import Chassis, ChassisPins, Gimbal, GimbalPins, Led
import robot_pb2
import robot_pb2_grpc
from loguru import logger

try:
    import pigpio
except ModuleNotFoundError:
    import fake_pigpio as pigpio
    logger.debug("Using fake pigpio in robot_impl module.")

class HardwareController:
    def __init__(self) -> None:
        self.pi = pigpio.pi()
        self.chassis = Chassis(self.pi, ChassisPins(
            left_motor_CW_pin=5,
            left_motor_CCW_pin=6,
            left_motor_PWM_pin=13,
            right_motor_CW_pin=23,
            right_motor_CCW_pin=24,
            right_motor_PWM_pin=12
        ))
        self.gimbal = Gimbal(self.pi, GimbalPins(
            vertical_servo_pin=27,
            horizontal_servo_pin=22
        ))
        self.laser = Led(self.pi, 26)

class RobotServicer(robot_pb2_grpc.RobotServicer):
    def __init__(self) -> None:
        super().__init__()
        self.hc = HardwareController()

    def SetThrust(self, request, context):
        self.hc.chassis.write(request.LeftMotor, request.RightMotor)
        return robot_pb2.Status(Ok=False, Timestamp=time.time())

    def SetGimbal(self, request, context):
        self.hc.gimbal.write(request.HorizontalAngle, request.VerticalAngle)
        return robot_pb2.Status(Ok=False, Timestamp=time.time())

    def SetLaser(self, request, context):
        self.hc.laser.write(request.Power)
        return robot_pb2.Status(Ok=False, Timestamp=time.time())