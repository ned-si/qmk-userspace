#!/usr/bin/env python3
"""Draw a keymap's layers as text diagrams in its README.

    python3 util/layers.py keyboards/<keyboard>/keymaps/nedsi           # update README.md
    python3 util/layers.py keyboards/<keyboard>/keymaps/nedsi --print   # only print
    python3 util/layers.py users/nedsi       # shared layers, in this repository's README.md

Run from the root of this userspace, with the QMK CLI set up. The diagrams go
between the `<!-- layers:start -->` and `<!-- layers:end -->` markers in the
keymap's README.md (a "Layers" section is added if they are missing).

How it works:
- The keymap is run through the C preprocessor with QMK's headers replaced by
  empty stubs, so only this userspace's macros (row macros, HOME_A, ...) expand
  and QMK keycodes stay readable (KC_A, MO(_SYM), LGUI_T(KC_A)).
- Key positions come from QMK's layout data (`qmk info`), or, for a layout
  macro defined in the keymap itself, from how its parameters are laid out in
  the source.
- Tap dance notes are read from the keymap's own `<NAME>_finished` functions.
"""
import argparse
import json
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

W = 7  # cell width
ROOT = pathlib.Path.cwd()
MARK_START, MARK_END = "<!-- layers:start -->", "<!-- layers:end -->"

# Layers are drawn in this order; unknown ones keep their keymap order, Gaming last.
ORDER = ["MAIN", "BASE", "NUM", "NUMBERS", "NUMPAD", "SYM", "SYMBOLS", "ACC", "ACCENTS",
         "NAV", "MISC", "OPTIONS"]
LAST = ["GAMING"]

# Keyboards whose QMK layout data does not draw well as a grid.
POSITIONS = {
    # Kyria rev1: three 6-key rows, the two inner bottom-row keys on a row of
    # their own, then the 5-key thumb arc (tucked under each half when drawn).
    "splitkb/kyria/rev1/base": (
        [[x, y] for y in (0, 1) for x in [*range(0, 6), *range(9, 15)]]
        + [[x, 2] for x in range(0, 6)] + [[4, 3], [5, 3], [9, 3], [10, 3]] + [[x, 2] for x in range(9, 15)]
        + [[x, 4] for x in [*range(1, 6), *range(9, 14)]]
    ),
}


# --- extraction ---------------------------------------------------------------
def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def target_for(keymap_dir):
    kb = str(keymap_dir.relative_to(ROOT / "keyboards")).removesuffix("/keymaps/nedsi")
    for t, _ in json.load(open(ROOT / "qmk.json"))["build_targets"]:
        if t == kb or t.startswith(kb + "/"):
            return t
    sys.exit(f"no target in qmk.json for {kb}")


def uses_userspace(keymap_dir):
    rules = keymap_dir / "rules.mk"
    return not (rules.exists() and re.search(r"USER_NAME\s*:?=\s*nedsi_none", rules.read_text()))


def source_files(keymap_dir, userspace):
    files = [f for f in keymap_dir.iterdir() if f.suffix in (".c", ".h")]
    if userspace:
        files += [f for f in (ROOT / "users/nedsi").iterdir() if f.suffix in (".c", ".h")]
    return files


LAYOUT_DEFINE = re.compile(r"#\s*define\s+(LAYOUT\w*)\s*\(((?:\\\n|[^\n])*)")


def extract_layers(keymap_dir, userspace):
    work = pathlib.Path(tempfile.mkdtemp())
    try:
        src, stubs = work / "src", work / "stubs"
        src.mkdir(); stubs.mkdir()
        local_layouts = {}
        for f in source_files(keymap_dir, userspace):
            text = f.read_text()
            def disable(m):
                if "{" in m.group(0):  # builds the matrix: keep the call unexpanded
                    if f.parent == keymap_dir:
                        local_layouts[m.group(1)] = f
                    return m.group(0).replace(m.group(1) + "(", m.group(1) + "_DISABLED(", 1)
                return m.group(0)
            (src / f.name).write_text(LAYOUT_DEFINE.sub(disable, text))
        (stubs / "qmk_keyboard.h").write_text("")
        defines = ["TAP_DANCE_ENABLE", "UNICODEMAP_ENABLE", "UNICODE_ENABLE", "COMBO_ENABLE",
                   "ENCODER_ENABLE", "OLED_ENABLE", "RGBLIGHT_ENABLE", "RGB_MATRIX_ENABLE",
                   "MOUSEKEY_ENABLE", "POINTING_DEVICE_ENABLE", "EXTRAKEY_ENABLE"]
        cc = os.environ.get("LAYERS_CC") or next((c for c in ("clang", "gcc", "cc", "avr-gcc", "arm-none-eabi-gcc") if shutil.which(c)), None)
        if not cc:
            sys.exit("needs a C preprocessor: clang, gcc or a QMK toolchain compiler")
        cmd = [cc, "-E", "-P", "-x", "c", "-w", "-I", str(src), "-I", str(stubs),
               '-DQMK_KEYBOARD_H="qmk_keyboard.h"'] + [f"-D{d}" for d in defines] + [str(src / "keymap.c")]
        for _ in range(100):
            r = run(cmd)
            if r.returncode == 0:
                break
            missing = re.findall(r"fatal error: '([^']+)' file not found", r.stderr)  # clang
            missing += re.findall(r"fatal error: ([^:\s]+): No such file or directory", r.stderr)  # gcc
            if not missing:
                sys.exit(r.stderr)
            for n in missing:
                (stubs / n).parent.mkdir(parents=True, exist_ok=True)
                (stubs / n).write_text("")
        out = r.stdout
    finally:
        shutil.rmtree(work)

    body = out[out.index("{", out.index("keymaps[")) + 1:]
    layers, i = [], 0
    entry = re.compile(r"\s*\[\s*(\w+)\s*\]\s*=\s*(\w+)\s*\(")
    while (m := entry.match(body, i)):
        j, depth, args, cur = m.end(), 1, [], ""
        while True:
            c = body[j]
            depth += (c == "(") - (c == ")")
            if depth == 0:
                break
            if c == "," and depth == 1:
                args.append(cur); cur = ""
            else:
                cur += c
            j += 1
        args.append(cur)
        layers.append({"name": m.group(1), "layout": m.group(2), "keys": [" ".join(a.split()) for a in args]})
        i = j + 1
        while i < len(body) and body[i] in " \n\t,":
            i += 1
    return layers, local_layouts


def positions_from_macro(path, name):
    text = path.read_text().expandtabs(8)
    m = re.search(r"#\s*define\s+" + re.escape(name) + r"\s*\(", text)
    params = text[m.end(): text.index(")", m.end())]
    pts = []
    for y, line in enumerate(params.split("\n")):
        for t in re.finditer(r"[A-Za-z_]\w*", line):
            pts.append([t.start(), y])
    xs = sorted({p[0] for p in pts})
    gaps = [b - a for a, b in zip(xs, xs[1:])]
    pitch = max(set(gaps), key=gaps.count) if gaps else 1
    base = min(xs)
    ys = sorted({p[1] for p in pts})
    return [[(x - base) / pitch, ys.index(y)] for x, y in pts]


def positions_from_qmk(target, layout):
    r = run(["qmk", "info", "-kb", target, "-f", "json"], cwd=ROOT)
    info = json.loads(r.stdout)
    layouts = info["layouts"]
    name = info.get("layout_aliases", {}).get(layout, layout)
    if name not in layouts:
        sys.exit(f"{target} has no layout {layout} (has {', '.join(layouts)})")
    return [[k["x"], k["y"]] for k in layouts[name]["layout"]]


# --- labels -----------------------------------------------------------------
BASIC = {
    "SPC": "Space", "SPACE": "Space", "ENT": "Enter", "ENTER": "Enter", "BSPC": "Bksp", "DEL": "Del",
    "TAB": "Tab", "ESC": "Esc", "CAPS": "Caps", "LSFT": "Shift", "RSFT": "Shift", "LCTL": "Ctrl",
    "RCTL": "Ctrl", "LALT": "Alt", "RALT": "AltGr", "LGUI": "Gui", "RGUI": "Gui",
    "HOME": "Home", "END": "End", "PGUP": "PgUp", "PGDN": "PgDn", "INS": "Ins",
    "LEFT": "Left", "RGHT": "Right", "RIGHT": "Right", "UP": "Up", "DOWN": "Down",
    "MINS": "-", "EQL": "=", "LBRC": "[", "RBRC": "]", "BSLS": "\\", "SCLN": ";", "QUOT": "'",
    "GRV": "`", "COMM": ",", "COMMA": ",", "DOT": ".", "SLSH": "/", "TILD": "~", "EXLM": "!",
    "AT": "@", "HASH": "#", "DLR": "$", "PERC": "%", "CIRC": "^", "AMPR": "&", "ASTR": "*",
    "LPRN": "(", "RPRN": ")", "UNDS": "_", "PLUS": "+", "LCBR": "{", "RCBR": "}", "PIPE": "|",
    "COLN": ":", "DQUO": '"', "DQT": '"', "LT": "<", "GT": ">", "QUES": "?",
    "PPLS": "+", "PMNS": "-", "PAST": "*", "PSLS": "/", "PDOT": ".", "PENT": "Enter",
    "VOLU": "Vol+", "VOLD": "Vol-", "MUTE": "Mute", "MPLY": "Play", "MNXT": "Next", "MPRV": "Prev",
    "MSTP": "Stop", "BRIU": "Bri+", "BRID": "Bri-", "PSCR": "PrtSc", "APP": "Menu",
    "BTN1": "Click", "BTN2": "RClick", "BTN3": "MClick", "MS_BTN1": "Click", "MS_BTN2": "RClick",
    "MS_BTN3": "MClick", "WH_U": "Whl Up", "WH_D": "Whl Dn", "MS_WHLU": "Whl Up", "MS_WHLD": "Whl Dn",
    "MS_U": "Ms Up", "MS_D": "Ms Dn", "MS_L": "Ms Lt", "MS_R": "Ms Rt",
    # users/nedsi custom keycodes and keymap-local ones
    "EURO": "€", "DEGR": "°", "PMED": "·", "SHRG": "Shrug", "SIGN": "Sign",
    "EAIG": "é", "EGRV": "è", "ECIR": "ê", "EUML": "ë", "AGRV": "à", "ACIR": "â", "AUML": "ä",
    "ICIR": "î", "IUML": "ï", "OCIR": "ô", "OUML": "ö", "UGRV": "ù", "UCIR": "û", "UUML": "ü",
    "CCED": "ç", "ULCLK": "U/Clk", "IRCLK": "I/RClk", "JLCLK": "J/Clk", "KRCLK": "K/RClk",
    "SCROLL": "Scroll",
}
KEYS = {
    "DED__CIR": "^ dead", "DED__UML": "¨ dead", "UM(DED__CIR)": "^ dead", "UM(DED__UML)": "¨ dead",
    "UM(DEGREE)": "°", "QK_BOOT": "Boot", "RESET": "Boot", "CW_TOGG": "CapsWrd",
    "TD(CA_CC_CV)": "Copy*", "TD(NXT_PRV)": "Next*", "TD(UNI_W_L)": "Unicode",
    "LCTL(KC_Z)": "Undo", "LCTL(KC_Y)": "Redo",
}
MODS = {"LCTL": "Ctl", "RCTL": "Ctl", "C": "Ctl", "LSFT": "Sft", "RSFT": "Sft", "S": "Sft",
        "LALT": "Alt", "RALT": "AGr", "A": "Alt", "LGUI": "Gui", "RGUI": "Gui", "G": "Gui",
        "MEH": "Meh", "HYPR": "Hyp"}
SHIFTED = {"KC_1": "!", "KC_2": "@", "KC_3": "#", "KC_4": "$", "KC_5": "%", "KC_6": "^", "KC_7": "&",
           "KC_8": "*", "KC_9": "(", "KC_0": ")", "KC_MINS": "_", "KC_EQL": "+", "KC_SLSH": "?",
           "KC_SCLN": ":", "KC_QUOT": '"', "KC_GRV": "~", "KC_COMM": "<", "KC_DOT": ">"}
RGB = {"TOGG": "RGB tog", "NEXT": "RGB+", "PREV": "RGB-", "HUEU": "Hue+", "HUED": "Hue-",
       "SATU": "Sat+", "SATD": "Sat-", "VALU": "Bri+", "VALD": "Bri-", "SPDU": "Spd+", "SPDD": "Spd-"}
SHORT = {"Space": "Spc", "Enter": "Ent", "Shift": "Sft", "Right": "Rgt"}
DIACRITIC = {"ACUT": "́", "GRAV": "̀", "CIRC": "̂", "CDIL": "̧", "UMLT": "̈",
             "DIAE": "̈", "TILD": "̃"}


def layer_title(t):
    t = t.lstrip("_")
    return f"Layer {t}" if t.isdigit() else t.capitalize()


def layer_key(t):
    return t.lstrip("_").upper()


def label(t, used):
    """Label for one keycode; `used` collects what the notes need to explain."""
    t = " ".join(t.split())
    if t in ("_______", "KC_TRNS", "KC_TRANSPARENT", "XXXXXXX", "KC_NO", "___", "KC_"):
        return ""
    if t in KEYS:
        used.add(t)
        return KEYS[t]
    if (m := re.fullmatch(r"KC_(\w+)", t)):
        k = m.group(1)
        if re.fullmatch(r"[A-Z0-9]|F\d+", k):
            return k
        if k in BASIC:
            used.add(t)
            return BASIC[k]
    if (m := re.fullmatch(r"(?:MO|TT|OSL)\((\w+)\)", t)):
        return layer_key(m.group(1))
    if (m := re.fullmatch(r"(?:TG|TO|DF)\((\w+)\)", t)):
        used.add(("toggle", m.group(1)))
        return layer_title(m.group(1))
    if (m := re.fullmatch(r"LT\((\w+),\s*(.+)\)", t)):
        used.add("dual")
        return label(m.group(2), used) + "/" + layer_title(m.group(1))[:3]
    if (m := re.fullmatch(r"(\w+?)_T\((.+)\)", t)) and m.group(1) in MODS:
        used.add("dual")
        return label(m.group(2), used) + "/" + MODS[m.group(1)]
    if (m := re.fullmatch(r"(?:LSFT|S)\((KC_\w+)\)", t)) and m.group(1) in SHIFTED:
        return SHIFTED[m.group(1)]
    if (m := re.fullmatch(r"UP\((\w)__(\w+?),.*\)", t)) and m.group(2) in DIACRITIC:
        return unicodedata.normalize("NFC", m.group(1) + DIACRITIC[m.group(2)])
    if (m := re.fullmatch(r"(?:RM|UG|RGB)_(\w+)", t)) and m.group(1) in RGB:
        return RGB[m.group(1)]
    # Modifier combinations: C(KC_Z) -> Ctl+Z, C(S(KC_C)) -> CtlSftC
    mods, inner = [], t
    while (m := re.fullmatch(r"(LCTL|LSFT|LALT|LGUI|RALT|C|S|A|G|MEH|HYPR)\((.+)\)", inner)):
        mods.append(MODS[m.group(1)]); inner = m.group(2)
    if mods:
        if "Meh" in mods:
            used.add("meh")
        key = label(inner, used)
        key = SHORT.get(key, key)
        return (mods[0] + "+" + key) if len(mods) == 1 else "".join(mods) + key
    used.add(("unknown", t))
    return t.removeprefix("KC_")[:W]


# --- tap dance notes, from the keymap's own functions ------------------------
def describe_call(stmt, used):
    if (m := re.search(r"tap_code16?\((.+?)\);", stmt)):
        return label(m.group(1), set()).replace("Ctl+", "Ctrl+") or m.group(1)
    if (m := re.search(r"set_unicode_input_mode\(UNICODE_MODE_(\w+)\)", stmt)):
        return {"LINUX": "Linux", "WINCOMPOSE": "WinCompose", "MACOS": "macOS", "WINDOWS": "Windows",
                "BSD": "BSD"}.get(m.group(1), m.group(1)) + " input"
    return None


def tap_dance_notes(files):
    text = "\n".join(f.read_text() for f in files if f.suffix == ".c")
    notes = {}
    for m in re.finditer(r"void\s+(\w+)_finished\s*\([^)]*\)\s*\{", text):
        name, depth, j = m.group(1), 1, m.end()
        while depth:
            depth += (text[j] == "{") - (text[j] == "}"); j += 1
        body = text[m.end(): j]
        parts = []
        for case in re.finditer(r"case\s+(SINGLE_TAP|SINGLE_HOLD|DOUBLE_SINGLE_TAP|DOUBLE_TAP)\s*:(.*?)(?=case\s|default\s*:|\}\s*$)", body, re.S):
            what = describe_call(case.group(2), set())
            if what:
                verb = {"SINGLE_TAP": "tap", "SINGLE_HOLD": "hold", "DOUBLE_SINGLE_TAP": "double-tap",
                        "DOUBLE_TAP": "double-tap"}[case.group(1)]
                parts.append(f"{verb} {what}")
        if parts:
            notes[f"TD({name})"] = ", ".join(parts)
    return notes


# --- combos --------------------------------------------------------------------
def object_macros(files):
    """Simple object-like #defines (NAME value) from the keymap sources."""
    out = {}
    for f in files:
        for m in re.finditer(r"^\s*#\s*define\s+(\w+)[ \t]+([^\n]+?)\s*(?://.*)?$", f.read_text(), re.M):
            out.setdefault(m.group(1), m.group(2))
    return out


def resolve(token, macros):
    for _ in range(10):
        if token not in macros:
            break
        token = macros[token]
    return token


def combos(keymap_dir, macros):
    rules = (keymap_dir / "rules.mk").read_text() if (keymap_dir / "rules.mk").exists() else ""
    f = keymap_dir / "combos.c"
    if not f.exists() or not re.search(r"COMBO_ENABLE\s*=\s*yes", rules):
        return []
    text = f.read_text()
    def key(k):
        lab = label(resolve(k, macros), set()) or k
        return lab.split("/")[0] if "/" in lab and len(lab) > 1 else lab  # tap key of a mod-tap
    arrays = {m.group(1): [key(k) for k in re.split(r"\s*,\s*", m.group(2).strip()) if k and k != "COMBO_END"]
              for m in re.finditer(r"(\w+)\[\]\s*=\s*\{([^}]*)\}", text)}
    out = []
    for m in re.finditer(r"\[(\w+)\]\s*=\s*COMBO_ACTION\((\w+)\)", text):
        name, arr = m.groups()
        case = re.search(r"case\s+" + name + r"\s*:(.*?)break;", text, re.S)
        does = None
        if case:
            sent = re.findall(r'(?:SEND_STRING|send_string)\("((?:[^"\\]|\\.)*)"', case.group(1))
            if sent:
                does = f"`{sent[-1]}`"
                variants = re.findall(r'MOD_MASK_(SHIFT|CTRL)\)\s*\{.*?send_string\("((?:[^"\\]|\\.)*)"', case.group(1), re.S)
                if variants:
                    does += " (" + ", ".join(f"{'Shift' if m == 'SHIFT' else 'Ctrl'}: `{v}`" for m, v in variants) + ")"
            elif (s := re.search(r"tap_code16?\((\w+(?:\([^)]*\))?)\)", case.group(1))):
                does = label(s.group(1), set())
                does = f"`{does}`" if len(does) == 1 else does
            elif "caps_word" in case.group(1):
                does = "Caps Word"
        out.append((arrays.get(arr, [arr]), does or name))
    return out


# --- drawing -------------------------------------------------------------------
def rnd(v):
    return math.floor(v + 0.5)


def tuck(cells, nrows):
    """On split boards, move rows that reach past a half's columns (thumb rows)
    back under that half, so the halves stay close together."""
    row0 = sorted(c for r, c in cells if r == 0)
    gaps = [(b - a, a, b) for a, b in zip(row0, row0[1:])]
    if not gaps or max(gaps)[0] < 2:
        return cells
    _, inner_l, inner_r = max(gaps)
    split, outer_l, outer_r = (inner_l + inner_r) / 2, row0[0], row0[-1]
    out = {}
    for r in range(nrows):
        row = {c: i for (rr, c), i in cells.items() if rr == r}
        left = [c for c in row if c < split]
        right = [c for c in row if c > split]
        dl = dr = 0
        if left and outer_l not in left:  # not a main row: tuck it in
            dl = min(max(0, max(left) - inner_l), min(left) - outer_l)
        if right and outer_r not in right:
            dr = min(max(0, inner_r - min(right)), outer_r - max(right))
        for c, i in row.items():
            out[(r, c - dl if c < split else c + dr)] = i
    return out


def grid(positions):
    pts = [list(p) for p in positions]
    gmin = min(p[1] for p in pts)
    tops = {}
    for x, y in pts:  # undo column stagger, so each column's top key sits on the top row
        if y - gmin < 1.0:
            tops[rnd(x)] = min(tops.get(rnd(x), y), y)
    for p in pts:
        p[1] -= tops.get(rnd(p[0]), gmin) - gmin
    ys = sorted({round(p[1] * 2) / 2 for p in pts})
    rows, cur = [], [ys[0]]
    for y in ys[1:]:
        if y - cur[0] < 0.75:
            cur.append(y)
        else:
            rows.append(cur); cur = [y]
    rows.append(cur)
    cells = {}
    for i, (x, y) in enumerate(pts):
        r = next(n for n, row in enumerate(rows) if round(y * 2) / 2 in row)
        c = rnd(x)
        while (r, c) in cells:
            c += 1
        cells[(r, c)] = i
    cells = tuck(cells, len(rows))
    used = sorted({c for _, c in cells})
    colmap, kinds = {}, []
    for c in range(used[0], used[-1] + 1):
        if c in used:
            colmap[c] = len(kinds); kinds.append("k")
        elif kinds[-1] != "g":
            kinds.append("g")
    return {(r, colmap[c]): i for (r, c), i in cells.items()}, kinds, len(rows)


def draw(labels, layout):
    cells, kinds, nrows = layout
    xs, x = [], 0
    for k in kinds:
        xs.append(x); x += (W + 1) if k == "k" else 3
    width = x + 1
    lines = []
    for r in range(nrows + 1):
        sep = [" "] * width
        for k, kind in enumerate(kinds):
            if kind == "k" and ((r - 1, k) in cells or (r, k) in cells):
                x0 = xs[k]
                for j in range(x0 + 1, x0 + W + 1):
                    if sep[j] != "+":
                        sep[j] = "-"
                sep[x0] = sep[x0 + W + 1] = "+"
        lines.append("".join(sep).rstrip())
        if r == nrows:
            break
        row = [" "] * width
        for k in range(len(kinds)):
            if (r, k) in cells:
                x0 = xs[k]
                lab = labels[cells[(r, k)]][:W].center(W)
                row[x0] = row[x0 + W + 1] = "|"
                row[x0 + 1: x0 + 1 + W] = list(lab)
        lines.append("".join(row).rstrip())
    return "\n".join(lines)


def ordered(layers):
    names = [layer_key(l["name"]) for l in layers]
    first = [names[0]] + [n for n in ORDER if n in names and n != names[0]]
    last = [n for n in LAST if n in names]
    middle = [n for n in names if n not in first and n not in last]
    by = {layer_key(l["name"]): l for l in layers}
    return [by[n] for n in first + middle + last]


def activators(layers, target):
    """(layer index, key index, how) for keys that switch to `target`."""
    out = []
    for li, l in enumerate(layers):
        for ki, k in enumerate(l["keys"]):
            if re.fullmatch(rf"(?:MO|TT|OSL)\({target}\)", k):
                out.append((li, ki, "hold"))
            elif re.fullmatch(rf"LT\({target},.*\)", k):
                out.append((li, ki, "hold"))
            elif re.fullmatch(rf"(?:TG|TO|DF)\({target}\)", k):
                out.append((li, ki, "toggle"))
    return out


def notes_for(used_all, td, userspace):
    """Explanations for the special keys a set of layers uses."""
    notes = []
    if "dual" in used_all:
        notes.append("`X/Mod` and `X/Lay` keys type X when tapped, and act as the modifier or layer while held.")
    for t, text in sorted(td.items()):
        if t in used_all:
            notes.append(f"`{KEYS.get(t, t)}`: {text}.")
    if userspace:
        if "KC_COLN" in used_all:
            notes.append("`:` sends `;` when shifted.")
        if "KC_BSPC" in used_all:
            notes.append("`Bksp` sends Delete when shifted.")
        if "KC_AMPR" in used_all:
            notes.append("`&` sends `|` when shifted.")
    if "CW_TOGG" in used_all:
        notes.append("`CapsWrd` is Caps Word: capitalises until the next non-word key.")
    if "KC_SHRG" in used_all:
        notes.append("`Shrug` types `¯\\_(ツ)_/¯`.")
    if used_all & {"DED__CIR", "DED__UML", "UM(DED__CIR)", "UM(DED__UML)"}:
        notes.append("The dead keys add a circumflex or diaeresis to the next letter.")
    if used_all & {"QK_BOOT", "RESET"}:
        notes.append("`Boot` reboots into the bootloader, for flashing.")
    for item in sorted(x for x in used_all if isinstance(x, tuple) and x[0] == "toggle"):
        notes.append(f"`{layer_title(item[1])}` toggles the {layer_title(item[1])} layer on and off.")
    if "TD(UNI_W_L)" in used_all and "TD(UNI_W_L)" not in td:
        notes.append("`Unicode` switches the Unicode input mode.")
    if used_all & {"LCTL(KC_Z)", "LCTL(KC_Y)"}:
        notes.append("`Undo` and `Redo` are Ctrl+Z and Ctrl+Y.")
    if "meh" in used_all:
        notes.append("`Meh` is Ctrl+Shift+Alt.")
    if used_all & {"KC_ULCLK", "KC_IRCLK", "KC_JLCLK", "KC_KRCLK"}:
        notes.append("`U/Clk`, `I/RClk` type the letter, or click (right-click) right after the trackball moved. `Scroll` switches the trackball between cursor and scrolling.")
    unknown = sorted(x[1] for x in used_all if isinstance(x, tuple) and x[0] == "unknown")
    if unknown:
        print("labels guessed for: " + ", ".join(unknown), file=sys.stderr)
    return notes


def section(keymap_dir):
    target = target_for(keymap_dir)
    userspace = uses_userspace(keymap_dir)
    layers, local_layouts = extract_layers(keymap_dir, userspace)
    layout_name = layers[0]["layout"]
    if target in POSITIONS:
        positions = POSITIONS[target]
    elif layout_name in local_layouts:
        positions = positions_from_macro(local_layouts[layout_name], layout_name)
    else:
        positions = positions_from_qmk(target, layout_name)
    n = len(layers[0]["keys"])
    if len(positions) != n:
        sys.exit(f"{layout_name}: {n} keys in the keymap, {len(positions)} positions")
    layout = grid(positions)
    td = tap_dance_notes(source_files(keymap_dir, userspace))

    base = layers[0]
    out, used_all = [], set()
    for layer in ordered(layers):
        used = set()
        labels = [label(k, used) for k in layer["keys"]]
        used_all |= used
        title = layer_title(layer["name"])
        if layer is base:
            how = "base layer"
        else:
            acts = activators(layers, layer["name"])
            how = ""
            direct = [a for a in acts if a[0] == layers.index(base)]
            for li, ki, kind in direct or acts:
                via = layers[li]
                key = label(via["keys"][ki], set())
                if kind == "toggle":
                    how = f"toggle with `{key}` on {layer_title(via['name'])}"
                    break
                if via is base:
                    how = f"hold `{key}`"
                    labels[ki] = labels[ki] or f"[{key}]"
                    break
                # Reached from another layer: hold that layer's key on Main first.
                outer = [a for a in activators(layers, via["name"]) if a[0] == layers.index(base) and a[2] == "hold"]
                if outer:
                    _, oki, _ = outer[0]
                    okey = label(base["keys"][oki], set())
                    how = f"hold `{okey}`, then `{key}`"
                    labels[oki] = labels[oki] or f"[{okey}]"
                    labels[ki] = labels[ki] or f"[{key}]"
                    break
        out.append(f"### {title}" + (f" ({how})" if how else ""))
        out.append("")
        out.append("```")
        out.append(draw(labels, layout))
        out.append("```")
        out.append("")

    notes = notes_for(used_all, td, userspace)
    if notes:
        out.extend(f"- {n}" for n in notes)
        out.append("")

    cmb = combos(keymap_dir, object_macros(source_files(keymap_dir, userspace)))
    if cmb:
        out.append("### Combos")
        out.append("")
        out.append("Press together:")
        out.append("")
        out.append("| Keys | Sends |")
        out.append("|---|---|")
        def cell(text):
            return text.replace("|", "\\|")
        out.extend(f"| {cell(' + '.join(k))} | {cell(d)} |" for k, d in cmb)
        out.append("")
        on_layers = {lab for layer in layers for lab in (label(k, set()) for k in layer["keys"])}
        on_layers |= {lab.split("/")[0] for lab in on_layers if "/" in lab and len(lab) > 1}
        absent = sorted({k for keys, _ in cmb for k in keys if k not in on_layers})
        if absent:
            out.append(", ".join(f"`{k}`" for k in absent) + " is not on any layer, so the combos using it never fire.")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def userspace_section():
    """The shared layers: users/nedsi/wrapper.h row macros, as 3x5 + 3x5 grids."""
    text = (ROOT / "users/nedsi/wrapper.h").read_text()
    rows = {}
    for m in re.finditer(r"#\s*define\s+(_+([A-Z]+)_([LR])([123])_+)\s", text):
        rows.setdefault(m.group(2), {})[m.group(3) + m.group(4)] = m.group(1)
    names = [n for n, r in rows.items() if len(r) == 6]
    work = pathlib.Path(tempfile.mkdtemp())
    try:
        entries = ",\n".join(
            f"[_{n}] = ROWS({', '.join(rows[n][k] for k in ('L1', 'R1', 'L2', 'R2', 'L3', 'R3'))})" for n in names)
        (work / "keymap.c").write_text(
            '#include "nedsi.h"\nconst uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {\n' + entries + "\n};\n")
        layers, _ = extract_layers(work, True)
    finally:
        shutil.rmtree(work)
    positions = [[x, y] for y in range(3) for x in [*range(0, 5), *range(6, 11)]]
    layout = grid(positions)
    td = tap_dance_notes([f for f in (ROOT / "users/nedsi").iterdir() if f.suffix == ".c"])
    out, used_all = [], set()
    for layer in ordered(layers):
        used = set()
        labels = [label(k, used) for k in layer["keys"]]
        used_all |= used
        out += [f"#### {layer_title(layer['name'])}", "", "```", draw(labels, layout), "```", ""]
    notes = notes_for(used_all, td, True)
    if notes:
        out.extend(f"- {n}" for n in notes)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


USERSPACE_INTRO = """Generated by `util/layers.py users/nedsi` from the row macros in
`users/nedsi/wrapper.h`: the three main rows of each half. Each keymap adds its
own outer columns, thumbs and layer keys around them. Empty keys fall through.
"""


INTRO = """Generated by `util/layers.py` in qmk-userspace from this keymap; rerun it after a
keymap change. Empty keys fall through to the layer below. `[NAME]` marks the
key held to reach that layer; upper-case `SYM`, `NUM`, ... are hold-for-layer keys.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("keymap_dir")
    ap.add_argument("--print", action="store_true", help="print instead of updating README.md")
    a = ap.parse_args()
    keymap_dir = (ROOT / a.keymap_dir).resolve()
    if keymap_dir == (ROOT / "users/nedsi").resolve():
        block = f"{MARK_START}\n{USERSPACE_INTRO}\n{userspace_section()}{MARK_END}"
        keymap_dir = ROOT
    else:
        block = f"{MARK_START}\n{INTRO}\n{section(keymap_dir)}{MARK_END}"
    if a.print:
        print(block)
        return
    readme = keymap_dir / "README.md"
    text = readme.read_text() if readme.exists() else ""
    if MARK_START in text:
        pre, rest = text.split(MARK_START, 1)
        text = pre + block + rest.split(MARK_END, 1)[1]
    else:
        new = f"## Layers\n\n{block}\n"
        anchor = re.search(r"^## Build", text, re.M)
        text = text[:anchor.start()] + new + "\n" + text[anchor.start():] if anchor else text.rstrip() + "\n\n" + new
    readme.write_text(text)
    print(f"updated {readme.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
