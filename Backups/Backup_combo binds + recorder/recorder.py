# === recorder.py ===
import json
import time
from pynput import keyboard, mouse

with open("vk_map.json", "r", encoding="utf-8") as f:
    VK_MAP = json.load(f)

recorded_actions = []
last_time = time.time()

def add_delay():
    global last_time
    now = time.time()
    delay = int((now - last_time) * 1000)
    if delay > 0:
        recorded_actions.append({"action": "delay", "ms": delay})
    last_time = now

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

def on_key_press(key):
    add_delay()
    vk = get_vk(key)
    if vk is not None:
        recorded_actions.append({"action": "press", "key": str(key).strip("'").lower()})

def on_key_release(key):
    add_delay()
    vk = get_vk(key)
    if vk is not None:
        recorded_actions.append({"action": "release", "key": str(key).strip("'").lower()})
    if key == keyboard.Key.esc:
        return False

def on_click(x, y, button, pressed):
    add_delay()
    btn_map = {"left": "lmb", "right": "rmb", "middle": "mmb"}
    btn_name = button.name.lower()
    vk = btn_map.get(btn_name)
    if vk:
        action = "press" if pressed else "release"
        recorded_actions.append({"action": action, "key": btn_name})

print("[INFO] Recording started. Press ESC to stop.")
keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener.start()
mouse_listener.start()
keyboard_listener.join()
mouse_listener.stop()

print("[INFO] Recording finished. Saving to macro...")

macro_data = {
    "bind": {
        "button": "f",
        "window": "chrome",
        "button_vk": VK_MAP.get("f", 70)
    },
    "settings": {
        "mode": "press",
        "repeat": 1
    },
    "actions": recorded_actions
}

with open("macros/recorded_macro.json", "w", encoding="utf-8") as f:
    lines = [
        '{',
        '  "bind": {',
        f'    "button": "f",',
        f'    "window": "chrome",',
        f'    "button_vk": {VK_MAP.get("f", 70)}',
        '  },',
        '  "settings": {',
        '    "mode": "press",',
        '    "repeat": 1',
        '  },',
        '  "actions": ['
    ]
    for a in recorded_actions:
        if "ms" in a:
            lines.append(f'    {{"action": "delay", "ms": {a["ms"]}}},')
        else:
            lines.append(f'    {{"action": "{a["action"]}", "key": "{a["key"]}"}},')
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]
    lines.append('  ]')
    lines.append('}')
    f.write("\n".join(lines))

print("[INFO] Saved to macros/recorded_macro.json")
