from evdev import InputDevice, categorize, ecodes

from inputs import get_gamepad

from booster_robotics_sdk_python import (
    DanceId,
    WholeBodyDanceId,
    B1LocoClient,
    ChannelFactory,
    RobotMode,
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

    ChannelFactory.Instance().Init(0, sys.argv[1])

    client = B1LocoClient()
    client.Init()
    res = 0

    # res = client.ChangeMode(RobotMode.kCustom)
    # res = client.GetUpWithMode(RobotMode.kWalking)
    # res = client.EnterWBCGait()

    # # Find the gamepad device file (e.g., /dev/input/eventX)
    # gamepad = InputDevice("/dev/input/js0")
    # print(gamepad)

    # for event in gamepad.read_loop():
    #     if event.type == ecodes.EV_KEY:
    #         print(categorize(event))  # Button presses
    #         # res = client.PlaySound("/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/Michael Jackson - Billie Jean(2).mp3")
    #         # res = client.Dance(DanceId.kNewYear)
    #     elif event.type == ecodes.EV_ABS:
    #         print(categorize(event))  # Stick movements
    #         # res = client.StopSound()
    #         # res = client.Dance(DanceId.kUltramanGuesture)

    while True:
        events = get_gamepad()
        for event in events:
            print(f'{event.ev_type} | {event.code} | {event.state}')
            
        print("--------------")

    if res != 0:
        print(f"Request failed: error = {res}")


if __name__ == "__main__":
    main()