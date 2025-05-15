import json
import time
from pynput import keyboard, mouse

# === КЛАССЫ ===

class Action:
    def __init__(self, action, key=None, ms=None, x=None, y=None, duration=None):
        self.action = action
        self.key = key
        self.ms = ms
        self.x = x
        self.y = y
        self.duration = duration

    def to_line(self):
        if self.action == "delay":
            return f'{{"action": "delay", "ms": {self.ms}}}'
        elif self.action == "move":
            return f'{{"action": "move", "x": {self.x}, "y": {self.y}, "duration": {self.duration}}}'
        elif self.action == "scroll":
            return f'{{"action": "scroll", "clicks": {self.ms}}}'

        else:
            return f'{{"action": "{self.action}", "key": "{self.key}"}}'

class Macro:
    def __init__(self, bind, settings, actions):
        self.bind = bind
        self.settings = settings
        self.actions = actions

# === ЗАГРУЗКА VK MAP ===

with open("vk_map.json", "r", encoding="utf-8") as f:
    VK_MAP = json.load(f)

RAW_STOP_KEY = keyboard.Key.esc
_key_str = str(RAW_STOP_KEY).strip("'").lower()
stop_key = VK_MAP["aliases"].get(_key_str, _key_str)

recorded_actions = []
last_time = time.time()

# === INPUT ===

macro_name = input("Enter macro file name (without extension): ").strip()
bind_input = input("Enter bind (single key or combo, e.g. f or ctrl+a): ").strip().lower()
bind_window = input("Enter window title keyword (e.g. chrome): ").strip()
mode = input("Enter mode (press / release / hold): ").strip().lower()
repeat = int(input("Enter repeat count (default 1): ") or 1)

delay_input = input("Enter delay mode (number / empty for 15 / 'real' for actual timing): ").strip()
if delay_input == "real":
    delay_mode = "real"
    fixed_delay = None
elif delay_input == "":
    delay_mode = "fixed"
    fixed_delay = 15
else:
    try:
        fixed_delay = int(delay_input)
        delay_mode = "fixed"
    except ValueError:
        print("Invalid delay input, defaulting to 15.")
        fixed_delay = 15
        delay_mode = "fixed"

record_coords = input("Record mouse coordinates before clicks? (1 = yes, empty = no): ").strip() == "1"

macro_path = f"macros/{macro_name}.json"

if "+" in bind_input:
    keys = [k.strip() for k in bind_input.split("+")]
    bind_section = {
        "hotkey": keys,
        "window": bind_window
    }
else:
    bind_section = {
        "button": bind_input,
        "button_vk": VK_MAP.get(bind_input, 0),
        "window": bind_window
    }

# === DELAY ===

def add_delay():
    global last_time
    now = time.time()

    if delay_mode == "real":
        delay = int((now - last_time) * 1000)
        if delay > 0:
            recorded_actions.append(Action("delay", ms=delay))
    else:
        recorded_actions.append(Action("delay", ms=fixed_delay))

    last_time = now

# === UTILS ===

def get_vk(key):
    if hasattr(key, 'char') and key.char:
        c = key.char
        if 1 <= ord(c) <= 26:
            return ord(c.upper()) + 64
    name = str(key).replace("Key.", "").lower()
    if name in VK_MAP:
        return VK_MAP[name]
    try:
        vk = key.vk
        if vk != 255:
            return vk
    except:
        pass
    if hasattr(key, 'char') and key.char:
        name = key.char.lower()
        if name in VK_MAP:
            return VK_MAP[name]
        if "aliases" in VK_MAP and name in VK_MAP["aliases"]:
            alias_target = VK_MAP["aliases"][name]
            if alias_target in VK_MAP:
                return VK_MAP[alias_target]
    name = str(key).strip("'").lower()
    if name in VK_MAP:
        return VK_MAP[name]
    if "aliases" in VK_MAP and name in VK_MAP["aliases"]:
        alias_target = VK_MAP["aliases"][name]
        if alias_target in VK_MAP:
            return VK_MAP[alias_target]
    return None

def resolve_key_name(key):
    name = str(key).strip("'").lower()
    if "aliases" in VK_MAP and name in VK_MAP["aliases"]:
        return VK_MAP["aliases"][name]
    if len(name) == 1 and name.isascii():
        return name
    return None

def resolve_mouse_button_name(btn_name):
    if "aliases" in VK_MAP and btn_name in VK_MAP["aliases"]:
        return VK_MAP["aliases"][btn_name]
    return btn_name

# === ХУКИ ===


def on_scroll(x, y, dx, dy):
    add_delay()
    if dy > 0:
        recorded_actions.append(Action("scroll", ms=100))
    elif dy < 0:
        recorded_actions.append(Action("scroll", ms=-100))

def on_key_press(key):
    add_delay()
    vk = get_vk(key)
    if vk is not None:
        k = resolve_key_name(key)
        if k:
            recorded_actions.append(Action("press", key=k))

def on_key_release(key):
    add_delay()
    vk = get_vk(key)
    if vk is not None:
        k = resolve_key_name(key)
        if k:
            recorded_actions.append(Action("release", key=k))
    if key == RAW_STOP_KEY:
        return False

def on_click(x, y, button, pressed):
    add_delay()
    btn_name = button.name.lower()
    vk_name = resolve_mouse_button_name(btn_name)
    if vk_name:
        if record_coords and pressed:
            recorded_actions.append(Action("move", x=x, y=y, duration=0))
        action = "press" if pressed else "release"
        recorded_actions.append(Action(action, key=vk_name))

# === ЗАПИСЬ ===

print("[INFO] Recording started. Use your designated stop trigger to finish.")
keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
keyboard_listener.start()
mouse_listener.start()
keyboard_listener.join()
mouse_listener.stop()

print("[INFO] Recording finished. Saving to macro...")

# === ЧИСТКА ===

if len(recorded_actions) >= 2:
    first, second = recorded_actions[0], recorded_actions[1]
    if first.action == "delay" and second.action == "release" and second.key == "enter":
        recorded_actions = recorded_actions[2:]

if len(recorded_actions) >= 3:
    last3 = recorded_actions[-3:]
    if (
        last3[0].action == "press" and last3[0].key == stop_key and
        last3[1].action == "delay" and
        last3[2].action == "release" and last3[2].key == stop_key
    ):
        recorded_actions = recorded_actions[:-3]

# === СОХРАНЕНИЕ ===

macro = Macro(
    bind=bind_section,
    settings={"mode": mode, "repeat": repeat},
    actions=recorded_actions
)

with open(macro_path, "w", encoding="utf-8") as f:
    f.write('{\n')

    # BIND
    f.write('  "bind": {\n')
    if "hotkey" in macro.bind:
        hotkey_list = ', '.join([f'"{k}"' for k in macro.bind["hotkey"]])
        f.write(f'  "hotkey": [{hotkey_list}],\n')
    if "button" in macro.bind:
        f.write(f'  "button": "{macro.bind["button"]}",\n')
    f.write(f'  "window": "{macro.bind["window"]}"\n')
    f.write('},\n')

    # SETTINGS
    f.write('  "settings": {\n')
    f.write(f'  "mode": "{macro.settings["mode"]}",\n')
    f.write(f'  "repeat": {macro.settings["repeat"]}\n')
    f.write('},\n')

    # ACTIONS
    f.write('  "actions": [\n')
    for i, a in enumerate(macro.actions):
        comma = "," if i < len(macro.actions) - 1 else ""
        f.write(f'    {a.to_line()}{comma}\n')
    f.write('  ]\n')

    f.write('}\n')

print(f"[INFO] Saved to macros/{macro_name}.json")
