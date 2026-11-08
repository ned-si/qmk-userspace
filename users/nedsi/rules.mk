SRC += nedsi.c
SRC += custom_unicode.c
SRC += custom_strings.c
SRC += custom_shift_keys.c

UNICODE_COMMON = yes
UNICODE_ENABLE = no
UNICODEMAP_ENABLE = yes
UCIS_ENABLE = no
NKRO_ENABLE = yes
TAP_DANCE_ENABLE = yes
COMBO_ENABLE = no
CAPS_WORD_ENABLE = yes

# Tap dance actions must be visible to QMK's keymap introspection, so this file
# is compiled as part of the keymap instead of through SRC.
INTROSPECTION_KEYMAP_C += tapdance.c
