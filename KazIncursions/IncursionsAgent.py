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

Code_map = {0:"ABS_HAT0X", 1:"ABS_HAT0Y", 310:"BTN_LT", 311:"BTN_RT", 308:"BTN_Y", 307:"BTN_X", 304:"BTN_A", 305:"BTN_B"}
Button_values = {"BTN_EAST": 0, "BTN_C": 0, "BTN_SOUTH": 0, "BTN_NORTH": 0, "BTN_WEST": 0, "BTN_Z": 0, "BTN_TL": 0, "BTN_TR": 0, "BTN_TL2": 0, "BTN_TR2": 0, "ABS_HAT0X": 0, "ABS_HAT0Y": 0, "BTN_START": 0, "BTN_SELECT": 0, "BTN_THUMBL": 0, "BTN_MODE": 0}

json_path = 'KazIncursions/action_sequence.json'


global Agent_flag
global Busy_flag
global Stand_flag
global Sit_flag

from evdev import InputDevice, categorize, ecodes

from threading import Thread
import json
import rclpy
from rclpy.executors import SingleThreadedExecutor

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

import KazAgent.Dialogue_behavior as DB
import KazAgent.Music_Dance_behavior as MDB
import KazAgent.Vision_behavior as VB




def action_list_parser() -> list:
    with open(json_path) as f:
        data = json.load(f)
    return data["action_list"]


def main():

    # if len(sys.argv) < 2:
    #     print(f"Usage: {sys.argv[0]} networkInterface")
    #     sys.exit(-1)

    # ChannelFactory.Instance().Init(0, sys.argv[1])

    ChannelFactory.Instance().Init(0,'127.0.0.1')

    client = B1LocoClient()
    client.Init()
    res = 0

    Agent_flag = 0
    Busy_flag = 0
    Sit_flag = 0
    Stand_flag = 0

    Action_index = -1
    Action_list = action_list_parser()

    time.sleep(5)
    # res = client.ChangeMode(RobotMode.kCustom)
    res = client.GetUpWithMode(RobotMode.kWalking)
    if res != 0:
        print(f"Failed to get up with error code : {res}!")
        return
    # res = client.EnterWBCGait()

    rclpy.init(args=None)
    vision_subscriber = VB.VisionSubscriber()
    executor = SingleThreadedExecutor()
    executor.add_node(vision_subscriber)

    spin_thread = Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    gamepad = InputDevice('/dev/input/event20')

    try:
        print("vision system running. Press Ctrl+C to stop.")
        while True:
            
            for event in gamepad.read_loop():
                if event.type == ecodes.EV_KEY:
                    print(categorize(event))
                elif event.type == ecodes.EV_ABS:
                    print((event.code,event.value))
                
                Button_values[Code_map[event.code]] = event.state

            events = get_gamepad()
            for event in events:
                # pass
                print(f'{event.ev_type} | {event.code} | {event.state}')
                Button_values[event.code] = event.state

            # Logic flow:
            # 1. Priortize Joystick input for body movement; Reset movement if joystick released to middle position
            # 2. Then if a relevant button is pressed, do the actions following sqeuence from json file for actions

            # Enable IncursionAgent
            if Button_values[But_RT] == 1 and Button_values[But_LT] == 0 and Agent_flag == 0:
                print("IncursionAgent Enabled!")
                Busy_flag = 0
                Agent_flag = 1
                Stand_flag = 1
                # Switch to Walk mode
                res = client.ChangeMode(RobotMode.kWalking)

            #Disable IncursionAgent
            elif Button_values[But_RT] == 0 and Button_values[But_LT] == 1 and Agent_flag == 1:
                print("IncursionAgent Disabled!")
                Busy_flag = 0
                Agent_flag = 0
                Stand_flag = 1
                # Switch to Walk mode
                # res = client.ChangeMode(RobotMode.kWalking)

            #Prometheus movement commands
            if (Button_values[D_Y] == 1 or Button_values[D_X] == 1) and Agent_flag == 1:
                client.Move(0.0,0.0,0.0)

            elif Button_values[D_Y] == 0 and Agent_flag == 1:
                #Forward
                client.Move(0.1,0.0,0.0)

            elif Button_values[D_Y] == 2 and Agent_flag == 1:
                #Backward
                client.Move(0.1,0.0,0.0)

            elif Button_values[D_X] == 0 and Agent_flag == 1:
                #Left turn
                client.Move(0.0,0.0,-0.1)

            elif Button_values[D_X] == 2 and Agent_flag == 1:
                #Right turn
                client.Move(0.0,0.0,0.1)
            

            elif Button_values[But_A] == 1 and Button_values[But_B] == 0 and Agent_flag == 1:
                Action_index += 1
                if Action_index >= len(Action_list):
                    print("No more actions in the list!")
                    Action_index = len(Action_list) - 1
                else:
                    # Execute the action at Action_index from Action_list
                    Action_item = Action_list[Action_index]
                    if Action_item[0] == "DG":
                        print("Requested Dialogue")
                        Busy_flag = 1
                        # Execute dialogue behavior
                        DB.Single_Dialogue_behavior(Action_item[1])
                        Busy_flag = 0

            elif Button_values[But_B] == 1 and Button_values[But_A] == 0 and Agent_flag == 1:
                Action_index -= 1
                if Action_index >= len(Action_list):
                    print("No more actions in the list!")
                    Action_index = len(Action_list) - 1
                else:
                    # Execute the action at Action_index from Action_list
                    Action_item = Action_list[Action_index]
                    if Action_item[0] == "DG":
                        print("Requested Dialogue")
                        Busy_flag = 1
                        # Execute dialogue behavior
                        DB.Single_Dialogue_behavior(Action_item[1])
                        Busy_flag = 0


    except KeyboardInterrupt:
        print("Stopping vision_demo.")
    finally:
        executor.shutdown()
        vision_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
