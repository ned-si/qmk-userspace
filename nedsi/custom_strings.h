#pragma once
#include "nedsi.h"

#define PLACEHOLDER_SAFE_RANGE SAFE_RANGE

enum userspace_custom_keycodes {
  KC_EAIG=PLACEHOLDER_SAFE_RANGE,
  KC_EGRV,
  KC_ECIR,
  KC_EUML,
  KC_AGRV,
  KC_ACIR,
  KC_AUML,
  KC_ICIR,
  KC_IUML,
  KC_OCIR,
  KC_OUML,
  KC_UGRV,
  KC_UCIR,
  KC_UUML,
  KC_CCED,
  KC_DEGR,
  KC_EURO,
  KC_SHRG,
  KC_SIGN,
  KC_VCLN,
  NEW_SAFE_RANGE
};

bool process_record_keymap(uint16_t keycode, keyrecord_t *record);
