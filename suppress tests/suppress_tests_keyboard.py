import keyboard

def handle_event(e):
    if e.event_type == 'down' and e.name == 'z':
        print("[HOOK] Suppressed 'z' → triggering 's'")
        keyboard.send('s')
        return False  # 🔕 отменить 'z'
    return True  # остальные клавиши проходят

print("[INFO] Press 'z' to test suppression. Should type 's'. Press ESC to exit.")

keyboard.hook(handle_event, suppress=True)
keyboard.wait('esc')
