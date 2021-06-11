#include "nedsi.h"

uint16_t copy_paste_timer;

__attribute__((weak)) bool process_record_keymap(uint16_t keycode, keyrecord_t *record) { return true; }

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case KC_EAIG:
            if (record->event.pressed) {
                send_unicode_string("é");
            }
            break;

        case KC_EGRV:
            if (record->event.pressed) {
                send_unicode_string("è");
            }
            break;

        case KC_ECIR:
            if (record->event.pressed) {
                send_unicode_string("ê");
            }
            break;

        case KC_EUML:
            if (record->event.pressed) {
                send_unicode_string("ë");
            }
            break;

        case KC_AGRV:
            if (record->event.pressed) {
                send_unicode_string("à");
            }
            break;

        case KC_ACIR:
            if (record->event.pressed) {
                send_unicode_string("â");
            }
            break;

        case KC_AUML:
            if (record->event.pressed) {
                send_unicode_string("ä");
            }
            break;

        case KC_ICIR:
            if (record->event.pressed) {
                send_unicode_string("î");
            }
            break;

        case KC_IUML:
            if (record->event.pressed) {
                send_unicode_string("ï");
            }
            break;

        case KC_OCIR:
            if (record->event.pressed) {
                send_unicode_string("ô");
            }
            break;

        case KC_OUML:
            if (record->event.pressed) {
                send_unicode_string("ö");
            }
            break;

        case KC_UGRV:
            if (record->event.pressed) {
                send_unicode_string("ù");
            }
            break;

        case KC_UCIR:
            if (record->event.pressed) {
                send_unicode_string("û");
            }
            break;

        case KC_UUML:
            if (record->event.pressed) {
                send_unicode_string("ü");
            }
            break;

        case KC_CCED:
            if (record->event.pressed) {
                send_unicode_string("ç");
            }
            break;

        case KC_DEGR:
            if (record->event.pressed) {
                send_unicode_string("°");
            }
            break;

        case KC_EURO:
            if (record->event.pressed) {
                send_unicode_string("€");
            }
            break;

        case KC_SHRG:
            if (record->event.pressed) {
                send_unicode_string("¯\\_(ツ)_/¯");
            }
            break;

        case KC_SIGN:
            if (record->event.pressed) {
                send_unicode_string("Cheers,\n\n\nJulien");
            }
            break;

        case KC_VCLN: {
           static uint16_t kc;
           if (record->event.pressed) {
                if ( get_mods() & MOD_MASK_SHIFT) {
                    kc = KC_SCLN;
                    del_mods(MOD_MASK_SHIFT);
                } else {
                    kc = KC_COLN;
                }
                register_code16(kc);
            } else {
                unregister_code16(kc);
            }
            break;
        }

    }

    return true;

}
