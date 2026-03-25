from booster_robotics_sdk_python import (
    ChannelFactory,
    B1RemoteControllerSubscriber,
)
import time


def handler(remote_controller_msg):
    """
    Docstring for handler function

    :param remote_controller_msg: Description

    Function meant to read and echo out gamepad buttons, triggers and joystick inputs.
    """
    print("Received message:")
    print(
        f"\nButton values: A-{remote_controller_msg.a}|B-{remote_controller_msg.b}\
          |X-{remote_controller_msg.x}|Y-{remote_controller_msg.y}|LB-{remote_controller_msg.lb}\
          |RB-{remote_controller_msg.rb}|LT-{remote_controller_msg.lt}|RT-{remote_controller_msg.rt}\
          |LS-{remote_controller_msg.ls}|RS-{remote_controller_msg.rs}|BACK-{remote_controller_msg.back}\
          |START-{remote_controller_msg.start}"
    )
    print(
        f"\nL Stick values: LX-{remote_controller_msg.lx}|LY-{remote_controller_msg.ly}\
          |RX-{remote_controller_msg.rx}|RY-{remote_controller_msg.ry}"
    )

    print(
        f"\nButton values: HAT_C-{remote_controller_msg.hat_c}|HAT_U-{remote_controller_msg.hat_u}\
          |HAT_D-{remote_controller_msg.hat_d}|HAT_L-{remote_controller_msg.hat_l}|HAT_R-{remote_controller_msg.hat_r}\
          |HAT_LU-{remote_controller_msg.hat_lu}|HAT_LD-{remote_controller_msg.hat_ld}|HAT_RU-{remote_controller_msg.hat_ru}\
          |HAT_RD-{remote_controller_msg.hat_rd}"
    )

    print("\nDone.....")


def main():
    ChannelFactory.Instance().Init(0)
    channel_subscriber = B1RemoteControllerSubscriber(handler)
    channel_subscriber.InitChannel()
    print("init handler")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
