# qmk-userspace

My [QMK External Userspace](https://docs.qmk.fm/newbs_external_userspace):
keymaps and shared user code live here, QMK Firmware itself stays a vanilla
clone.

```
qmk.json                                   build targets for `qmk userspace-compile`
users/nedsi/                               shared code: layers, row macros, custom keycodes, tap dances
keyboards/bastardkb/scylla/keymaps/nedsi/  Scylla keymap (submodule: ned-si/scylla)
```

## Setup

1. Install the QMK CLI and toolchains. The official route is
   `curl -fsSL https://install.qmk.fm | sh`. Equivalent manual steps:
   `uv tool install --with pip qmk`, then extract the latest
   [qmk_toolchains](https://github.com/qmk/qmk_toolchains/releases) and
   [qmk_flashutils](https://github.com/qmk/qmk_flashutils/releases) releases
   into `~/Library/Application Support/qmk` (flashutils under `bin/`).
2. Clone QMK Firmware and point the CLI at it:

   ```sh
   git clone --recurse-submodules https://github.com/qmk/qmk_firmware.git ~/repos/qmk_firmware
   qmk config user.qmk_home="$HOME/repos/qmk_firmware"
   ```

3. Clone this repository with its submodules and register it as the overlay:

   ```sh
   git clone --recurse-submodules git@github.com:ned-si/qmk-userspace.git ~/repos/qmk-userspace
   qmk config user.overlay_dir="$HOME/repos/qmk-userspace"
   ```

4. `qmk doctor` should end with "QMK is ready to go".

## Build

```sh
qmk userspace-compile        # every target in qmk.json; firmware lands in this directory
qmk compile -kb bastardkb/scylla/promicro -km nedsi
```

## Flash (Scylla)

```sh
qmk flash -kb bastardkb/scylla/promicro -km nedsi
```

Then put one half in bootloader mode; it mounts as `RPI-RP2` and the CLI copies
the `.uf2` onto it. Repeat for the other half: both take the same firmware.
Ways into the bootloader: double-tap the reset button, `QK_BOOT` (top-left key
on the NAV layer), or hold the top-left key while plugging the half in.

## Updating

```sh
git -C ~/repos/qmk_firmware pull --recurse-submodules
git -C ~/repos/qmk-userspace pull --recurse-submodules
```
