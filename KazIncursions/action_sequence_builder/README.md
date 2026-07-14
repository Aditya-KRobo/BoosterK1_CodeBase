# Action Sequence Builder

A small Tkinter prototype for building `KazIncursions/action_sequence.json`.

Run it from the repository root:

```bash
python3 KazIncursions/action_sequence_builder/app.py
```

The GUI writes JSON in the same shape currently consumed by `IncursionsAgent.py`:

```json
{
  "move_x": 0.5,
  "move_y": 0.5,
  "turn": 0.5,
  "gait_type": "normal",
  "head_up": -0.2,
  "head_down": 0.75,
  "head_left": 0.5,
  "head_right": -0.5,
  "action_list": [
    ["DG", "/path/to/audio.mp3", 1000],
    ["DGDC", "/path/to/audio.mp3", 2]
  ]
}
```

The first prototype supports the action opcodes that `IncursionsAgent.py` already
executes:

- `DG`: play one dialogue/audio file.
- `DGDC`: play one dialogue/audio file and trigger one dance ID.

It also scans `Music_Dance_behavior.py`, `Dialogue_behavior.py`, and
`Vision_behavior.py` with Python `ast` and shows discovered functions as reference
items. Those discovered function items are not exported until the robot executor
gets matching opcodes for them.
