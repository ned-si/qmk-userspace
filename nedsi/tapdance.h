#pragma once

#include "nedsi.h"

// Tap dance states
typedef enum {
  SINGLE_TAP,
  SINGLE_HOLD,
  DOUBLE_SINGLE_TAP
} td_state_t;

enum {
    CA_CC_CV,
    UNI_W_L,
    NXT_PRV,
};

#define CACCCV TD(CA_CC_CV)
#define UNIWL TD(UNI_W_L)
#define NXTPRV TD(NXT_PRV)

int cur_dance (tap_dance_state_t *state);
void CA_CC_CV_finished (tap_dance_state_t *state, void *user_data);
void UNI_W_L_finished (tap_dance_state_t *state, void *user_data);
void NXT_PRV_finished (tap_dance_state_t *state, void *user_data);
uint16_t get_tapping_term(uint16_t keycode, keyrecord_t *record);
