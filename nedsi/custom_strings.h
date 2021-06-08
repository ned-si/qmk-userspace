#pragma once
#include "nedsi.h"

enum userspace_custom_keycodes {
  KC_EAIG,
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
  KC_EURO//,
  /* UC_CLN */
};

bool process_record_keymap(uint16_t keycode, keyrecord_t *record);
