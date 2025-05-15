# Macro Engine

A universal Python-based macro engine for executing and recording keyboard/mouse macros with full support for combos, delays, modes, and hotkey bindings.

## Features

- Live macro recording with custom settings
- Supports keyboard and mouse events (incl. X1/X2)
- VK code auto-mapping from human-readable names
- Modes: press / release / hold / loop (with repeat count)
- Macros stored as editable JSON files
- Per-window targeting (e.g. bind only in Chrome)
- Modular design for future expansion

## Getting Started

```bash
git clone https://github.com/Rasslabsya4el/Script.git
cd Script
pip install -r requirements.txt  # if needed
```

## Usage

### Running macro player:
```bash
python main.py
```

### Running macro recorder:
```bash
python recorder.py
```

During recording, the following inputs will be requested:

```python
macro_name   = input("Enter macro file name (without extension): ")
bind_input   = input("Enter bind (e.g. f or ctrl+a): ")
bind_window  = input("Enter window title keyword (e.g. chrome): ")
mode         = input("Enter mode (press / release / hold): ")
repeat       = int(input("Enter repeat count (default 1): ") or 1)
delay_input  = input("Enter delay mode (number / blank for 15 / 'real'): ")
```

## Project Structure

```
/macros              - JSON macros (editable by hand)
/modules             - Core modules (input, logic, etc.)
vk_map.json          - Key name to VK-code mapping
main.py              - Macro player
recorder.py          - Macro recorder
spec_macro_format.txt- Macro JSON format description
```

## Example Macro

```json
{
  "bind": {
    "key": "f",
    "mode": "press",
    "window": "chrome"
  },
  "settings": {
    "repeat": 1
  },
  "actions": [
    {"action": "press", "key": "6"},
    {"action": "delay", "ms": 15},
    {"action": "release", "key": "6"}
  ]
}
```

## TODO

- [ ] Suppression of original input
- [ ] GUI editor for macros
- [ ] Conditional actions and variables
- [ ] Profile system for multiple macro sets

## Feedback

Open an issue or fork and contribute.

## License

MIT
