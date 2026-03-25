from booster_robotics_sdk_python import (
    ChannelFactory,
    B1RemoteControllerSubscriber,
    B1LocoClient,
    RobotMode,
    B1LowCmdPublisher,
    LowCmd,
    LowCmdType,
    MotorCmd,
    B1JointCnt,
    B1JointIndex,
    B1RemoteControllerStateSubscriber,
    B1LowStateSubscriber,
)

import time, sys

behv_cmd = "a"
K1_chair_state = 0


def handler(remote_controller_msg):
    """
    Docstring for handler function

    :param remote_controller_msg: Description

    Function meant to read input from gamepad and assign appropriate command to run custom behaviors.
    """
    if (
        remote_controller_msg.a == 1
        and remote_controller_msg.b == 0
        and K1_chair_state == 0
    ):
        # chair sit-down command
        K1_chair_state = 1
        print("sit-down command received")
        pass
    elif (
        remote_controller_msg.a == 1
        and remote_controller_msg.b == 1
        and K1_chair_state == 1
    ):
        # chair get-up command
        K1_chair_state = 0
        print("get-up command received")
        pass
    elif remote_controller_msg.a == 1 and remote_controller_msg.x == 1:
        # Ai chat command
        print("Ai chat command received")
        pass
    elif remote_controller_msg.a == 1 and remote_controller_msg.y == 1:
        # story telling command
        print("story telling command received")
        pass
    elif remote_controller_msg.b == 1 and remote_controller_msg.x == 1:
        # music-dance command
        print("music-dance command received")
        pass
    elif remote_controller_msg.b == 1 and remote_controller_msg.y == 1:
        # sport acting command
        print("sport acting command received")
        pass

    # print(
    #     f"\nButton values: A-{remote_controller_msg.a}|B-{remote_controller_msg.b}\
    #       |X-{remote_controller_msg.x}|Y-{remote_controller_msg.y}|LB-{remote_controller_msg.lb}\
    #       |RB-{remote_controller_msg.rb}|LT-{remote_controller_msg.lt}|RT-{remote_controller_msg.rt}\
    #       |LS-{remote_controller_msg.ls}|RS-{remote_controller_msg.rs}|BACK-{remote_controller_msg.back}\
    #       |START-{remote_controller_msg.start}"
    # )
    # print(
    #     f"\nL Stick values: LX-{remote_controller_msg.lx}|LY-{remote_controller_msg.ly}\
    #       |RX-{remote_controller_msg.rx}|RY-{remote_controller_msg.ry}"
    # )
    # print(
    #     f"\nButton values: HAT_C-{remote_controller_msg.hat_c}|HAT_U-{remote_controller_msg.hat_u}\
    #       |HAT_D-{remote_controller_msg.hat_d}|HAT_L-{remote_controller_msg.hat_l}|HAT_R-{remote_controller_msg.hat_r}\
    #       |HAT_LU-{remote_controller_msg.hat_lu}|HAT_LD-{remote_controller_msg.hat_ld}|HAT_RU-{remote_controller_msg.hat_ru}\
    #       |HAT_RD-{remote_controller_msg.hat_rd}"
    # )


def main():

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)

    net_if = sys.argv[1]
    robot_name = sys.argv[2] if len(sys.argv) >= 3 else None

    # Initialize DDS
    ChannelFactory.Instance().Init(0, net_if)

    client = B1LocoClient()
    if robot_name:
        client.InitWithName(robot_name)
    else:
        client.Init()

    res = 0
    res = client.ChangeMode(RobotMode.kCustom)

    channel_subscriber = B1RemoteControllerSubscriber(handler)
    channel_subscriber.InitChannel()
    print("init handler")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
