from evdev import InputDevice, categorize, ecodes

# Replace with your actual device path from /dev/input/
gamepad = InputDevice('/dev/input/event11') 

for event in gamepad.read_loop():
    if event.type == ecodes.EV_KEY:
        print(categorize(event)," ",(event.code,event.value))
    elif event.type == ecodes.EV_ABS:
        # Joystick/Axes
        print(categorize(event)," ",(event.code,event.value))


# from inputs import get_gamepad

# events = get_gamepad()
# for event in events:
#     # pass
#     print(f'{event.ev_type} | {event.code} | {event.state}')
