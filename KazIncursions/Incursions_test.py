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
import pygame
from inputs import get_gamepad

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

Audio_files = ["/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/01.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/02.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/03.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/04.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/05.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/06.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/07.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/08.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/09.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/10.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/11.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/12.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/13.mp3",
            "/home/booster/Workspace/K1_Custom_Behaviors/K1_test_programs/res/14.mp3"]

def main():

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)

    ChannelFactory.Instance().Init(0, sys.argv[1])

    client = B1LocoClient()
    client.Init()
    res = 0

    # res = client.ChangeMode(RobotMode.kCustom)

    audio_lock = False
    audio_flag = 0
    pygame.init()

    while True:

        events = get_gamepad()
        
        for event in events:
            # print(f'{event.ev_type} | {event.code} | {event.state}')
            Button_values[event.code] = event.state

            # if Button_values[But_Plu] == 0 and audio_lock:
            #     audio_lock = False
            if Button_values[But_Plu] == 1 and not audio_lock:
                pygame.mixer.music.load(Audio_files[audio_flag])
            
            # if Button_values[But_Min] == 0 and audio_lock:
            #     audio_lock = False
            if Button_values[But_Min] == 1 and not audio_lock:
                # print("Button Min is pressed, starting music playback...")
                audio_lock = True
                Button_values[But_Min] = 0
                try:
                    if audio_flag < 14:
                        pygame.mixer.music.load(Audio_files[audio_flag])
                        audio_flag += 1
                    elif audio_flag == 14:
                        audio_flag = 0

                except pygame.error as e:
                    print(f"Could not load music file: {e}")
                    # Handle the error, maybe exit the program or use a placeholder
                    exit()

                pygame.mixer.music.set_volume(1.0)

                try:
                    pygame.mixer.music.play()
                    print("Music started playing...")
                    while pygame.mixer.music.get_busy():
                        time.sleep(1) 
                        if res != 0:
                            print(f"Request failed: error = {res}")
                    audio_lock = False
                except KeyboardInterrupt:
                    print("Music playback interrupted by user.")
                # finally:
                    # audio_lock = False
                    # pygame.quit()


if __name__ == "__main__":
    main()
