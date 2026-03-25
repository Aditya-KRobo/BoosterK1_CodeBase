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
from inputs import get_gamepad

import pygame # Load the popular external library

But_A = "BTN_EAST"
But_B = "BTN_C"
But_X = "BTN_SOUTH"
But_Y = "BTN_NORTH"
But_LB = "BTN_WEST"
But_RB = "BTN_Z"
But_LT = "ABS_RX"
But_RT = "ABS_RY"
But_Min = "BTN_TL2"
But_Plu = "BTN_TR2"
D_X = "ABS_HAT0X"
D_Y = "ABS_HAT0Y"
But_START = "BTN_START"
But_SELECT = "BTN_SELECT"
But_O = "BTN_THUMBL"
But_HOME = "BTN_MODE"

Button_values = {"BTN_EAST": 0, "BTN_C": 0, "BTN_SOUTH": 0, "BTN_NORTH": 0, "BTN_WEST": 0, "BTN_Z": 0, "ABS_RX": 0, "ABS_RY": 0, "BTN_TL2": 0, "BTN_TR2": 0, "ABS_HAT0X": 0, "ABS_HAT0Y": 0, "BTN_START": 0, "BTN_SELECT": 0, "BTN_THUMBL": 0, "BTN_MODE": 0}


import threading
import time


def danceRoutine(client):
    print("Dance thread starting...")
    time.sleep(1) # Simulate an I/O operation

    #MJ2, tf, 
    dance_sequence = [
        WholeBodyDanceId.kMichaelDance2,
        DanceId.kDabbingGesture,
        WholeBodyDanceId.kMichaelDance3,
        DanceId.kLuckyCatGesture,
        WholeBodyDanceId.kMichaelDance1,
        DanceId.kTowardsFuture,
        WholeBodyDanceId.kMoonWalk, 
        DanceId.kRespectGesture
        ]
    # dance_sequence = [DanceId.kDabbingGesture, DanceId.kLuckyCatGesture]
    wbd = [0,2,4,6]
    d = [1,3,5,7]
    # d = [0,1]
    dance_lock = False
    dance_num = 0
    res = 0

    while True:

        events = get_gamepad()
        
        for event in events:
            print(f'{event.ev_type} | {event.code} | {event.state}')
            Button_values[event.code] = event.state

            if Button_values[But_Plu] == 0 and dance_lock:
                dance_lock = False
                # res = client.ChangeMode(RobotMode.kWalking)
            elif Button_values[But_Plu] == 1 and not dance_lock:
                dance_lock = True
                # if dance_num-1 in wbd:
                #     res = client.ChangeMode(RobotMode.kWalking)
                # res = client.ChangeMode(RobotMode.kWalking)
                if dance_num in wbd:
                    res = client.WholeBodyDance(dance_sequence[dance_num])#dance_sequence[dance_num])
                elif dance_num in d:
                    res = client.Dance(dance_sequence[dance_num])#dance_sequence[dance_num])
                dance_num += 1
            
            if dance_num >= len(dance_sequence):
                dance_num = 0
                print("Dance completed.")
                exit()

        # break

'''
def musicPlayback():
    print(f"Music thread starting...")
    time.sleep(1) # Simulate an I/O operation
    pygame.init()
    pygame.mixer.music.load('/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/Michael Jackson - Billie Jean(2).mp3')
    pygame.mixer.music.set_volume(0.2)
    try:
        pygame.mixer.music.play()
        print("Music started playing...")
        while pygame.mixer.music.get_busy():
            time.sleep(1) 
    except KeyboardInterrupt:
        print("Music playback interrupted by user.")
        pygame.mixer.music.stop()
'''

def main():

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)

    ChannelFactory.Instance().Init(0, sys.argv[1])

    client = B1LocoClient()
    client.Init()

    # Create and start dance thread
    dance_thread = threading.Thread(target=danceRoutine, args=(client,))
    dance_thread.start()

    time.sleep(3) # Ensure the dance thread has started before playing music
    
    # Audio playback of music
    pygame.init()
    pygame.mixer.music.load('/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/Michael Jackson - Billie Jean(2).mp3')
    pygame.mixer.music.set_volume(0.75)
    try:
        pygame.mixer.music.play()
        print("Music started playing...")
        while pygame.mixer.music.get_busy():
            time.sleep(1) 
    except KeyboardInterrupt:
        print("Music playback interrupted by user.")
        pygame.mixer.music.stop()

    # Wait for threads to finish
    dance_thread.join()

    print("Main thread: all done.")


if __name__ == "__main__":
    main()
