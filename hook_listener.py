# === hook_listener.py ===
import ctypes
import ctypes.wintypes
import threading
import time
import json
import os
import traceback
import win32gui
from logic import run_macro
import keyboard


print("[DEBUG] hook_listener.py loaded")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14
WM_KEYDOWN = 0x0100
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204
WM_MBUTTONDOWN = 0x0207
WM_XBUTTONDOWN = 0x020B

LLKHF_INJECTED = 0x10
LLMHF_INJECTED = 0x01

keyboard_hook = None
mouse_hook = None
keyboard_proc_ref = None
mouse_proc_ref = None

VK_MAP = {}
ALIASES = {}
macros = []

def load_vk_map():
    global VK_MAP, ALIASES
    try:
        with open("vk_map.json", "r", encoding="utf-8") as f:
            VK_MAP = json.load(f)
            ALIASES = VK_MAP.get("aliases", {})
            print("[DEBUG] VK map loaded:", len(VK_MAP))
    except Exception as e:
        print(f"[ERROR] Failed to load vk_map.json: {e}")

def get_active_window_title():
    try:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()
    except:
        return ""

def load_macros():
    global macros
    macros.clear()

    print("[DEBUG] Loading macros...")
    for filename in os.listdir("macros"):
        if filename.endswith(".json"):
            try:
                with open(os.path.join("macros", filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    bind = data.get("bind", {})
                    btn = bind.get("button")
                    if btn:
                        vk = VK_MAP.get(btn.lower())
                        print(f"[DEBUG] Binding macro: {btn.lower()} → VK={vk} from {filename}")
                        bind["button_vk"] = vk
                        for action in data.get("actions", []):
                            key = action.get("key")
                            if key:
                                action["key_vk"] = VK_MAP.get(key.lower())
                        print(f"[DEBUG] Loaded macro {filename}: {btn} → VK {vk}")
                    macros.append(data)
                    print(f"[DEBUG] Appended macro for VK={vk}: {data['bind']}")

            except Exception as e:
                print(f"[ERROR] Failed to load macro {filename}: {e}")

def match_macro(vk):
    print(f"[DEBUG] Matching macro for VK={vk}")
    title = get_active_window_title()
    for macro in macros:
        bind = macro.get("bind", {})
        print(f"[DEBUG] Checking macro bind: {bind}")

        if bind.get("button_vk") != vk:
            continue
        if bind.get("window", "").lower() not in title:
            continue
        return macro
    return None

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", ctypes.wintypes.DWORD),
        ("scanCode", ctypes.wintypes.DWORD),
        ("flags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.wintypes.LPARAM),
    ]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", ctypes.wintypes.POINT),
        ("mouseData", ctypes.c_ulong),
        ("flags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.wintypes.LPARAM),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)

def keyboard_proc(nCode, wParam, lParam):
    try:
        if nCode == 0:
            kbd = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk = kbd.vkCode

            if kbd.flags & LLKHF_INJECTED:
                return user32.CallNextHookEx(None, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))

            if wParam == WM_KEYDOWN:
                print(f"[KEYBOARD] VK={vk} pressed")
                macro = match_macro(vk)
                if macro:
                    print(f"[SUPPRESS] Keyboard VK={vk} matched. Suppressing and launching macro.")
                    threading.Thread(target=run_macro, args=(macro["actions"],), daemon=True).start()
                    return 1
    except Exception as e:
        print(f"[HOOK ERROR] keyboard_proc: {e}")
        traceback.print_exc()

    return user32.CallNextHookEx(None, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))

def mouse_proc(nCode, wParam, lParam):
    try:
        if nCode != 0:
            return user32.CallNextHookEx(None, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))

        if wParam == 0x0200:
            return user32.CallNextHookEx(None, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))

        ms = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents

        if ms.flags & LLMHF_INJECTED:
            return user32.CallNextHookEx(None, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))

        vk = None
        x_id = None

        if wParam == WM_LBUTTONDOWN:
            vk = 1
        elif wParam == WM_RBUTTONDOWN:
            vk = 2
        elif wParam == WM_MBUTTONDOWN:
            vk = 3
        elif wParam == WM_XBUTTONDOWN:
            x_id = (ms.mouseData >> 16) & 0xFFFF
            if x_id == 1:
                vk = 4
                print("[XBUTTON] X1 clicked")
            elif x_id == 2:
                vk = 5
                print("[XBUTTON] X2 clicked")
            else:
                print(f"[XBUTTON] Unknown x_id={x_id}")
                return user32.CallNextHookEx(None, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))

        if vk is not None:
            print(f"[MOUSE] VK={vk} event={hex(wParam)}")
            macro = match_macro(vk)
            if macro:
                print(f"[SUPPRESS] Mouse VK={vk} matched. Suppressing and launching macro.")
                threading.Thread(target=run_macro, args=(macro["actions"],), daemon=True).start()
                return 1  # ← suppress только если действительно запускали макрос
            else:
                print(f"[MOUSE] No macro matched for VK={vk}, x_id={x_id}")

    except Exception as e:
        print(f"[HOOK ERROR] mouse_proc: {e}")
        traceback.print_exc()

    return user32.CallNextHookEx(None, nCode, wParam, ctypes.cast(lParam, ctypes.c_void_p))



def install_hooks():
    global keyboard_hook, mouse_hook, keyboard_proc_ref, mouse_proc_ref

    keyboard_proc_ref = HOOKPROC(keyboard_proc)
    mouse_proc_ref = HOOKPROC(mouse_proc)

    keyboard_hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, keyboard_proc_ref, None, 0)
    mouse_hook = user32.SetWindowsHookExW(WH_MOUSE_LL, mouse_proc_ref, None, 0)


    if not keyboard_hook or not mouse_hook:
        print("[ERROR] Failed to install hooks.")
        return False

    return True

def uninstall_hooks():
    if keyboard_hook:
        user32.UnhookWindowsHookEx(keyboard_hook)
    if mouse_hook:
        user32.UnhookWindowsHookEx(mouse_hook)
    print("[INFO] Hooks removed.")

def listen_forever():
    try:
        load_vk_map()
        load_macros()
        if not install_hooks():
            return

        print("[INFO] Hooks installed. Listening...")

        threading.Thread(target=esc_listener, daemon=True).start()

        
        msg = ctypes.wintypes.MSG()
        while True:
            while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.01)
    except Exception as e:
        print(f"[FATAL ERROR] Listener crashed: {e}")
        traceback.print_exc()
        uninstall_hooks()

def esc_listener():
    print("[ESC] Press ESC to exit.")
    keyboard.wait("esc")
    print("[ESC] Exit triggered.")
    uninstall_hooks()
    os._exit(0)
