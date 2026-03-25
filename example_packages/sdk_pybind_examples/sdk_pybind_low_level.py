#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
example_low_level_io_all.py

Demonstrates:
- Initializing DDS via ChannelFactory
- Subscribing (optionally) to:
    - B1LowStateSubscriber (joint + IMU state)
    - B1OdometerStateSubscriber (odometry)
    - B1LowHandDataSubscriber (hand joint state)       <-- Corrected name
    - B1LowHandTouchDataSubscriber (tactile arrays)    <-- Corrected name
    - B1BatteryStateSubscriber (battery status)        <-- Added
- Publishing LowCmd periodically via B1LowCmdPublisher (optional):
    - Behavior: move joints 2–9 from
      [0.2, -1.45, 0.0, -0.5, 0.2, 1.45, 0.0, 0.5]
      to 0 with smooth interpolation over 3 seconds

Command-line options:
    --subs  Comma-separated: low_state,odom,hand_data,hand_touch,battery,all,none
    --pubs  Comma-separated: lowcmd,all,none

Examples:
    Enable all (default):
        python example_low_level_io_all.py

    Enable only low_state and battery; disable LowCmd publisher:
        python example_low_level_io_all.py --subs low_state,battery --pubs none
"""

import time
import math
import signal
import argparse
import sys

# 尝试导入 SDK，处理可能未安装的情况
try:
    import booster_robotics_sdk_python as br
except ImportError:
    print("Error: 'booster_robotics_sdk_python' module not found.")
    print("Please ensure the SDK is installed or PYTHONPATH is set correctly.")
    sys.exit(1)


# ========== DDS initialization ==========

def init_dds(domain_id: int = 0, iface: str = ""):
    """
    Initialize DDS communication. Must be called once before using channels.
    """
    factory = br.ChannelFactory.Instance()
    factory.Init(domain_id, iface)


# ========== LowCmd construction and publishing ==========

def create_base_lowcmd() -> br.LowCmd:
    """
    Build a base LowCmd:
    - PARALLEL mode
    - All joints: q/dq/tau = 0
    - kp/kd set to conservative values
    """
    cmd = br.LowCmd()
    cmd.cmd_type = br.LowCmdType.PARALLEL

    # Prefer the joint count exposed by the SDK; fall back to 22 if absent
    joint_cnt = int(getattr(br, "kJointCnt", 22))

    motors = []
    for _ in range(joint_cnt):
        m = br.MotorCmd()
        m.mode = 0          # Actual mode depends on the firmware; example only
        m.q = 0.0
        m.dq = 0.0
        m.tau = 0.0
        m.kp = 20.0
        m.kd = 1.0
        m.weight = 1.0
        motors.append(m)

    cmd.motor_cmd = motors
    return cmd


# ========== Joints 2–9: smooth interpolation to 0 within 3 seconds ==========

START_ANGLES = [0.2, -1.45, 0.0, -0.5,
                0.2,  1.45, 0.0,  0.5]   # For joints 2–9
END_ANGLES = [0.0] * 8                  # Final target is 0 for all


def generate_arm_down_trajectory(duration_sec: float = 3.0,
                                 dt: float = 0.02):
    """
    Generate a smooth trajectory for joints 2–9 from START_ANGLES to END_ANGLES.
    """
    if duration_sec <= 0.0:
        duration_sec = 3.0
    if dt <= 0.0:
        dt = 0.02

    num_frames = int(duration_sec / dt) + 1
    if num_frames < 2:
        num_frames = 2

    traj = []
    for i in range(num_frames):
        s = i / (num_frames - 1)
        smooth = 0.5 * (1.0 - math.cos(math.pi * s))  # 0 → 1
        frame = []
        for start, end in zip(START_ANGLES, END_ANGLES):
            angle = start * (1.0 - smooth) + end * smooth
            frame.append(angle)
        traj.append(frame)

    return traj


def apply_arm_trajectory(cmd: br.LowCmd, frame_idx: int, traj):
    """
    Write the specified trajectory frame into LowCmd.
    """
    if not traj:
        return frame_idx

    num_frames = len(traj)
    if num_frames == 0:
        return frame_idx

    # Clamp to the last frame so that joints stay at the final posture
    if frame_idx >= num_frames:
        frame_idx = num_frames - 1
    if frame_idx < 0:
        frame_idx = 0

    frame = traj[frame_idx]  # length = 8
    motors = cmd.motor_cmd

    # Unified control parameters
    mode = 1    # Example: assume 1 = position mode
    kp = 40.0
    kd = 3.0

    # Global joint indices 2–9
    for local_idx in range(8):
        j = 2 + local_idx
        if j >= len(motors):
            break
        m = motors[j]
        m.mode = mode
        m.kp = kp
        m.kd = kd
        m.q = float(frame[local_idx])

    cmd.motor_cmd = motors
    return frame_idx


# ========== Callbacks ==========

def on_low_state(msg: br.LowState):
    """Low-level joint + IMU state callback."""
    imu = msg.imu_state
    rpy = imu.rpy
    motors = msg.motor_state_parallel

    # Print first few joint positions
    positions = [m.q for m in motors[:4]]
    print(f"[LowState] rpy(deg)={[round(v * 180.0 / math.pi, 1) for v in rpy]}, "
          f"q[:4]={[round(v, 3) for v in positions]}")


def on_odom(msg: br.Odometer):
    """Odometry callback."""
    print(f"[Odom] x={msg.x:.3f}, y={msg.y:.3f}, theta={msg.theta:.3f}")


def on_hand_data(msg: br.HandReplyData):
    """Hand joint state callback."""
    hand_index = msg.hand_index
    params = msg.hand_data
    # Print angle/force for the first two fingers
    brief = [(p.seq, p.angle, p.force) for p in params[:2]]
    print(f"[HandData] idx={hand_index}, type={msg.hand_type}, params[:2]={brief}")


def on_hand_touch(msg: br.HandTouchData):
    """Tactile array callback."""
    t = msg.touch_data
    # Use 'len' just to show we received data
    lens = {
        "1": len(t.finger_one), "2": len(t.finger_two),
        "3": len(t.finger_three), "4": len(t.finger_four),
        "5": len(t.finger_five), "P": len(t.finger_palm),
    }
    print(f"[HandTouch] idx={msg.hand_index}, lens={lens}")


def on_battery_state(msg: br.BatteryState):
    """Battery state callback."""
    # 基于之前修复的binding，这些字段现在可以正常访问了
    print(f"[Battery] V={msg.voltage:.2f}V, I={msg.current:.2f}A, "
          f"SOC={msg.soc:.1f}%, AvgV={msg.average_voltage:.2f}V")


# ========== Argument parsing ==========

def parse_args():
    parser = argparse.ArgumentParser(
        description="B1 low-level IO all-in-one example"
    )
    parser.add_argument(
        "--domain-id", type=int, default=0,
        help="DDS domain id (default: 0)"
    )
    parser.add_argument(
        "--iface", type=str, default="",
        help="DDS network interface"
    )
    parser.add_argument(
        "--subs", type=str, default="all",
        help="low_state,odom,hand_data,hand_touch,battery,all,none"
    )
    parser.add_argument(
        "--pubs", type=str, default="lowcmd",
        help="lowcmd,all,none"
    )
    return parser.parse_args()


def parse_switches(raw: str, valid: set, default_all: bool) -> set:
    s = raw.strip().lower()
    if s == "all":
        return set(valid)
    if s == "none" or not s:
        return set()

    result = set()
    for item in s.split(","):
        item = item.strip()
        if not item: continue
        if item in valid:
            result.add(item)
        else:
            print(f"[Warn] unknown switch '{item}', ignored.")

    if not result and default_all:
        return set(valid)
    return result


# ========== Main loop ==========

def main():
    args = parse_args()

    # Define valid keys
    valid_subs = {"low_state", "odom", "hand_data", "hand_touch", "battery"}
    valid_pubs = {"lowcmd"}

    enabled_subs = parse_switches(args.subs, valid_subs, default_all=True)
    enabled_pubs = parse_switches(args.pubs, valid_pubs, default_all=False)

    print(f"Subs: {sorted(enabled_subs)}")
    print(f"Pubs: {sorted(enabled_pubs)}")

    # 2. Init DDS
    init_dds(domain_id=args.domain_id, iface=args.iface)

    # 3. Init objects
    subscribers = []
    lowcmd_pub = None

    if "low_state" in enabled_subs:
        s = br.B1LowStateSubscriber(on_low_state)
        s.InitChannel()
        subscribers.append(s)

    if "odom" in enabled_subs:
        s = br.B1OdometerStateSubscriber(on_odom)
        s.InitChannel()
        subscribers.append(s)

    if "hand_data" in enabled_subs:
        # Corrected class name: Subscriber instead of Scriber
        s = br.B1LowHandDataSubscriber(on_hand_data)
        s.InitChannel()
        subscribers.append(s)

    if "hand_touch" in enabled_subs:
        # Corrected class name: Subscriber instead of Scriber
        s = br.B1LowHandTouchDataSubscriber(on_hand_touch)
        s.InitChannel()
        subscribers.append(s)

    if "battery" in enabled_subs:
        # Newly added subscriber
        s = br.B1BatteryStateSubscriber(on_battery_state)
        s.InitChannel()
        subscribers.append(s)

    if "lowcmd" in enabled_pubs:
        lowcmd_pub = br.B1LowCmdPublisher()
        lowcmd_pub.InitChannel()

    # 4. Loop
    running = True
    def handle_sigint(sig, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, handle_sigint)

    traj = None
    frame_idx = 0
    dt = 0.02

    if lowcmd_pub:
        cmd = create_base_lowcmd()
        # Init start pose
        for local_idx, q0 in enumerate(START_ANGLES):
            if 2 + local_idx < len(cmd.motor_cmd):
                cmd.motor_cmd[2 + local_idx].q = q0
        
        traj = generate_arm_down_trajectory(3.0, dt)
        print("\n[Running] Pub=True. Press Ctrl+C to exit.\n")
    else:
        print("\n[Running] Pub=False. Press Ctrl+C to exit.\n")

    try:
        while running:
            if lowcmd_pub and traj:
                apply_arm_trajectory(cmd, frame_idx, traj)
                if frame_idx < len(traj) - 1:
                    frame_idx += 1
                lowcmd_pub.Write(cmd)
            
            time.sleep(dt)

    finally:
        print("\nClosing channels...")
        for s in subscribers:
            s.CloseChannel()
        if lowcmd_pub:
            lowcmd_pub.CloseChannel()
        print("Done.")

if __name__ == "__main__":
    main()