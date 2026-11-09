# qmk-userspace

My [QMK External Userspace](https://docs.qmk.fm/newbs_external_userspace):
keymaps and shared user code live here, QMK Firmware itself stays a vanilla
clone.

```
qmk.json      build targets for `qmk userspace-compile`
keymaps.txt   which keymap repository is cloned into which keymap folder
users/nedsi/  shared code: layers, row macros, custom keycodes, tap dances
keyboards/    keymap clones, one repository per keyboard (git-ignored)
```

Each keyboard keymap is its own repository, cloned into its QMK keymap folder.
This repository ignores those folders (`keyboards/**/keymaps/nedsi/`), so it
never pins a keymap commit: a build uses whatever each clone has checked out.

## Keyboards

| Keyboard | QMK target | Repository |
|---|---|---|
| Scylla (Splinky v3) | `bastardkb/scylla/promicro` | [scylla](https://github.com/ned-si/scylla) |
| Skeletyl (handwired) | `bastardkb/skeletyl/promicro` | [skeletyl-qmk](https://github.com/ned-si/skeletyl-qmk) |
| Microdox v1 | `boardsource/microdox/v1` | [microdox-qmk](https://github.com/ned-si/microdox-qmk) |
| Tractyloder (Dactyl 4x5, trackball) | `handwired/dactyl_manuform/4x5` | [tractyloder](https://github.com/ned-si/tractyloder) |
| Atreus 44 (handwired) | `handwired/pteron44` | [atreus44](https://github.com/ned-si/atreus44) |
| BDN9 | `keebio/bdn9/rev1` | [bdn9](https://github.com/ned-si/bdn9) |
| Keyboardio Atreus | `keyboardio/atreus` | [keyboardio-atreus](https://github.com/ned-si/keyboardio-atreus) |
| Planck | `planck/rev6` | [planck](https://github.com/ned-si/planck) |
| Kyria rev1 | `splitkb/kyria/rev1/base` | [kyria](https://github.com/ned-si/kyria) |
| Zima | `splitkb/zima` | [zima](https://github.com/ned-si/zima) |

Handwired boards build on the closest upstream keyboard, with their pins and
matrix layout carried in the keymap; each keymap README says what differs.
BDN9, Planck, Tractyloder and Zima keymaps are standalone and do not use
`users/nedsi`.

To add a keyboard: clone its repository into
`keyboards/<keyboard>/keymaps/nedsi`, then add it to `keymaps.txt` and its
target to `qmk.json`.

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

3. Clone this repository, register it as the overlay, then clone every keymap
   listed in `keymaps.txt`:

   ```sh
   git clone git@github.com:ned-si/qmk-userspace.git ~/repos/qmk-userspace
   qmk config user.overlay_dir="$HOME/repos/qmk-userspace"
   cd ~/repos/qmk-userspace
   grep -v '^#' keymaps.txt | while read -r dir repo; do git clone "git@github.com:$repo.git" "$dir"; done
   ```

4. `qmk doctor` should end with "QMK is ready to go".

## Build

```sh
qmk userspace-compile                               # every target in qmk.json; firmware lands here
qmk compile -kb bastardkb/scylla/promicro -km nedsi # one keyboard
```

## Flash

```sh
qmk flash -kb <target> -km nedsi
```

Then put the keyboard (or one half) in bootloader mode; the CLI waits for it
and flashes. Split keyboards take the same firmware on both halves, flashed one
at a time. Each keymap README says how to enter its bootloader.

## Updating

```sh
git -C ~/repos/qmk_firmware pull --recurse-submodules
cd ~/repos/qmk-userspace && git pull
grep -v '^#' keymaps.txt | while read -r dir repo; do git -C "$dir" pull; done
```

Keymap changes are committed and pushed from inside the keymap clone, to its own
repository. Shared code in `users/nedsi` is committed here.
