But_A = "BTN_EAST"
But_B = "BTN_C"
But_X = "BTN_SOUTH"
But_Y = "BTN_NORTH"
But_LB = "BTN_WEST"
But_RB = "BTN_Z"
But_LT = "BTN_TL"
But_RT = "BTN_TR"
But_Min = "BTN_TL2"
But_Plu = "BTN_TR2"
D_X = "ABS_HAT0X"
D_Y = "ABS_HAT0Y"
But_START = "BTN_START"
But_SELECT = "BTN_SELECT"
But_O = "BTN_THUMBL"
But_HOME = "BTN_MODE"

Button_values = {"BTN_EAST": 0, "BTN_C": 0, "BTN_SOUTH": 0, "BTN_NORTH": 0, "BTN_WEST": 0, "BTN_Z": 0, "BTN_TL": 0, "BTN_TR": 0, "BTN_TL2": 0, "BTN_TR2": 0, "ABS_HAT0X": 0, "ABS_HAT0Y": 0, "BTN_START": 0, "BTN_SELECT": 0, "BTN_THUMBL": 0, "BTN_MODE": 0}

global Agent_flag
global Busy_flag
global Stand_flag
global Sit_flag


# from evdev import InputDevice, categorize, ecodes

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

import Dialogue_behavior as DB
import Music_Dance_behavior as MDB


def main():

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)

    ChannelFactory.Instance().Init(0, sys.argv[1])

    client = B1LocoClient()
    client.Init()
    res = 0

    Agent_flag = 0
    Busy_flag = 0
    Sit_flag = 0
    Stand_flag = 0

    time.sleep(5)
    # res = client.ChangeMode(RobotMode.kCustom)
    # res = client.GetUpWithMode(RobotMode.kWalking)
    # res = client.EnterWBCGait()

    while True:
        events = get_gamepad()
        for event in events:
            # pass
            # print(f'{event.ev_type} | {event.code} | {event.state}')
            Button_values[event.code] = event.state

        # Enable KazAgent v1
        if Button_values[But_LT] == 1 and Button_values[But_LB] == 1 and Agent_flag == 0:
            print("KazAgent Enabled!")
            Busy_flag = 0
            Agent_flag = 1
            Stand_flag = 1
            # Switch to Walk mode
            # res = client.ChangeMode(RobotMode.kWalking)

        #Disable KazAgent v1
        elif Button_values[But_RT] == 1 and Button_values[But_RB] == 1 and Agent_flag == 1:
            print("KazAgent Disabled!")
            Busy_flag = 0
            Agent_flag = 0
            Stand_flag = 1
            # Switch to Walk mode
            # res = client.ChangeMode(RobotMode.kDamping)

        # Trigger Sitdown behavior, if robot is standing and idle
        if Button_values[But_LT] == 1 and Button_values[But_Min] == 1 and Agent_flag == 1 and Stand_flag == 1 and Busy_flag == 0:
            print("Requested Sit-down")
            #Lock the robot process
            Busy_flag = 1
            Sit_flag = 1
            # Execute sit-down behavior
            Busy_flag = 0
            Stand_flag = 0

        #Trigger Stand-up behavior, if robot is sitting and idle
        elif Button_values[But_LT] == 1 and Button_values[But_Plu] == 1 and Agent_flag == 1 and Sit_flag == 1 and Busy_flag == 0:
            print("Requested Stand-up")
            Busy_flag = 1
            Stand_flag = 1
            # Execute stand-up behavior
            Busy_flag = 0
            Sit_flag = 0

        #Trigger Music-Dance behavior, if robot is idle
        elif Button_values[But_LB] == 1 and Button_values[But_Min] == 1 and Agent_flag == 1 and Busy_flag == 0:
            print("Requested Music-Dance")
            Busy_flag = 1
            # Execute music-dance behavior
            # MDB.Music_Dance_behavior(client)

        #Trigger Dialogue behavior, if robot is idle
        elif Button_values[But_LB] == 1 and Button_values[But_Plu] == 1 and Agent_flag == 1 and Busy_flag == 0:
            print("Requested Dialogue")
            Busy_flag = 1
            # Execute dialogue behavior
            # DB.Dialogue_behavior()

        elif Button_values[But_O] == 1 and Agent_flag == 1 and Busy_flag == 1:
            print("Requested Robot to be put to Idle mode")
            Busy_flag = 0



if __name__ == "__main__":
    main()
