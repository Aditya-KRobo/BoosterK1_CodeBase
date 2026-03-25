import time
from booster_robotics_sdk_python import (
    ChannelFactory,
    B1LowCmdPublisher,
    LowCmd,
    LowCmdType,
    MotorCmd,
    RobotMode,
    B1LocoClient,
    # B1JointCnt,
    # B1JointIndex,
)

SLEEP_TIME = 1


def main():
    ChannelFactory.Instance().Init(0)
    channel_publisher = B1LowCmdPublisher()
    channel_publisher.InitChannel()
    motor_cmds = [MotorCmd() for _ in range(22)]

    client = B1LocoClient()
    client.Init()

    DQ = 0.5
    TAU = 0.2

    q_data_orig = [
        0.00,
        0.00,
        0.25,
        -1.40,
        0.00,
        -0.50,
        0.25,
        1.40,
        0.00,
        0.50,
        0.0,
        -0.1,
        0.0,
        0.0,
        0.2,
        0.137,
        0.125,
        -0.1,
        0.0,
        0.0,
        0.2,
        0.137,
        0.125,
    ]
    kp_data = [
        5.0,
        5.0,
        40.0,
        50.0,
        20.0,
        10.0,
        40.0,
        50.0,
        20.0,
        10.0,
        100.0,
        350.0,
        350.0,
        180.0,
        350.0,
        450.0,
        450.0,
        350.0,
        350.0,
        180.0,
        350.0,
        450.0,
        450.0,
    ]
    kd_data = [
        0.1,
        0.1,
        0.5,
        1.5,
        0.2,
        0.2,
        0.5,
        1.5,
        0.2,
        0.2,
        5.0,
        7.5,
        7.5,
        3.0,
        5.5,
        0.5,
        0.5,
        7.5,
        7.5,
        3.0,
        5.5,
        0.5,
        0.5,
    ]

    q_data = q_data_orig.copy()

    low_cmd = LowCmd()
    low_cmd.cmd_type = LowCmdType.PARALLEL
    low_cmd.motor_cmd = motor_cmds

    for i in range(22):
        low_cmd.motor_cmd[i].q = q_data_orig[i]
        low_cmd.motor_cmd[i].dq = DQ
        low_cmd.motor_cmd[i].tau = TAU
        low_cmd.motor_cmd[i].kp = kp_data[i]
        low_cmd.motor_cmd[i].kd = kd_data[i]
        low_cmd.motor_cmd[i].weight = 0.0

    channel_publisher.Write(low_cmd)

    while True:
        low_cmd = LowCmd()
        low_cmd.cmd_type = LowCmdType.PARALLEL
        low_cmd.motor_cmd = motor_cmds

        joint_num = input(
            "Please enter the joint you want to control (between 1-23) : "
        )
        client.ChangeMode(RobotMode.kCustom)

        # joint_val = input(
        #     f"Please enter the joint value you want to set the joint to (currently {q_data[int(joint_num)-1]}) : "
        # )

        while True:
            action = input("Should the joint be increased, decreased, reset or quit? (i/d/r/q): ")
            if action == 'r':
                for i in range(22):
                    low_cmd.motor_cmd[i].q = q_data_orig[i]
                    low_cmd.motor_cmd[i].dq = DQ
                    low_cmd.motor_cmd[i].tau = TAU
                    low_cmd.motor_cmd[i].kp = kp_data[i]
                    low_cmd.motor_cmd[i].kd = kd_data[i]
                    low_cmd.motor_cmd[i].weight = 0.0

                channel_publisher.Write(low_cmd)
                break

            elif action == 'i':
                if i == int(joint_num) - 1:
                    q_data[int(joint_num) - 1] += 0.1
                    low_cmd.motor_cmd[i].q = q_data[int(joint_num) - 1]
                    low_cmd.motor_cmd[i].dq = DQ
                    low_cmd.motor_cmd[i].tau = TAU
                    low_cmd.motor_cmd[i].kp = kp_data[i]
                    low_cmd.motor_cmd[i].kd = kd_data[i]
                    low_cmd.motor_cmd[i].weight = 0.0
                else:
                    low_cmd.motor_cmd[i].q = q_data[i]
                    low_cmd.motor_cmd[i].dq = DQ
                    low_cmd.motor_cmd[i].tau = TAU
                    low_cmd.motor_cmd[i].kp = kp_data[i]
                    low_cmd.motor_cmd[i].kd = kd_data[i]
                    low_cmd.motor_cmd[i].weight = 0.0

                channel_publisher.Write(low_cmd)
            
            
            elif action == 'd':
                if i == int(joint_num) - 1:
                    q_data[int(joint_num) - 1] -= 0.1
                    low_cmd.motor_cmd[i].q = q_data[int(joint_num) - 1]
                    low_cmd.motor_cmd[i].dq = DQ
                    low_cmd.motor_cmd[i].tau = TAU
                    low_cmd.motor_cmd[i].kp = kp_data[i]
                    low_cmd.motor_cmd[i].kd = kd_data[i]
                    low_cmd.motor_cmd[i].weight = 0.0
                else:
                    low_cmd.motor_cmd[i].q = q_data[i]
                    low_cmd.motor_cmd[i].dq = DQ
                    low_cmd.motor_cmd[i].tau = TAU
                    low_cmd.motor_cmd[i].kp = kp_data[i]
                    low_cmd.motor_cmd[i].kd = kd_data[i]
                    low_cmd.motor_cmd[i].weight = 0.0

                channel_publisher.Write(low_cmd)
            
            elif action == 'q':
                print("Exiting joint manipulation...")
                break
            
            else:
                print("Invalid input. Please enter 'i', 'd', 'r', or 'q'.")
                for i in range(22):
                    low_cmd.motor_cmd[i].q = q_data_orig[i]
                    low_cmd.motor_cmd[i].dq = DQ
                    low_cmd.motor_cmd[i].tau = TAU
                    low_cmd.motor_cmd[i].kp = kp_data[i]
                    low_cmd.motor_cmd[i].kd = kd_data[i]
                    low_cmd.motor_cmd[i].weight = 0.0

                channel_publisher.Write(low_cmd)
                break


        
        # for i in range(22):

        #     if i == int(joint_num) - 1:
        #         q_data[i] = float(joint_val)
        #         low_cmd.motor_cmd[i].q = float(joint_val)
        #         low_cmd.motor_cmd[i].dq = 0.5
        #         low_cmd.motor_cmd[i].tau = 0.2
        #         low_cmd.motor_cmd[i].kp = kp_data[i]
        #         low_cmd.motor_cmd[i].kd = kd_data[i]
        #         low_cmd.motor_cmd[i].weight = 0.0
        #     else:
        #         low_cmd.motor_cmd[i].q = q_data[i]
        #         low_cmd.motor_cmd[i].dq = 0.5
        #         low_cmd.motor_cmd[i].tau = 0.2
        #         low_cmd.motor_cmd[i].kp = kp_data[i]
        #         low_cmd.motor_cmd[i].kd = kd_data[i]
        #         low_cmd.motor_cmd[i].weight = 0.0

        channel_publisher.Write(low_cmd)
        # print("Publish...")
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
