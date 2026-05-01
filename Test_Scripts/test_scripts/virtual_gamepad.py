# demo.py
# to execute this demo, please run following
# source /opt/ros/humble/setup.bash
# python demo.py

import rclpy
from rclpy.node import Node
from booster_robotics_sdk_python import RemoteControllerState
import os
import numpy as np
import string
import pyttsx3

class GamepadSubscriber(Node):

  def __init__(self):
    super().__init__('gamepad_subscriber')
    self.gamepad_subscription = self.create_subscription(
      RemoteControllerState,
      '/remote_controller_state',
      self.gamepad_listener_callback,
      10)

  def gamepad_listener_callback(self, msg):
    self.get_logger().info('Receiving gamepad state')
    print(msg.lx)


def main(args=None):
    rclpy.init(args=args)
    gamepad_subscriber = GamepadSubscriber()
    try:
        print("gamepad_demo running. Press Ctrl+C to stop.")
        rclpy.spin(gamepad_subscriber)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, stopping gamepad_demo...")
    finally:
        gamepad_subscriber.destroy_node()
        rclpy.shutdown()
        

if __name__ == '__main__':
    main()
