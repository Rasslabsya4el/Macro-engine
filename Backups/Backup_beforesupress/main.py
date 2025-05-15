# === main.py ===
from input_listener import start_listening
import logic

if __name__ == "__main__":
    print("[INFO] Starting macro engine...")

    # Временный тест
    logic.run_macro([
        {"action": "press", "key_vk": 72},
        {"action": "delay", "ms": 50},
        {"action": "release", "key_vk": 72}
    ])

    start_listening()