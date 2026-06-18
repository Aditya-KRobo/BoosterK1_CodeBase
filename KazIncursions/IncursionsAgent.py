But_A = 304
But_B = 305
But_X = "BTN_SOUTH"
But_Y = "BTN_NORTH"
But_LB = "BTN_WEST"
But_RB = "BTN_Z"
But_LT = 310
But_RT = 311
But_Min = "BTN_TL2"
But_Plu = "BTN_TR2"
D_X = 1
D_Y = 0
But_START = "BTN_START"
But_SELECT = "BTN_SELECT"
But_O = "BTN_THUMBL"
But_HOME = "BTN_MODE"

Code_map = {0:"ABS_HAT0X", 1:"ABS_HAT0Y", 310:"BTN_LT", 311:"BTN_RT", 308:"BTN_Y", 307:"BTN_X", 304:"BTN_A", 305:"BTN_B", 312:"BTN_LB", 313:"BTN_RB"}
New_Button_values = {0: 0, 1: 0, 310: 0, 311: 0, 308: 0, 307: 0, 304: 0, 305: 0, 312: 0, 313: 0}
# Button_values = {"BTN_EAST": 0, "BTN_C": 0, "BTN_SOUTH": 0, "BTN_NORTH": 0, "BTN_WEST": 0, "BTN_Z": 0, "BTN_TL": 0, "BTN_TR": 0, "BTN_TL2": 0, "BTN_TR2": 0, "ABS_HAT0X": 0, "ABS_HAT0Y": 0, "BTN_START": 0, "BTN_SELECT": 0, "BTN_THUMBL": 0, "BTN_MODE": 0}

json_path = '/home/booster/Workspace/BoosterK1_CodeBase/KazIncursions/action_sequence.json'


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
import os, sys, time, random

# folder_path = os.path.abspath('~/Workspace/BoosterK1_CodeBase/KazAgent')
# sys.path.insert(0, folder_path)
import Dialogue_behavior as DB
import Music_Dance_behavior as MDB
import Vision_behavior as VB


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

    Action_index = -1
    Action_list = action_list_parser()

    Last_action = None

    time.sleep(5)
    # res = client.ChangeMode(RobotMode.kCustom)
    res = client.ChangeMode(RobotMode.kWalking)
    if res != 0:
        print(f"Failed to get up with error code : {res}!")
        # return
    # res = client.EnterWBCGait()

    rclpy.init(args=None)
    vision_subscriber = VB.VisionSubscriber()
    executor = SingleThreadedExecutor()
    executor.add_node(vision_subscriber)

    spin_thread = Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    gamepad = InputDevice('/dev/input/event11')

    try:
        print("vision system running. Press Ctrl+C to stop.")
        while True:
            
            for event in gamepad.read_loop():
                
                Old_Button_values = New_Button_values.copy()
                
                if event.type == ecodes.EV_KEY:
                    # print((event.code,event.value))
                    # print(Code_map[int(event.code)])
                    if event.code == 304 or event.code == 305 or event.code == 310 or event.code == 311:
                        New_Button_values[int(event.code)] = int(event.value)
                    # print(New_Button_values[int(event.code)])

                elif event.type == ecodes.EV_ABS:
                    New_Button_values[int(event.code)] = int(event.value)
                    # print((event.code,event.value))
                    # print(New_Button_values[D_X], New_Button_values[D_Y])
                # print ("------------------------------")

                if New_Button_values == Old_Button_values:
                    # print("Button values unchanged!")
                    continue

            # events = get_gamepad()
            # for event in events:
            #     # pass
            #     print(f'{event.ev_type} | {event.code} | {event.state}')
            #     Button_values[event.code] = event.state

                # Logic flow:
                # 1. Priortize Joystick input for body movement; Reset movement if joystick released to middle position
                # 2. Then if a relevant button is pressed, do the actions following sqeuence from json file for actions
            
                # Enable IncursionAgent
                if New_Button_values[int(But_RT)] == 1 and New_Button_values[int(But_LT)] == 0 and Agent_flag == 0:
                    # print("IncursionAgent Enabled!")
                    Busy_flag = 0
                    Agent_flag = 1
                    # Switch to Walk mode
                    # res = client.ChangeMode(RobotMode.kWalking)

                #Disable IncursionAgent
                elif New_Button_values[int(But_RT)] == 0 and New_Button_values[int(But_LT)] == 1 and Agent_flag == 1:
                    # print("IncursionAgent Disabled!")
                    Busy_flag = 0
                    Agent_flag = 0
                    Action_index = -1
                    # Switch to Walk mode
                    # res = client.ChangeMode(RobotMode.kWalking)

                
                #Prometheus movement commands
                if (New_Button_values[D_Y] == 1 and New_Button_values[D_X] == 1) and Agent_flag == 1:
                    # print("Standing still")
                    client.Move(0.0,0.0,0.0)

                elif New_Button_values[D_Y] == 1 and New_Button_values[D_X] == 0 and Agent_flag == 1:
                    # print("Moving forward")
                    client.Move(0.5,0.0,0.0)

                elif New_Button_values[D_Y] == 1 and New_Button_values[D_X] == 2 and Agent_flag == 1:
                    # print("Moving backward")
                    client.Move(-0.5,0.0,0.0)

                elif New_Button_values[D_Y] == 0 and New_Button_values[D_X] == 1 and Agent_flag == 1:
                    # print("Turning left")
                    client.Move(0.0,0.0,0.5)

                elif New_Button_values[D_Y] == 2 and New_Button_values[D_X] == 1 and Agent_flag == 1:
                    # print("Turning right")
                    client.Move(0.0,0.0,-0.5)
                
                
                if New_Button_values[int(But_A)] == 1 and New_Button_values[int(But_B)] == 0 and Agent_flag == 1:
                    Action_index += 1
                    if Action_index >= len(Action_list):
                        # print("No more actions in the list!")
                        Action_index = len(Action_list) - 1
                    else:
                        # Execute the action at Action_index from Action_list
                        Action_item = Action_list[Action_index]
                        if (Last_action == "DGDC"):
                            MDB.Single_Dance_behavior(client, 1000)
                            time.sleep(1)
                            res = client.ChangeMode(RobotMode.kWalking)
                            # MDB.Single_Dance_behavior(client, Action_item[2])

                        # print(f"Executing action: {Action_item}")
                        if Action_item[0] == "DG":
                            # print("Requested Dialogue")
                            # Execute dialogue behavior
                            DB.Single_Dialogue_behavior(Action_item[1])


                        elif Action_item[0] == "DGDC":
                            # print("Requested Dialogue + Dance")
                            # Execute dialogue behavior and dance behavior
                            DB.Single_Dialogue_behavior(Action_item[1])
                            MDB.Single_Dance_behavior(client, Action_item[2])

                        Last_action = Action_item[0]
    
                '''
                elif New_Button_values[int(But_B)] == 1 and New_Button_values[int(But_A)] == 0 and Agent_flag == 1:
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
                '''

    except KeyboardInterrupt:
        print("Stopping vision_demo.")
    finally:
        executor.shutdown()
        vision_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
