#pip install evdev
from evdev import UInput, ecodes as e

# Define capabilities (buttons and axes)
cap = {
    e.EV_KEY: [e.BTN_A, e.BTN_B],
    e.EV_ABS: [
        (e.ABS_X, (0, 255, 128, 0)), # axis, (min, max, fuzz, flat)
        (e.ABS_Y, (0, 255, 128, 0))
    ]
}

# Create virtual device
with UInput(cap, name='virtual-gamepad') as ui:
    # Press A button
    ui.write(e.EV_KEY, e.BTN_A, 1)
    ui.syn()

    # Move joystick
    ui.write(e.EV_ABS, e.ABS_X, 255)
    ui.syn()
