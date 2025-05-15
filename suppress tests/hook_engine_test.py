import ctypes
import ctypes.wintypes
import time
import threading
import keyboard
import pyautogui

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Константы
WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14
WM_KEYDOWN = 0x0100
LLKHF_INJECTED = 0x10
stop_event = threading.Event()

# Бинды
binds = {
    70: "F key macro",  # клавиша F
    3: "MMB macro"      # средняя кнопка мыши
}

# Hook refs
keyboard_hook = None
mouse_hook = None
keyboard_proc_ref = None
mouse_proc_ref = None

# Структуры
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
        ("mouseData", ctypes.wintypes.DWORD),
        ("flags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.wintypes.LPARAM),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)

# Сопоставление VK к PyAutoGUI actions
def perform_synthetic_input(vk):
    try:
        if vk == 70:
            print("[TEST] Synthetic key press via PyAutoGUI: F")
            pyautogui.press("z")
        elif vk == 3:
            print("[TEST] Synthetic mouse press via PyAutoGUI: MMB")
            pyautogui.middleClick()
    except Exception as e:
        print("[ERROR] Failed to perform synthetic input:", e)

# Хуки
def keyboard_proc(nCode, wParam, lParam):
    if nCode == 0:
        struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk = struct.vkCode
        if struct.flags & LLKHF_INJECTED:
            return user32.CallNextHookEx(None, nCode, wParam, ctypes.wintypes.LPARAM(lParam))

        if wParam == WM_KEYDOWN and vk in binds:
            print(f"[DEBUG] Suppressed keyboard VK={vk}, event={hex(wParam)}")
            print(f"[TRIGGER] Keyboard VK={vk} → {binds[vk]}")
            threading.Thread(target=perform_synthetic_input, args=(vk,), daemon=True).start()
            return 1
    return user32.CallNextHookEx(None, nCode, wParam, ctypes.wintypes.LPARAM(lParam))

def mouse_proc(nCode, wParam, lParam):
    if nCode == 0:
        struct = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        if struct.flags & 0x01:  # LLMHF_INJECTED = 0x01
            return user32.CallNextHookEx(None, nCode, wParam, ctypes.wintypes.LPARAM(lParam))

        event_to_vk = {
            0x0201: 1,  # LMB down
            0x0202: 1,  # LMB up
            0x0204: 2,  # RMB down
            0x0205: 2,  # RMB up
            0x0207: 3,  # MMB down
            0x0208: 3,  # MMB up
            0x020B: 4,  # X1 down
            0x020C: 4,  # X1 up
            0x020E: 5,  # X2 down
            0x020F: 5,  # X2 up
        }

        vk = event_to_vk.get(wParam)
        if vk and vk in binds:
            print(f"[DEBUG] Suppressed mouse VK={vk}, event={hex(wParam)}")
            print(f"[TRIGGER] Mouse VK={vk} → {binds[vk]}")
            threading.Thread(target=perform_synthetic_input, args=(vk,), daemon=True).start()
            return 1

    return user32.CallNextHookEx(None, nCode, wParam, ctypes.c_void_p(lParam))

# Установка хуков
def install_hooks():
    global keyboard_hook, mouse_hook
    global keyboard_proc_ref, mouse_proc_ref

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
    print("[INFO] Hooks uninstalled.")

def esc_listener():
    keyboard.wait("esc")
    print("[EXIT] ESC pressed. Cleaning up...")
    uninstall_hooks()
    stop_event.set()

def main():
    print("[INFO] Installing hooks. Press F or MMB to test. ESC to exit.")
    if not install_hooks():
        return

    threading.Thread(target=esc_listener, daemon=True).start()

    msg = ctypes.wintypes.MSG()
    while not stop_event.is_set():
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.01)

    print("[INFO] Exited cleanly.")

if __name__ == "__main__":
    main()
