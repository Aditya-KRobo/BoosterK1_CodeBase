from evdev import InputDevice, categorize, ecodes

# Replace with your actual device path from /dev/input/
gamepad = InputDevice('/dev/input/event6') 

for event in gamepad.read_loop():
    if event.type == ecodes.EV_KEY:
        print(categorize(event))
    elif event.type == ecodes.EV_ABS:
        # Joystick/Axes
        print(categorize(event))