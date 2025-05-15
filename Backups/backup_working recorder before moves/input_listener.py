# === input_listener.py ===
import time
import threading
import win32gui
import os
import json
from pynput import mouse, keyboard
from pynput.keyboard import Key
from logic import run_macro

print("[DEBUG] input_listener.py loaded")

hold_flags = {}
macros = []
pressed_keys = set()

def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def load_vk_map():
    try:
        with open("vk_map.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load vk_map.json: {e}")
        return {}

VK_MAP = load_vk_map()

def load_macros():
    global macros
    macros = []
    for filename in os.listdir("macros"):
        if filename.endswith(".json"):
            path = os.path.join("macros", filename)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["__path"] = path.replace("\\", "/")


                button_name = data.get("bind", {}).get("button")
                if button_name:
                    data["bind"]["button_vk"] = VK_MAP.get(button_name.lower())

                for action in data.get("actions", []):
                    key_name = action.get("key")
                    if key_name:
                        action["key_vk"] = VK_MAP.get(key_name.lower())

                    if action.get("action") == "hotkey" and "keys" in action:
                        keys = action["keys"]
                        if isinstance(keys, list):
                            action["keys_vk"] = [VK_MAP.get(k.lower()) for k in keys if k.lower() in VK_MAP]

                if "keys" in data.get("bind", {}):
                    keys = data["bind"]["keys"]
                    if isinstance(keys, list):
                        data["bind"]["keys_vk"] = [VK_MAP.get(k.lower()) for k in keys if k.lower() in VK_MAP]

                if "hotkey" in data.get("bind", {}):
                    combo = data["bind"]["hotkey"]
                    if isinstance(combo, list) and len(combo) >= 1:
                        hotkey_vk = [VK_MAP.get(k.lower()) for k in combo if k.lower() in VK_MAP]
                        if len(hotkey_vk) == len(combo):
                            data["bind"]["hotkey_vk"] = hotkey_vk

                print(f"[LOADED] {path} →", json.dumps(data, indent=2))
                macros.append(data)

                btn = data.get("bind", {}).get("button_vk")
                if btn is not None:
                    hold_flags.setdefault(btn, False)

def execute_macro(macro, button_vk=None):
    settings = macro["settings"]
    actions = macro["actions"]
    mode = settings.get("mode", "press")
    repeat = settings.get("repeat", 1)
    
    def run():
        if mode == "hold" and button_vk:
            while hold_flags.get(button_vk, False):
                run_macro(actions, original_vk=button_vk)
        else:
            for _ in range(repeat):
                run_macro(actions, original_vk=button_vk)

    threading.Thread(target=run, daemon=True).start()

def check_and_execute(macro, btn_code, pressed):
    bind = macro.get("bind", {})
    match_button = bind.get("button_vk") == btn_code
    match_window = bind.get("window", "").lower() in get_active_window_title().lower()

    match_combo = False
    if "keys_vk" in bind:
        match_combo = all(code in pressed_keys for code in bind["keys_vk"])

    match_sequence = False
    if "hotkey_vk" in bind:
        expected = bind["hotkey_vk"]
        if len(expected) >= 1 and btn_code == expected[-1]:
            match_sequence = all(code in pressed_keys for code in expected[:-1])

    if not (match_window and (match_button or match_combo or match_sequence)):
        return

    mode = macro["settings"].get("mode", "press")

    if mode == "press" and pressed:
        execute_macro(macro, btn_code)
    elif mode == "release" and not pressed:
        execute_macro(macro, btn_code)
    elif mode == "hold" and btn_code:
        hold_flags[btn_code] = pressed
        if pressed:
            execute_macro(macro, btn_code)

def get_vk_name(key):
    # Special handling for Ctrl + A..Z as ASCII control codes
    if hasattr(key, 'char') and key.char:
        c = key.char
        if len(c) == 1 and 1 <= ord(c) <= 26:
            return ord(c.upper()) + 64  #             return ord(c.upper()) + 64  #  → 65 ('A'),             return ord(c.upper()) + 64  #  → 65 ('A'),  → 83 ('S')
    name = str(key).replace("Key.", "").lower()
    if name in VK_MAP:
        return VK_MAP[name]

    try:
        vk = key.vk
        if vk != 255:
            return vk
    except AttributeError:
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

    print(f"[WARN] Could not resolve VK: {key}")
    return None

def on_mouse_click(x, y, button, pressed):
    vk_map = {"left": 1, "right": 2, "middle": 3}
    btn_vk = vk_map.get(button.name)
    print(f"[DEBUG] Mouse event: {button.name}, VK: {btn_vk}, Pressed: {pressed}")
    if btn_vk is not None:
        for macro in macros:
            check_and_execute(macro, btn_vk, pressed)

def on_keyboard_press(key):
    k = get_vk_name(key)
    print(f"[DEBUG] Pressed key: {key}, VK: {k}")
    if k is None:
        return
    if k not in pressed_keys:
        pressed_keys.add(k)
        for macro in macros:
            check_and_execute(macro, k, True)

def on_keyboard_release(key):
    k = get_vk_name(key)
    if k is None:
        return
    if k in pressed_keys:
        pressed_keys.remove(k)
    for macro in macros:
        check_and_execute(macro, k, False)

def start_listening():
    load_macros()
    print("[INFO] Loaded macros:", len(macros))
    print("[INFO] Listening for mouse and keyboard...")

    mouse_listener = mouse.Listener(on_click=on_mouse_click)
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_press=on_keyboard_press, on_release=on_keyboard_release)
    keyboard_listener.start()

    while True:
        time.sleep(0.01)
