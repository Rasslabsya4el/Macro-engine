# === input_listener.py ===
import time
import threading
import win32gui
import os
import json
from pynput import mouse, keyboard
from logic import run_macro

print("[DEBUG] input_listener.py loaded")

hold_flags = {}
macros = []


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
                data["__path"] = path

                # Преобразование button → button_vk (всегда)
                button_name = data.get("bind", {}).get("button")
                if button_name:
                    data["bind"]["button_vk"] = VK_MAP.get(button_name.lower())

                # Преобразование key → key_vk в actions (всегда)
                for action in data.get("actions", []):
                    key_name = action.get("key")
                    if key_name:
                        action["key_vk"] = VK_MAP.get(key_name.lower())

                print(f"[LOADED] {path} →", json.dumps(data, indent=2))

                macros.append(data)

                btn = data.get("bind", {}).get("button_vk")
                if btn is not None:
                    hold_flags.setdefault(btn, False)


def execute_macro(macro, button_vk):
    settings = macro["settings"]
    actions = macro["actions"]
    mode = settings.get("mode", "press")
    repeat = settings.get("repeat", 1)
    suppress = settings.get("suppress", False)

    def run():
        if mode == "hold":
            while hold_flags.get(button_vk, False):
                run_macro(actions, suppress_original=suppress, original_vk=button_vk)
        else:
            for _ in range(repeat):
                run_macro(actions, suppress_original=suppress, original_vk=button_vk)

    threading.Thread(target=run, daemon=True).start()


def check_and_execute(macro, btn_code, pressed):
    bind = macro.get("bind", {})
    match_button = bind.get("button_vk") == btn_code
    match_window = bind.get("window", "").lower() in get_active_window_title().lower()
    if not (match_button and match_window):
        return

    mode = macro["settings"].get("mode", "press")

    if mode == "press" and pressed:
        execute_macro(macro, btn_code)
    elif mode == "release" and not pressed:
        execute_macro(macro, btn_code)
    elif mode == "hold":
        hold_flags[btn_code] = pressed
        if pressed:
            execute_macro(macro, btn_code)


def get_vk_name(key):
    try:
        return key.vk
    except AttributeError:
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
    if k is not None:
        for macro in macros:
            check_and_execute(macro, k, True)


def on_keyboard_release(key):
    k = get_vk_name(key)
    if k is not None:
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
