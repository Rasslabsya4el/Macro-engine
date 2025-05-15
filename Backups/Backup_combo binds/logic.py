# === logic.py ===
import json
import time
import threading
import ctypes
from ctypes import wintypes
import pyautogui

print("[DEBUG] logic.py loaded")

# Константы
KEYEVENTF_KEYUP = 0x0002

# Старый API для ввода (работает почти всегда)
keybd_event = ctypes.windll.user32.keybd_event


def press_key(vk_code):
    print(f"[VK] Pressing key {vk_code}")
    keybd_event(vk_code, 0, 0, 0)


def release_key(vk_code):
    print(f"[VK] Releasing key {vk_code}")
    keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


def run_macro(sequence, suppress_original=False, original_vk=None):
    print(f"[DEBUG] Macro running in thread {threading.get_ident()}")

    for event in sequence:
        action = event.get("action")
        vk = event.get("key_vk")

        if suppress_original and original_vk and action == "press" and vk == original_vk:
            print(f"[OVERRIDE] Suppressing key {original_vk} (skipped original press)")
            continue

        print(f"[MACRO] Performing: {event}")

        if action == "press" and vk:
            press_key(vk)
        elif action == "release" and vk:
            release_key(vk)
        elif action == "delay":
            time.sleep(event.get("ms", 0) / 1000.0)
        elif action == "move":
            x = event.get("x")
            y = event.get("y")
            if x is not None and y is not None:
                pyautogui.moveTo(x, y)
        elif action == "click":
            button = event.get("button", "left")
            pyautogui.click(button=button)
        elif action == "mousedown":
            button = event.get("button", "left")
            pyautogui.mouseDown(button=button)
        elif action == "mouseup":
            button = event.get("button", "left")
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