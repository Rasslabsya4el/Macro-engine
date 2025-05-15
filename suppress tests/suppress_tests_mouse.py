import ctypes
import ctypes.wintypes
import threading
import keyboard
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Константы
WH_MOUSE_LL = 14
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205

LowLevelMouseProc = ctypes.WINFUNCTYPE(
    ctypes.c_int,
    ctypes.c_int,
    ctypes.wintypes.WPARAM,
    ctypes.wintypes.LPARAM,
)

# Глобальные переменные
hook_pointer = None
hHook = None
stop_event = threading.Event()

def hook_proc(nCode, wParam, lParam):
    if nCode == 0:
        if wParam == WM_RBUTTONDOWN:
            print(f"[DEBUG] Mouse event: wParam={wParam}")

            print("[HOOK] RMB suppressed → sending '1'")
            keyboard.write("1")
            return 1  # Подавить нажатие ПКМ
        elif wParam == WM_RBUTTONUP:
            print(f"[DEBUG] Mouse event: wParam={wParam}")

            return 1  # Подавить отпускание ПКМ
    return user32.CallNextHookEx(hHook, nCode, wParam, ctypes.c_void_p(lParam))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def esc_listener():
    keyboard.wait("esc")
    print("[EXIT] ESC pressed. Unhooking and exiting...")
    if hHook:
        user32.UnhookWindowsHookEx(hHook)
    stop_event.set()
    ctypes.windll.kernel32.ExitProcess(0)

def install_hook():
    global hook_pointer, hHook
    hook_pointer = LowLevelMouseProc(hook_proc)
    hHook = user32.SetWindowsHookExW(
        WH_MOUSE_LL,
        hook_pointer,
        None,  # без DLL
        0
    )
    if not hHook:
        err = kernel32.GetLastError()
        print(f"[ERROR] Failed to install hook. Code {err} → {ctypes.FormatError(err)}")
        return False
    return True

def main():
    print("[DEBUG] Admin rights:", is_admin())
    if not install_hook():
        return
    print("[INFO] Hook installed. RMB will type '1'. Press ESC to exit.")
    threading.Thread(target=esc_listener, daemon=True).start()
    msg = ctypes.wintypes.MSG()
    while not stop_event.is_set():
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.01)

if __name__ == "__main__":
    main()
