# Macro Engine

A universal Python-based macro engine for executing and recording keyboard/mouse macros with support for combos, delays, execution modes, and per-window targeting.

## Features

- Live macro recording with customizable prompts
- Execution of keyboard and mouse actions, including X1/X2 buttons
- Modes: press / release / hold / loop
- Per-window targeting (binds apply only when specific window is active)
- Editable JSON macros with readable key/button names
- Modular architecture for future extension

## Getting Started

```bash
git clone https://github.com/Rasslabsya4el/Script.git
cd Script
pip install -r requirements.txt  # if needed
```

## Usage

### Run macro player:
```bash
python main.py
```

### Run macro recorder:
```bash
python recorder.py
```

During recording, you will be prompted for:

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
vk_map.json          - VK code mapping (used internally)
/Backups             - Legacy and backup versions
main.py              - Macro player entry point
recorder.py          - Macro recorder script
.gitignore           - Git exclusions
README.md            - This file
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

## Macro Format Reference

Each macro is stored as a JSON file with the following structure:

```json
{
  "bind": { ... },
  "settings": { ... },
  "actions": [ ... ]
}
```

### `bind` (macro trigger)

| Field     | Type     | Example             | Description                          |
|-----------|----------|---------------------|--------------------------------------|
| `key`     | string   | `"f"`               | Keyboard key                         |
| `hotkey`  | array    | `["ctrl", "g"]`     | Key combination (alternative)        |
| `window`  | string   | `"chrome"`          | Applies only to matching window title |

### `settings`

| Field     | Type     | Example             | Description                          |
|-----------|----------|---------------------|--------------------------------------|
| `mode`    | string   | `"press"`           | `press`, `release`, `hold`, or `loop` |
| `repeat`  | number   | `1`, `5`            | Repetition count (ignored in `loop`)  |

### `actions` (macro body)

Each action is an object like this:

```json
{ "action": "type", ...additional parameters... }
```

Supported action types:

| Action     | Example                                                             |
|------------|---------------------------------------------------------------------|
| `press`    | `{"action": "press", "key": "z"}`                                   |
| `release`  | `{"action": "release", "key": "z"}`                                 |
| `delay`    | `{"action": "delay", "ms": 15}`                                     |
| `move`     | `{"action": "move", "x": 800, "y": 400, "duration": 0}`            |
| `click`    | `{"action": "click", "button": "lmb"}`                              |
| `mousedown`| `{"action": "mousedown", "button": "rmb"}`                          |
| `mouseup`  | `{"action": "mouseup", "button": "rmb"}`                            |
| `scroll`   | `{"action": "scroll", "clicks": 300}`                               |
| `type`     | `{"action": "type", "text": "Hello, world!"}`                       |
| `hotkey`   | `{"action": "hotkey", "keys": ["ctrl", "c"]}`                       |

### Loop Mode

If `mode` is set to `"loop"`:
- The macro runs infinitely until the hotkey is pressed again
- The `repeat` setting is ignored
- A 15ms delay is automatically added between iterations

```json
{
  "settings": {
    "mode": "loop"
  }
}
```

### Notes

- Only readable key/button names are used in macros
- VK codes are assigned automatically at runtime using `vk_map.json`
- Mouse buttons: `"lmb"`, `"rmb"`, `"mmb"`, `"x1"`, `"x2"`
- `duration` in `move` is in seconds

## TODO

- [ ] Suppression of native inputs
- [ ] GUI macro editor
- [ ] Conditional logic support
- [ ] Macro profiles

## License

MIT
