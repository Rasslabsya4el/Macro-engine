# === logic.py ===
import json
import time
import threading
import ctypes
from ctypes import wintypes
import pyautogui
import input_listener

print("[DEBUG] logic.py loaded")

KEYEVENTF_KEYUP = 0x0002
keybd_event = ctypes.windll.user32.keybd_event

# Загрузка vk_map и pyautogui_buttons
with open("vk_map.json", "r", encoding="utf-8") as f:
    VK_MAP = json.load(f)
    ALIASES = VK_MAP.get("aliases", {})
    PY_BUTTONS = VK_MAP.get("pyautogui_buttons", {})

def press_key(vk_code):
    print(f"[VK] Pressing key {vk_code}")
    keybd_event(vk_code, 0, 0, 0)

def release_key(vk_code):
    print(f"[VK] Releasing key {vk_code}")
    keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

def run_macro(sequence, suppress_original=False, original_vk=None):
    print(f"[DEBUG] Macro running in thread {threading.get_ident()}")
    input_listener.suppress_listening = True

    try:
        for event in sequence:
            action = event.get("action")
            key = event.get("key")
            vk = event.get("key_vk")

            if suppress_original and original_vk and action == "press" and vk == original_vk:
                print(f"[OVERRIDE] Suppressing key {original_vk} (skipped original press)")
                continue

            print(f"[MACRO] Performing: {event}")

            if action == "press":
                if key in PY_BUTTONS:
                    pyautogui.mouseDown(button=PY_BUTTONS[key])
                elif vk:
                    press_key(vk)

            elif action == "release":
                if key in PY_BUTTONS:
                    pyautogui.mouseUp(button=PY_BUTTONS[key])
                elif vk:
                    release_key(vk)

            elif action == "delay":
                time.sleep(event.get("ms", 0) / 1000.0)

            elif action == "move":
                x = event.get("x")
                y = event.get("y")
                duration = event.get("duration", 0)
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y, duration=duration)

            elif action == "click":
                button = event.get("button")
                if button:
                    button = PY_BUTTONS.get(button, button)
                    pyautogui.click(button=button)

            elif action == "mousedown":
                button = event.get("button")
                if button:
                    button = PY_BUTTONS.get(button, button)
                    pyautogui.mouseDown(button=button)

            elif action == "mouseup":
                button = event.get("button")
                if button:
                    button = PY_BUTTONS.get(button, button)
                    pyautogui.mouseUp(button=button)

            elif action == "scroll":
                clicks = event.get("clicks", 0)
                pyautogui.scroll(clicks)

            elif action == "type":
                text = event.get("text", "")
                pyautogui.write(text)

            elif action == "hotkey":
                keys = event.get("keys", [])
                if isinstance(keys, list):
                    pyautogui.hotkey(*keys)

    finally:
        input_listener.suppress_listening = False
