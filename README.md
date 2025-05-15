# Macro Engine

A universal Python-based macro engine for executing and recording keyboard/mouse macros with support for combos, delays, execution modes, and per-window targeting.

---

## Features

- Live macro recording with customizable prompts
- Execution of keyboard and mouse actions, including scrolls and extra buttons (X1/X2)
- Modes: `press`, `release`, `hold`, `loop`
- Per-window targeting (binds apply only when specific window is active)
- Editable JSON macros with readable key/button names only (no VK codes)
- Modular structure with internal VK resolution via `vk_map.json`

---

## Getting Started

```bash
git clone https://github.com/Rasslabsya4el/Script.git
cd Script
pip install -r requirements.txt  # if needed
```

---

## Usage

### Run macro player:
```bash
python main.py
```

### Run macro recorder:
```bash
python recorder.py
```

You will be prompted for the following:

| Prompt         | Description                                                                 |
|----------------|------------------------------------------------------------------------------|
| `macro_name`   | File name for the macro (without `.json`)                                   |
| `bind_input`   | Key or combo, e.g. `f`, `ctrl+a`, `x1+enter`                                 |
| `bind_window`  | Keyword from window title, e.g. `chrome`                                     |
| `mode`         | One of: `press`, `release`, `hold`, `loop`                                   |
| `repeat`       | Number of repetitions (ignored if mode is `loop`)                            |
| `delay_input`  | One of: `real` (recorded timing), number (e.g. `100` ms), or empty (= 15 ms) |

You can also manually edit the resulting JSON in `/macros` after recording.

---

## Macro Format

Each macro is a JSON file structured like this:

```json
{
  "bind": { ... },
  "settings": { ... },
  "actions": [ ... ]
}
```

### `bind` (macro trigger)

Macros can be triggered by:
- A single `button` (keyboard or mouse)
- A multi-key `hotkey` sequence

| Field     | Type     | Example               | Description                                |
|-----------|----------|-----------------------|--------------------------------------------|
| `button`  | string   | `"mmb"`               | Single key or mouse button                 |
| `hotkey`  | array    | `["ctrl", "a"]`       | Any combination of keys and/or mouse buttons |
| `window`  | string   | `"chrome"`            | Restrict macro to specific app window      |

#### Hotkey Mechanics

- You can use **any number of keys/buttons** in a `hotkey`.
- The last key in the list is the one you **must release last** to trigger the macro.
- Example: `["ctrl", "shift", "x1", "g"]`
  - Hold keys in order: `ctrl` → `shift` → `x1` → `g`
  - Release in any order, but **`g` must be released last**

This allows powerful combos like:
```json
"hotkey": ["x1", "z", "enter"]
```
or
```json
"hotkey": ["scroll_down", "f", "shift"]
```

---

### `settings`

| Field     | Type     | Example     | Description                                     |
|-----------|----------|-------------|-------------------------------------------------|
| `mode`    | string   | `"press"`   | Execution mode: `press`, `release`, `hold`, `loop` |
| `repeat`  | number   | `1`, `5`     | Number of repetitions (ignored in loop mode)    |

---

### `actions` (macro body)

Each action is an object with a `type` and its parameters:

```json
{ "action": "press", "key": "z" }
```

Supported types:

| Action     | Example                                                             |
|------------|---------------------------------------------------------------------|
| `press`    | `{"action": "press", "key": "z"}`                                   |
| `release`  | `{"action": "release", "key": "z"}`                                 |
| `delay`    | `{"action": "delay", "ms": 15}`                                     |
| `move`     | `{"action": "move", "x": 800, "y": 400, "duration": 0}`            |
| `click`    | `{"action": "click", "button": "lmb"}`                              |
| `mousedown`| `{"action": "mousedown", "button": "rmb"}`                          |
| `mouseup`  | `{"action": "mouseup", "button": "rmb"}`                            |
| `scroll`   | `{"action": "scroll", "clicks": 300}` or `-300`                     |
| `type`     | `{"action": "type", "text": "Hello"}`                               |
| `hotkey`   | `{"action": "hotkey", "keys": ["ctrl", "c"]}`                       |

---

### Loop Mode Behavior

If `mode` is `"loop"`:
- The macro repeats infinitely
- Pressing the bind again stops it
- `repeat` is ignored
- 15 ms delay is inserted between iterations

---

## Key and Mouse Input Reference

### Keyboard

All key names must match **PyAutoGUI’s** syntax. See [official docs](https://pyautogui.readthedocs.io/en/latest/keyboard.html) or use this example subset:

<details>
<summary>Click to expand full supported key list</summary>

```json
[
'!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
'{', '|', '}', '~',
'\t', '\n', '\r', ' ',
'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
'browserback', 'browserfavorites', 'browserforward', 'browserhome',
'browserrefresh', 'browsersearch', 'browserstop',
'capslock', 'clear', 'command', 'convert', 'ctrl', 'ctrlleft', 'ctrlright',
'decimal', 'del', 'delete', 'divide', 'down',
'end', 'enter', 'esc', 'escape', 'execute',
'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19',
'f20', 'f21', 'f22', 'f23', 'f24',
'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home',
'insert', 'junja', 'kana', 'kanji',
'launchapp1', 'launchapp2', 'launchmail', 'launchmediaselect',
'left', 'modechange', 'multiply', 'nexttrack',
'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5',
'num6', 'num7', 'num8', 'num9', 'numlock',
'option', 'optionleft', 'optionright',
'pagedown', 'pageup', 'pause', 'pgdn', 'pgup',
'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
'prtsc', 'prtscr', 'return', 'right',
'scrolllock', 'select', 'separator', 'shift', 'shiftleft', 'shiftright',
'sleep', 'space', 'stop', 'subtract', 'tab',
'up', 'volumedown', 'volumemute', 'volumeup',
'win', 'winleft', 'winright', 'yen'
]
```
</details>

### Mouse Buttons and Scrolls

| Name         | Description                     |
|--------------|---------------------------------|
| `lmb`        | Left mouse button               |
| `rmb`        | Right mouse button              |
| `mmb`        | Middle mouse button             |
| `x1`         | Extra mouse button 1            |
| `x2`         | Extra mouse button 2            |
| `scroll_up`  | Scroll wheel up (virtual button)|
| `scroll_down`| Scroll wheel down               |

---

## Limitations

### No Side-Specific Modifier Binds

Due to internal VK-code mapping, the following keys are merged:

| Merged Inputs             | Treated As |
|---------------------------|------------|
| `ctrlleft`, `ctrlright`   | `ctrl`     |
| `altleft`, `altright`     | `alt`      |
| `shiftleft`, `shiftright` | `shift`    |

This means you **cannot** bind macros separately to left/right versions.

---

## Project Structure

```
vk_map.json            - Internal VK mappings
main.py                - Macro player
recorder.py            - Macro recorder
logic.py               - Core macro logic
hook_listener.py       - Low-level input hook manager
README.md              - This documentation
```

---

## Example Macro

```json
{
  "bind": {
    "hotkey": ["ctrl", "f"],
    "window": "notepad"
  },
  "settings": {
    "mode": "press",
    "repeat": 3
  },
  "actions": [
    {"action": "type", "text": "Hello"},
    {"action": "delay", "ms": 100},
    {"action": "press", "key": "enter"}
  ]
}
```

---

## TODO

- [ ] Suppression of native input (WIP)
- [ ] GUI macro editor
- [ ] Conditional logic support
- [ ] Profile support for grouped macros

---

## License

MIT
