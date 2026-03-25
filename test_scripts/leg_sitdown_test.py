import time
from booster_robotics_sdk_python import (
    ChannelFactory,
    B1LowCmdPublisher,
    LowCmd,
    LowCmdType,
    MotorCmd,
    B1JointCnt,
    B1JointIndex,
)

SLEEP_TIME = 1


def main():
    ChannelFactory.Instance().Init(0)
    channel_publisher = B1LowCmdPublisher()
    channel_publisher.InitChannel()
    motor_cmds = [MotorCmd() for _ in range(B1JointCnt)]

    low_cmd = LowCmd()
    low_cmd.cmd_type = LowCmdType.PARALLEL
    low_cmd.motor_cmd = motor_cmds

    for i in range(B1JointCnt):
        low_cmd.motor_cmd[i].q = 0.0
        low_cmd.motor_cmd[i].dq = 0.0
        low_cmd.motor_cmd[i].tau = 0.0
        low_cmd.motor_cmd[i].kp = 4.0
        low_cmd.motor_cmd[i].kd = 1.0
        low_cmd.motor_cmd[i].weight = 1.0
        if i in [10, 16]:
            low_cmd.motor_cmd[i].q = -0.5
            low_cmd.motor_cmd[i].dq = 0.05
            low_cmd.motor_cmd[i].tau = 0.0
            low_cmd.motor_cmd[i].kp = 4.0
            low_cmd.motor_cmd[i].kd = 1.0
            low_cmd.motor_cmd[i].weight = 1.0
        elif i in [13, 19]:
            low_cmd.motor_cmd[i].q = 0.5
            low_cmd.motor_cmd[i].dq = 0.05
            low_cmd.motor_cmd[i].tau = 0.0
            low_cmd.motor_cmd[i].kp = 4.0
            low_cmd.motor_cmd[i].kd = 1.0
            low_cmd.motor_cmd[i].weight = 1.0
        elif i in [14, 20]:
            low_cmd.motor_cmd[i].q = -0.5
            low_cmd.motor_cmd[i].dq = 0.05
            low_cmd.motor_cmd[i].tau = 0.0
            low_cmd.motor_cmd[i].kp = 4.0
            low_cmd.motor_cmd[i].kd = 1.0
            low_cmd.motor_cmd[i].weight = 1.0

    channel_publisher.Write(low_cmd)
    print("Publish ")
    time.sleep(SLEEP_TIME)

    channel_publisher.Write(low_cmd)
    print("Publish LowCmd")
    time.sleep(SLEEP_TIME)
