# Setup guide for the Safety show

## Introduction

This document contains the info and steps regarding the current setup for the Safety show as of 24th June. Currently the ring-styled controller has some weird issue where when the robot and then the controller are powered-on, the controller does auto-connect to the robot's 2nd bluetooth adaptor, but the input files to read controller input don't show up. Some commands need to be run to properly setup the controller interface. Also there are risks of the controller suddenly disconnecting while robot operates. In that case the robot should stop on its own, but if it doesn't, then just press the WALK button to stop the robot's motion. To deal with this weird issue, after I return, I will likely try to buy a few more controllers.

## Setup

### Powering ON

1. Power on the robot after putting in a fully-charged battery
2. While the robot powers up, open your terminal/command prompt sooftware on your system. You are going to be ssh'ing into the robot and executing a few commands.
3. Once the robot makes a sound indicating its live, ssh to it using 

    `ssh booster@10.12.100.167`

4. Then power on the ring controller and u can notice that its led will flash quickly and then stop flashing, indicating it autoconnected.

### Fixing the bluetooth controller

1. To fix the controller, we need to disconnect and reconnect it. First execute the following command in terminal session ssh'ed over to the robot

    `bluetoothctl`

2. This will open the bluetooth control tool for terminal on the robot. Then press the up button a few times to execute the following commands in sequence 
    
    ```
    select AC:A7:F1:B0:35:F9

    disconnect FF:25:12:02:21:8C

    connect FF:25:12:02:21:8C

    exit
    ```

    The above will setup the controller and can be checked with

    `ls /dev/input/`

    This should show event11 in the output

### Running the code

1. Next navigate to the codebase folder with

    `cd Workspace/BoosterK1_CodeBase`

2. Run the code with 

    `python3 KazIncursions/IncursionsAgent.py`

3. Make sure before Activiation button(button with U-turn symbol), move the joystick around to warm it 
up and then use the remote and robot as normal. Just be on the lookout for possible disconnections.