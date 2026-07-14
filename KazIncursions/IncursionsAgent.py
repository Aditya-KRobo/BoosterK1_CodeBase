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

def parameter_parser():
    with open(json_path) as f:
        data = json.load(f)
    move_x = data["move_x"]
    move_y = data["move_y"]
    turn = data["turn"]
    gait_type = data["gait_type"]
    head_up = data["head_up"]
    head_down = data["head_down"]
    head_left = data["head_left"]
    head_right = data["head_right"]
    return move_x, move_y, turn, gait_type, head_up, head_down, head_left, head_right

def main():

    ChannelFactory.Instance().Init(0,'127.0.0.1')

    client = B1LocoClient()
    client.Init()
    res = 0

    Agent_flag = 0
    Busy_flag = 0
    Body_head_switch = 0
    Head_direction = ""

    Action_index = -1
    Action_list = action_list_parser()

    Last_action = None

    x_spd, y_spd, turn_spd, gait, pitch_up, pitch_down, yaw_left, yaw_right = parameter_parser()
    pitch = 0.0
    yaw = 0.0

    # Robot setup: Walk Mode, Head looking straight ahead
    time.sleep(5)
    # res = client.ChangeMode(RobotMode.kCustom)
    res = client.ChangeMode(RobotMode.kWalking)
    # res = client.RotateHead(0.0,0.0)
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

    gamepad = InputDevice('/dev/input/event7')

    try:
        print("vision system running. Press Ctrl+C to stop.")
        
        Head_direction = "Center"

        while True:

            for event in gamepad.read_loop():

                if Agent_flag == 1:
                    if Head_direction == "Up" and Body_head_switch == 1:
                        pitch -= 0.05
                        pitch =  max(pitch_up, pitch)
                        client.RotateHead(pitch,yaw)
                        print("Looking up...")

                    elif Head_direction == "Down" and Body_head_switch == 1:
                        pitch += 0.05
                        pitch =  max(pitch_up, min(pitch_down, pitch))
                        client.RotateHead(pitch,yaw)
                        print("Looking down...")

                    elif Head_direction == "Left" and Body_head_switch == 1:
                        yaw += 0.05
                        yaw =  min(yaw,yaw_left)
                        client.RotateHead(pitch,yaw)
                        print("Looking left...")

                    elif Head_direction == "Right" and Body_head_switch == 1:
                        yaw -= 0.05
                        yaw =  max(yaw_right,yaw)
                        client.RotateHead(pitch,yaw)
                        print("Looking right...")

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

                if New_Button_values[int(But_B)] == 1 and New_Button_values[int(But_A)] == 0 and Agent_flag == 1:
                    if Body_head_switch == 0:
                        print("Switching to Head Control")
                        Body_head_switch = 1
                    elif Body_head_switch == 1:
                        print("Switching to Body Control")
                        Body_head_switch = 0
                
                #Prometheus body movement commands
                if (New_Button_values[D_Y] == 1 and New_Button_values[D_X] == 1) and Agent_flag == 1 and Body_head_switch == 0:
                    # print("Standing still")
                    client.Move(0.0,0.0,0.0)

                elif New_Button_values[D_Y] == 1 and New_Button_values[D_X] == 0 and Agent_flag == 1 and Body_head_switch == 0:
                    # print("Moving forward")
                    client.Move(x_spd,0.0,0.0)

                elif New_Button_values[D_Y] == 1 and New_Button_values[D_X] == 2 and Agent_flag == 1 and Body_head_switch == 0:
                    # print("Moving backward")
                    client.Move(-x_spd,0.0,0.0)

                elif New_Button_values[D_Y] == 0 and New_Button_values[D_X] == 1 and Agent_flag == 1 and Body_head_switch == 0:
                    # print("Turning left")
                    client.Move(0.0,0.0,turn_spd)

                elif New_Button_values[D_Y] == 2 and New_Button_values[D_X] == 1 and Agent_flag == 1 and Body_head_switch == 0:
                    # print("Turning right")
                    client.Move(0.0,0.0,-turn_spd)
                
                #Prometheus head movement commands
                elif New_Button_values[D_Y] == 1 and New_Button_values[D_X] == 1 and Agent_flag == 1 and Body_head_switch == 1:
                    Head_direction = "Center"
                    print("Looking straight ahead")

                elif New_Button_values[D_Y] == 1 and New_Button_values[D_X] == 0 and Agent_flag == 1 and Body_head_switch == 1:
                    print("Looking up")
                    Head_direction = "Up"
                    pitch -= 0.05
                    pitch =  max(pitch_up, pitch)
                    client.RotateHead(pitch,yaw)

                elif New_Button_values[D_Y] == 1 and New_Button_values[D_X] == 2 and Agent_flag == 1 and Body_head_switch == 1:
                    print("Looking down")
                    Head_direction = "Down"
                    pitch += 0.05
                    pitch =  max(pitch_up, min(pitch_down, pitch))
                    client.RotateHead(pitch,yaw)

                elif New_Button_values[D_Y] == 0 and New_Button_values[D_X] == 1 and Agent_flag == 1 and Body_head_switch == 1:
                    print("Looking left")
                    Head_direction = "Left"
                    yaw += 0.05
                    yaw =  min(yaw,yaw_left)
                    client.RotateHead(pitch,yaw)

                elif New_Button_values[D_Y] == 2 and New_Button_values[D_X] == 1 and Agent_flag == 1 and Body_head_switch == 1:
                    print("Looking right")
                    Head_direction = "Right"
                    yaw -= 0.05
                    yaw =  max(yaw_right,yaw)
                    client.RotateHead(pitch,yaw)


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
