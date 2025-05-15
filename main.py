# === main.py ===
from hook_listener import listen_forever
import logic

if __name__ == "__main__":
    print("[INFO] Starting macro engine with suppression.")
    listen_forever()
