/* SPDX-License-Identifier: Apache-2.0 */
#ifndef UDS_ECU_H
#define UDS_ECU_H

/* UDS-on-CAN server of the rear lighting controller (ISO 14229-1 subset on ISO 15765-2).
 *
 * Physical requests on 0x7E1, functional requests on 0x7DF, responses on 0x7E9; normal
 * 11-bit addressing, classic CAN, DLC 8 padded with 0xCC. Independent of ThreadX and
 * SocketCAN: the caller passes received frames and the time, and transmits through a
 * callback. See docs/can-lighting-contract.md, "Diagnostics". */

#include <linux/can.h>
#include <stdbool.h>
#include <stdint.h>

#define DIAG_REQUEST_ID 0x7E1U
#define DIAG_FUNCTIONAL_ID 0x7DFU
#define DIAG_RESPONSE_ID 0x7E9U
#define UDS_MAX_MESSAGE 64U
#define UDS_NCR_TIMEOUT_MS 1000U
#define UDS_NBS_TIMEOUT_MS 1000U
/* DTC U0293 "Lost communication with vehicle control unit", ISO 15031-6 encoding */
#define UDS_DTC_VCU_LOST 0xC29300UL
#define UDS_DID_SOFTWARE_VERSION 0xF195U
#define UDS_DID_SERIAL_NUMBER 0xF18CU
#define UDS_DID_LIGHTS_STATE 0x4C01U

typedef void (*uds_send_fn)(const struct can_frame *frame, void *context);

enum uds_tx_state { UDS_TX_IDLE, UDS_TX_WAIT_FC, UDS_TX_SENDING };

struct uds_ecu {
    const char *software_version;
    const char *serial_number;
    uds_send_fn send;
    void *context;
    /* ISO-TP reception */
    uint8_t rx[UDS_MAX_MESSAGE];
    uint16_t rx_length, rx_received;
    uint8_t rx_sn;
    bool rx_active;
    uint32_t rx_deadline_ms;
    /* ISO-TP transmission */
    uint8_t tx[UDS_MAX_MESSAGE];
    uint16_t tx_length, tx_sent;
    uint8_t tx_sn, tx_block_size, tx_block_left;
    enum uds_tx_state tx_state;
    uint32_t tx_stmin_ms, tx_next_ms, tx_deadline_ms;
    /* application */
    uint8_t session;
    uint8_t lights;      /* bit 0 reverse, bit 1 brake (last command) */
    bool input_stale;
    uint8_t dtc_status;  /* ISO 14229-1 status of UDS_DTC_VCU_LOST */
    unsigned long requests, responses;
};

void uds_init(struct uds_ecu *ecu, const char *software_version, const char *serial_number,
              uds_send_fn send, void *context);
/* True for frames addressed to the diagnostic server (0x7E1, 0x7DF; standard data frames). */
bool uds_accepts(const struct can_frame *frame);
void uds_frame(struct uds_ecu *ecu, const struct can_frame *frame, uint32_t now_ms);
/* Sends due consecutive frames and supervises N_Bs and N_Cr; call at least every 10 ms. */
void uds_tick(struct uds_ecu *ecu, uint32_t now_ms);
/* Lighting state for DID 0x4C01 and the VCU communication test (DTC U0293). */
void uds_set_lights(struct uds_ecu *ecu, uint8_t lights, bool input_stale);
void uds_report_vcu_lost(struct uds_ecu *ecu, bool lost);

#endif
