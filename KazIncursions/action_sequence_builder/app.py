#!/usr/bin/env python3
"""Prototype GUI for building KazIncursions action sequence JSON files."""

from __future__ import annotations

import ast
import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any


APP_DIR = Path(__file__).resolve().parent
INCURSIONS_DIR = APP_DIR.parent
DEFAULT_JSON_PATH = INCURSIONS_DIR / "action_sequence.json"
BEHAVIOR_FILES = [
    INCURSIONS_DIR / "Dialogue_behavior.py",
    INCURSIONS_DIR / "Music_Dance_behavior.py",
    INCURSIONS_DIR / "Vision_behavior.py",
]

BASE_PARAMETERS: dict[str, Any] = {
    "move_x": 0.5,
    "move_y": 0.5,
    "turn": 0.5,
    "gait_type": "normal",
    "head_up": -0.2,
    "head_down": 0.75,
    "head_left": 0.5,
    "head_right": -0.5,
}


@dataclass
class ActionTemplate:
    label: str
    opcode: str
    description: str
    exportable: bool = True


@dataclass
class TimelineAction:
    opcode: str
    audio_file: str = ""
    value: int = 1000
    label: str = ""
    exportable: bool = True

    @classmethod
    def from_json_item(cls, item: list[Any]) -> "TimelineAction":
        opcode = str(item[0]) if item else "DG"
        audio_file = str(item[1]) if len(item) > 1 else ""
        value = coerce_int(item[2], default=1000) if len(item) > 2 else 1000
        return cls(opcode=opcode, audio_file=audio_file, value=value, label=opcode)

    @classmethod
    def from_template(cls, template: ActionTemplate) -> "TimelineAction":
        default_value = 2 if template.opcode == "DGDC" else 1000
        return cls(
            opcode=template.opcode,
            value=default_value,
            label=template.label,
            exportable=template.exportable,
        )

    def to_json_item(self) -> list[Any]:
        return [self.opcode, self.audio_file, self.value]

    def display_text(self, index: int) -> str:
        audio_name = Path(self.audio_file).name if self.audio_file else "no audio"
        if not self.exportable:
            return f"{index + 1:02d}. {self.label} (reference only)"
        if self.opcode == "DGDC":
            return f"{index + 1:02d}. DGDC | {audio_name} | dance {self.value}"
        return f"{index + 1:02d}. {self.opcode} | {audio_name}"


def coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    merged = dict(BASE_PARAMETERS)
    for key in BASE_PARAMETERS:
        if key in data:
            merged[key] = data[key]
    merged["action_list"] = data.get("action_list", [])
    return merged


def write_json(path: Path, parameters: dict[str, Any], actions: list[TimelineAction]) -> None:
    exportable_actions = [action.to_json_item() for action in actions if action.exportable]
    data = dict(parameters)
    data["action_list"] = exportable_actions
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.write("\n")


def discover_behavior_functions() -> list[ActionTemplate]:
    templates: list[ActionTemplate] = []
    for file_path in BEHAVIOR_FILES:
        if not file_path.exists():
            continue
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                templates.append(
                    ActionTemplate(
                        label=f"{file_path.stem}.{node.name}",
                        opcode=node.name,
                        description="Discovered behavior function; add executor support before export.",
                        exportable=False,
                    )
                )
    return sorted(templates, key=lambda item: item.label.lower())


class ActionSequenceBuilder(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("KazIncursions Action Sequence Builder")
        self.geometry("1180x720")
        self.minsize(980, 620)

        self.json_path = DEFAULT_JSON_PATH
        self.parameters: dict[str, Any] = dict(BASE_PARAMETERS)
        self.actions: list[TimelineAction] = []
        self.templates = self.build_templates()
        self.drag_template_index: int | None = None
        self.drag_action_index: int | None = None

        self.path_var = tk.StringVar(value=str(self.json_path))
        self.status_var = tk.StringVar(value="Ready")
        self.audio_var = tk.StringVar()
        self.value_var = tk.StringVar()
        self.opcode_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.parameter_vars = {
            key: tk.StringVar(value=str(value)) for key, value in self.parameters.items()
        }

        self.create_widgets()
        self.load_file(self.json_path)

    def build_templates(self) -> list[ActionTemplate]:
        built_in = [
            ActionTemplate("Dialogue", "DG", "Play one dialogue/audio file."),
            ActionTemplate("Dialogue + Dance", "DGDC", "Play audio and trigger a dance ID."),
        ]
        return built_in + discover_behavior_functions()

    def create_widgets(self) -> None:
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self, padding=(10, 8))
        toolbar.grid(row=0, column=0, columnspan=3, sticky="ew")
        toolbar.columnconfigure(1, weight=1)

        ttk.Button(toolbar, text="Open", command=self.open_json).grid(row=0, column=0, padx=(0, 8))
        ttk.Entry(toolbar, textvariable=self.path_var, state="readonly").grid(row=0, column=1, sticky="ew")
        ttk.Button(toolbar, text="Save", command=self.save_json).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(toolbar, text="Save As", command=self.save_json_as).grid(row=0, column=3, padx=(8, 0))

        self.create_palette()
        self.create_timeline()
        self.create_properties()

        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(10, 6))
        status.grid(row=2, column=0, columnspan=3, sticky="ew")

    def create_palette(self) -> None:
        frame = ttk.Frame(self, padding=(10, 0, 6, 10))
        frame.grid(row=1, column=0, sticky="ns")
        frame.rowconfigure(2, weight=1)

        ttk.Label(frame, text="Actions").grid(row=0, column=0, sticky="w", pady=(0, 6))
        search = ttk.Entry(frame, textvariable=self.search_var, width=28)
        search.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        search.bind("<KeyRelease>", lambda _event: self.refresh_palette())

        self.palette = tk.Listbox(frame, width=34, height=24, activestyle="dotbox", exportselection=False)
        self.palette.grid(row=2, column=0, sticky="ns")
        self.palette.bind("<Double-Button-1>", self.add_selected_template)
        self.palette.bind("<ButtonPress-1>", self.start_template_drag)
        self.palette.bind("<ButtonRelease-1>", self.drop_template)
        self.palette.bind("<<ListboxSelect>>", self.show_template_status)
        self.refresh_palette()

    def create_timeline(self) -> None:
        frame = ttk.Frame(self, padding=(6, 0, 6, 10))
        frame.grid(row=1, column=1, sticky="nsew")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        header = ttk.Frame(frame)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Timeline").grid(row=0, column=0, sticky="w")
        ttk.Button(header, text="Up", command=lambda: self.move_selected(-1)).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(header, text="Down", command=lambda: self.move_selected(1)).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(header, text="Duplicate", command=self.duplicate_selected).grid(row=0, column=3, padx=(0, 6))
        ttk.Button(header, text="Delete", command=self.delete_selected).grid(row=0, column=4)

        self.timeline = tk.Listbox(frame, activestyle="dotbox", exportselection=False)
        self.timeline.grid(row=1, column=0, sticky="nsew")
        self.timeline.bind("<<ListboxSelect>>", self.on_timeline_select)
        self.timeline.bind("<ButtonPress-1>", self.start_action_drag)
        self.timeline.bind("<B1-Motion>", self.drag_action)

        hint = ttk.Label(frame, text="Drag actions here, reorder by dragging timeline rows, then save.")
        hint.grid(row=2, column=0, sticky="w", pady=(8, 0))

    def create_properties(self) -> None:
        frame = ttk.Frame(self, padding=(6, 0, 10, 10))
        frame.grid(row=1, column=2, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Selected Action").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))
        ttk.Label(frame, text="Opcode").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(frame, textvariable=self.opcode_var, state="readonly", width=28).grid(row=1, column=1, columnspan=2, sticky="ew", pady=3)

        ttk.Label(frame, text="Audio").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(frame, textvariable=self.audio_var, width=28).grid(row=2, column=1, sticky="ew", pady=3)
        ttk.Button(frame, text="Browse", command=self.pick_audio_file).grid(row=2, column=2, padx=(6, 0), pady=3)

        ttk.Label(frame, text="Value").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(frame, textvariable=self.value_var, width=28).grid(row=3, column=1, columnspan=2, sticky="ew", pady=3)
        ttk.Button(frame, text="Apply Action", command=self.apply_selected_action).grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 18))

        ttk.Separator(frame).grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        ttk.Label(frame, text="Robot Parameters").grid(row=6, column=0, columnspan=3, sticky="w", pady=(0, 6))

        for row_offset, key in enumerate(BASE_PARAMETERS, start=7):
            ttk.Label(frame, text=key).grid(row=row_offset, column=0, sticky="w", pady=2)
            ttk.Entry(frame, textvariable=self.parameter_vars[key], width=28).grid(row=row_offset, column=1, columnspan=2, sticky="ew", pady=2)

        ttk.Button(frame, text="Apply Parameters", command=self.apply_parameters).grid(
            row=7 + len(BASE_PARAMETERS), column=0, columnspan=3, sticky="ew", pady=(8, 0)
        )

    def refresh_palette(self) -> None:
        query = self.search_var.get().lower().strip()
        self.palette.delete(0, tk.END)
        for template in self.templates:
            if query and query not in template.label.lower() and query not in template.opcode.lower():
                continue
            suffix = "" if template.exportable else "  [reference]"
            self.palette.insert(tk.END, f"{template.label} ({template.opcode}){suffix}")

    def visible_templates(self) -> list[ActionTemplate]:
        query = self.search_var.get().lower().strip()
        return [
            template
            for template in self.templates
            if not query or query in template.label.lower() or query in template.opcode.lower()
        ]

    def start_template_drag(self, event: tk.Event) -> None:
        self.drag_template_index = self.palette.nearest(event.y)

    def drop_template(self, _event: tk.Event) -> None:
        if self.drag_template_index is None:
            return
        if self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery()) is self.timeline:
            templates = self.visible_templates()
            if 0 <= self.drag_template_index < len(templates):
                self.add_template_to_timeline(templates[self.drag_template_index])
        self.drag_template_index = None

    def add_selected_template(self, _event: tk.Event | None = None) -> None:
        selected = self.palette.curselection()
        if not selected:
            return
        templates = self.visible_templates()
        self.add_template_to_timeline(templates[selected[0]])

    def add_template_to_timeline(self, template: ActionTemplate) -> None:
        action = TimelineAction.from_template(template)
        self.actions.append(action)
        self.refresh_timeline(select_index=len(self.actions) - 1)
        if not template.exportable:
            self.status_var.set(f"Added reference action: {template.label}")
        else:
            self.status_var.set(f"Added action: {template.label}")

    def start_action_drag(self, event: tk.Event) -> None:
        self.drag_action_index = self.timeline.nearest(event.y)

    def drag_action(self, event: tk.Event) -> None:
        if self.drag_action_index is None or not self.actions:
            return
        target = self.timeline.nearest(event.y)
        if target == self.drag_action_index or target < 0 or target >= len(self.actions):
            return
        action = self.actions.pop(self.drag_action_index)
        self.actions.insert(target, action)
        self.drag_action_index = target
        self.refresh_timeline(select_index=target)

    def refresh_timeline(self, select_index: int | None = None) -> None:
        self.timeline.delete(0, tk.END)
        for index, action in enumerate(self.actions):
            self.timeline.insert(tk.END, action.display_text(index))
        if select_index is not None and 0 <= select_index < len(self.actions):
            self.timeline.selection_set(select_index)
            self.timeline.activate(select_index)
            self.timeline.see(select_index)
            self.load_action_into_editor(select_index)

    def on_timeline_select(self, _event: tk.Event | None = None) -> None:
        selected = self.timeline.curselection()
        if selected:
            self.load_action_into_editor(selected[0])

    def load_action_into_editor(self, index: int) -> None:
        action = self.actions[index]
        self.opcode_var.set(action.opcode)
        self.audio_var.set(action.audio_file)
        self.value_var.set(str(action.value))
        self.status_var.set(f"Selected timeline action {index + 1}")

    def selected_action_index(self) -> int | None:
        selected = self.timeline.curselection()
        if not selected:
            messagebox.showinfo("No action selected", "Select an action in the timeline first.")
            return None
        return selected[0]

    def apply_selected_action(self) -> None:
        index = self.selected_action_index()
        if index is None:
            return
        action = self.actions[index]
        action.audio_file = self.audio_var.get().strip()
        action.value = coerce_int(self.value_var.get().strip(), default=action.value)
        self.refresh_timeline(select_index=index)
        self.status_var.set(f"Updated action {index + 1}")

    def pick_audio_file(self) -> None:
        initial_dir = INCURSIONS_DIR / "Audio_Files"
        selected = filedialog.askopenfilename(
            title="Select audio file",
            initialdir=str(initial_dir if initial_dir.exists() else INCURSIONS_DIR),
            filetypes=[("Audio files", "*.mp3 *.wav *.ogg"), ("All files", "*.*")],
        )
        if selected:
            self.audio_var.set(selected)

    def move_selected(self, direction: int) -> None:
        index = self.selected_action_index()
        if index is None:
            return
        target = index + direction
        if target < 0 or target >= len(self.actions):
            return
        self.actions[index], self.actions[target] = self.actions[target], self.actions[index]
        self.refresh_timeline(select_index=target)

    def duplicate_selected(self) -> None:
        index = self.selected_action_index()
        if index is None:
            return
        original = self.actions[index]
        clone = TimelineAction(
            opcode=original.opcode,
            audio_file=original.audio_file,
            value=original.value,
            label=original.label,
            exportable=original.exportable,
        )
        self.actions.insert(index + 1, clone)
        self.refresh_timeline(select_index=index + 1)

    def delete_selected(self) -> None:
        index = self.selected_action_index()
        if index is None:
            return
        del self.actions[index]
        next_index = min(index, len(self.actions) - 1)
        self.refresh_timeline(select_index=next_index if self.actions else None)
        self.status_var.set("Deleted action")

    def show_template_status(self, _event: tk.Event) -> None:
        selected = self.palette.curselection()
        if not selected:
            return
        template = self.visible_templates()[selected[0]]
        self.status_var.set(template.description)

    def apply_parameters(self) -> None:
        parsed = dict(self.parameters)
        for key, var in self.parameter_vars.items():
            raw_value = var.get().strip()
            if key == "gait_type":
                parsed[key] = raw_value
            else:
                try:
                    parsed[key] = float(raw_value)
                except ValueError:
                    messagebox.showerror("Invalid parameter", f"{key} must be a number.")
                    return
        self.parameters = parsed
        self.status_var.set("Updated robot parameters")

    def open_json(self) -> None:
        selected = filedialog.askopenfilename(
            title="Open action sequence JSON",
            initialdir=str(INCURSIONS_DIR),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected:
            self.load_file(Path(selected))

    def load_file(self, path: Path) -> None:
        try:
            data = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Could not open JSON", str(exc))
            return

        self.json_path = path
        self.path_var.set(str(path))
        self.parameters = {key: data[key] for key in BASE_PARAMETERS}
        for key, value in self.parameters.items():
            self.parameter_vars[key].set(str(value))
        self.actions = [TimelineAction.from_json_item(item) for item in data.get("action_list", [])]
        self.refresh_timeline(select_index=0 if self.actions else None)
        self.status_var.set(f"Loaded {len(self.actions)} actions from {path.name}")

    def save_json(self) -> None:
        self.apply_parameters()
        try:
            write_json(self.json_path, self.parameters, self.actions)
        except OSError as exc:
            messagebox.showerror("Could not save JSON", str(exc))
            return
        self.status_var.set(f"Saved {len([a for a in self.actions if a.exportable])} actions to {self.json_path.name}")

    def save_json_as(self) -> None:
        selected = filedialog.asksaveasfilename(
            title="Save action sequence JSON",
            initialdir=str(INCURSIONS_DIR),
            initialfile=self.json_path.name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected:
            self.json_path = Path(selected)
            self.path_var.set(str(self.json_path))
            self.save_json()


def main() -> None:
    app = ActionSequenceBuilder()
    app.mainloop()


if __name__ == "__main__":
    main()
