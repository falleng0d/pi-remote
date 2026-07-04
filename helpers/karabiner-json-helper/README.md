# Karabiner JSON Helper

`KarabinerBackend` starts `karabiner_helper_command` and writes one JSON object per line to the helper's stdin.

The included `karabiner_json_helper.py` is a self-contained Python helper that speaks Karabiner-DriverKit-VirtualHIDDevice's daemon protocol over the root-only Unix domain socket:

```shell
sudo python3 helpers/karabiner-json-helper/karabiner_json_helper.py
```

It must run as root because the socket lives under `/Library/Application Support/org.pqrs/tmp/rootonly` with owner-only permissions.

This helper intentionally avoids reimplementing Karabiner's DriverKit driver. It connects to the `Karabiner-VirtualHIDDevice-Daemon` installed and managed by Karabiner-Elements, initializes the virtual keyboard and pointing device, and posts HID reports. Do not run a second daemon; Karabiner uses fixed bundle IDs and socket paths.

## Configuration

Example `remotecontrol.cfg` entry:

```python
output_backend = 'karabiner'
host = '127.0.0.1'
karabiner_helper_command = 'python3 helpers/karabiner-json-helper/karabiner_json_helper.py'
karabiner_allow_remote = False
```

Run pi-remote as root, or use a root-owned wrapper. Putting interactive `sudo` in `karabiner_helper_command` is brittle because the helper's stdin is used for JSON input.

Optional helper flags:

```shell
sudo python3 helpers/karabiner-json-helper/karabiner_json_helper.py \
  --socket-path '/Library/Application Support/org.pqrs/tmp/rootonly/karabiner_virtual_hid_device_service.sock' \
  --keyboard-country-code 33
```

Use `--dry-run` to validate JSON-lines input without touching Karabiner.

## JSON-Lines Protocol

Keyboard or consumer key event:

```json
{"type":"key","page":7,"code":4,"value":1,"device_hash":0}
```

Mouse event:

```json
{"type":"mouse","buttons":1,"x":10,"y":-5,"vertical_wheel":0,"horizontal_wheel":0,"device_hash":0}
```

Pages used by pi-remote:

- `7`: keyboard/keypad page
- `12`: consumer page

For keyboard page modifier usages `0xE0` through `0xE7`, the helper updates the modifier bitmask and posts a full keyboard report. For normal keyboard and consumer usages, it maintains the pressed-key set and posts a full report after every state change. Mouse messages post a pointing report immediately.

## Notes

This is an experimental direct daemon-protocol helper based on Karabiner's open-source `pqrs::unix_domain_stream` framing and VirtualHIDDevice service structs. A C++ or Rust helper linked against Karabiner's official header-only client remains the least brittle long-term integration path, but this helper keeps pi-remote usable without vendoring Karabiner sources.
