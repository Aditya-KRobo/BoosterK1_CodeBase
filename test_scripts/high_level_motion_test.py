from booster_robotics_sdk_python import (
    B1LocoClient,
    ChannelFactory,
    RobotMode,
    DanceId,
    WholeBodyDanceId,
    HandAction,
    kHandOpen,
    kHandClose,
    WaveHand,
    Handshake,
    Position,
    Orientation,
    Posture,
    GetModeResponse,
    Quaternion,
    Frame,
    Transform,
)
import sys, time, random


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)

    net_if = sys.argv[1]
    robot_name = sys.argv[2] if len(sys.argv) >= 3 else None

    ChannelFactory.Instance().Init(0, net_if)

    client = B1LocoClient()
    if robot_name:
        client.InitWithName(robot_name)
    else:
        client.Init()

    x, y, z, yaw, pitch = 0.0, 0.0, 0.0, 0.0, 0.0
    res = 0
    hand_action_count = 0

    while True:
        try:
            raw = input(
            "Here is the command list:\
                          \n1. Enter damp mode -> md\
                          \n2. Enter prep mode -> mp\
                          \n3. Enter walk mode -> mw\
                          \n4. Enter cust mode -> mc\
                          \n5. Start Handshake -> hsko\
                          \n6. Stop Handshake -> hskc\
                          \n7. Dance NewYear -> d0\
                          \n8. WB Dance Moonwalk -> wbd4\
                          \n....."
        ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExit.")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0]
        args = parts[1:]

        need_print = False


        if cmd == "mp":
            res = client.ChangeMode(RobotMode.kPrepare)
        elif cmd == "md":
            res = client.ChangeMode(RobotMode.kDamping)
        elif cmd == "mw":
            res = client.ChangeMode(RobotMode.kWalking)
        elif cmd == "mc":
            res = client.ChangeMode(RobotMode.kCustom)
        elif cmd == "hsko":
            res = client.ChangeMode(RobotMode.kWalking)
            res = client.Handshake(kHandOpen)
        elif cmd == "d0":
            res = client.ChangeMode(RobotMode.kWalking)
            res = client.Dance(DanceId.kNewYear)
        elif cmd == "wbd4":
            res = client.ChangeMode(RobotMode.kWalking)
            res = client.WholeBodyDance(WholeBodyDanceId.kMoonWalk)

        if res != 0:
            print(f"Request failed: error = {res}")


if __name__ == "__main__":
    main()
