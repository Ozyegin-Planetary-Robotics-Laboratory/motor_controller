# motor_controller_node.py

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from gpiozero import PWMOutputDevice
import RPi.GPIO as GPIO

class MotorController(Node):
    def __init__(self):
        super().__init__('motor_controller')
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        # Define your motor pins here
        self.left_motor_forward = PWMOutputDevice(17)
        self.left_motor_backward = PWMOutputDevice(18)
        self.right_motor_forward = PWMOutputDevice(22)
        self.right_motor_backward = PWMOutputDevice(23)

    def listener_callback(self, msg):
        linear = msg.linear.x
        angular = msg.angular.z

        # Calculate motor speeds
        left_speed = linear - angular
        right_speed = linear + angular

        # Normalize speeds to -1 to 1
        max_speed = max(abs(left_speed), abs(right_speed))
        if max_speed > 1.0:
            left_speed /= max_speed
            right_speed /= max_speed

        # Control left motor
        if left_speed >= 0:
            self.left_motor_forward.value = left_speed
            self.left_motor_backward.value = 0
        else:
            self.left_motor_forward.value = 0
            self.left_motor_backward.value = -left_speed

        # Control right motor
        if right_speed >= 0:
            self.right_motor_forward.value = right_speed
            self.right_motor_backward.value = 0
        else:
            self.right_motor_forward.value = 0
            self.right_motor_backward.value = -right_speed

def main(args=None):
    rclpy.init(args=args)
    motor_controller = MotorController()
    try:
        rclpy.spin(motor_controller)
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        motor_controller.destroy_node()
        rclpy.shutdown()
        GPIO.cleanup()

if __name__ == '__main__':
    main()
