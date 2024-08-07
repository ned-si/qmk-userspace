#pragma once
#include "nedsi.h"

#define LAYOUT_wrapper(...) LAYOUT(__VA_ARGS__)

// MAIN layout
#define ________________MAIN_L1________________     KC_Q,    KC_W,    KC_E,    KC_R,    KC_T
#define ________________MAIN_L2________________     HOME_A,  HOME_S,  HOME_D,  HOME_F,  HOME_G
#define ________________MAIN_L3________________     KC_Z,    KC_X,    KC_C,    KC_V,    KC_B

#define ________________MAIN_R1________________     KC_Y,    KC_U,    KC_I,    KC_O,    KC_P
#define ________________MAIN_R2________________     HOME_H,  HOME_J,  HOME_K,  HOME_L,  HOME_SCLN
#define ________________MAIN_R3________________     KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH

// GAMING layout
#define ________________GAMING_L2_________________     GAME_A,    KC_S,    KC_D,    KC_F,    KC_G
#define ________________GAMING_L3_________________     GAME_Z,    KC_X,    KC_C,    KC_V,    KC_B

// NUM layout
#define ________________NUM_L1________________     KC_F12,   KC_F7,   KC_F8,   KC_F9, _______
#define ________________NUM_L2________________     KC_F11,   KC_F4,   KC_F5,   KC_F6, _______
#define ________________NUM_L3________________     KC_F10,   KC_F1,   KC_F2,   KC_F3, _______

#define ________________NUM_R1________________     _______,    KC_7,    KC_8,    KC_9, _______
#define ________________NUM_R2________________     KC_PPLS,    KC_4,    KC_5,    KC_6,    KC_0
#define ________________NUM_R3________________      KC_EQL,    KC_1,    KC_2,    KC_3,  KC_DOT

// SYM layout
#define ________________SYM_L1________________    _______, _______, KC_EURO, KC_AMPR, KC_DEGR
#define ________________SYM_L2________________    _______, KC_TILD, KC_ASTR,  KC_GRV, KC_PMED
#define ________________SYM_L3________________    _______, _______, KC_PERC, KC_CIRC, KC_MINS

#define ________________SYM_R1________________    _______, KC_HASH, KC_LCBR, KC_RCBR, _______
#define ________________SYM_R2________________     KC_DLR, KC_EXLM, KC_LBRC, KC_RBRC,  KC_EQL
#define ________________SYM_R3________________      KC_AT, KC_PIPE, KC_LPRN, KC_RPRN, KC_BSLS

// NAV layout
#define ________________NAV_L1________________      _______, _______, _______, _______, _______
#define ________________NAV_L2________________      KC_LGUI, KC_LALT, KC_LCTL, KC_LSFT, _______
#define ________________NAV_L3________________      _______, _______,TG(_GAMING), _______, UNIWL

#define ________________NAV_R1________________      KC_HOME, KC_PGDN,KC_PGUP, KC_END , _______
#define ________________NAV_R2________________      KC_LEFT, KC_DOWN, KC_UP , KC_RGHT, _______
#define ________________NAV_R3________________      _______, _______, _______, _______, _______

// ACC layout
// TODO: add emojis
#define ________________ACC_L1________________     _______, KC_EGRV, KC_EAIG, _______, _______
#define ________________ACC_L2________________     KC_AGRV, KC_ACIR, KC_ECIR, KC_SHRG, _______
#define ________________ACC_L3________________     _______, _______, KC_CCED, _______, _______

#define ________________ACC_R1________________     DED_UML, KC_UGRV, KC_ICIR, KC_OCIR, _______
#define ________________ACC_R2________________     DED_CIR, KC_UCIR, KC_IUML, KC_OUML, _______
#define ________________ACC_R3________________     _______, _______, _______, _______, _______

// MISC layout
#define ________________MISC_L1________________     QK_BOOT, _______, _______, _______, _______
#define ________________MISC_L2________________     _______, _______, C(KC_C), C(KC_V), KC_CAPS
#define ________________MISC_L3________________     _______, _______, C(S(KC_C)), C(S(KC_V)), _______

#define ________________MISC_R1________________     _______, _______, _______, _______, _______
#define ________________MISC_R2________________     KC_MPRV, KC_VOLD, KC_VOLU, KC_MNXT, _______
#define ________________MISC_R3________________     _______, _______, _______, _______, _______
