#include "tapdance.h"

// create a global instance of the tapdance state type
static td_state_t td_state;

// track the tapdance state to return
int cur_dance (qk_tap_dance_state_t *state) {
  if (state->count == 1) {
    if (state->interrupted || !state->pressed) {
        return SINGLE_TAP;
    } else {
        return SINGLE_HOLD;
    }
  }
  if (state->count == 2) {
      return DOUBLE_SINGLE_TAP;
  }
  else {
      return 3; // any number higher than the maximum state value you return above
  }
};

void CA_CC_CV_finished (qk_tap_dance_state_t *state, void *user_data) {
  td_state = cur_dance(state);
  switch (td_state) {
    case SINGLE_TAP:
      tap_code16(C(KC_C));
      break;
    case SINGLE_HOLD:
      tap_code16(C(KC_V));
      break;
    case DOUBLE_SINGLE_TAP:
      tap_code16(C(KC_A));
      break;
  }
};

void UNI_W_L_finished (qk_tap_dance_state_t *state, void *user_data) {
  td_state = cur_dance(state);
  switch (td_state) {
    case SINGLE_TAP:
      tap_code16(UC_M_WC);
      break;
    case DOUBLE_SINGLE_TAP:
      tap_code16(UC_M_LN);
    break;
    default: break;
  }
};

void NXT_PRV_finished (qk_tap_dance_state_t *state, void *user_data) {
  td_state = cur_dance(state);
  switch (td_state) {
    case SINGLE_TAP:
      tap_code16(KC_MNXT);
      break;
    case DOUBLE_SINGLE_TAP:
      tap_code16(KC_MPRV);
    break;
    default: break;
  }
};

qk_tap_dance_action_t tap_dance_actions[] = {
    [CA_CC_CV] = ACTION_TAP_DANCE_FN_ADVANCED(NULL, CA_CC_CV_finished, NULL),
    [UNI_W_L] = ACTION_TAP_DANCE_FN_ADVANCED(NULL, UNI_W_L_finished, NULL),
    [NXT_PRV] = ACTION_TAP_DANCE_FN_ADVANCED(NULL, NXT_PRV_finished, NULL),
};

uint16_t get_tapping_term(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case HOME_A:
            return TAPPING_TERM + 50;
        case HOME_S:
            return TAPPING_TERM + 50;
        /* case HOME_D: */
        /*     return TAPPING_TERM - 20; */
        case HOME_F:
            return TAPPING_TERM - 20;
        case HOME_G:
            return TAPPING_TERM - 10;
        case HOME_H:
            return TAPPING_TERM - 10;
        case HOME_J:
            return TAPPING_TERM - 20;
        /* case HOME_K: */
        /*     return TAPPING_TERM - 20; */
        case HOME_L:
            return TAPPING_TERM + 50;
        case HOME_SCLN:
            return TAPPING_TERM + 50;
        default:
            return TAPPING_TERM;
    }
};

