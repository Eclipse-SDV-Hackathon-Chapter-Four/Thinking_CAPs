/* SPDX-License-Identifier: Apache-2.0 */
#include "uds_ecu.h"
#include <string.h>

#define PADDING 0xCCU
#define DTC_AVAILABILITY_MASK 0x7FU
#define STATUS_NOT_COMPLETED 0x50U /* not completed since last clear and this cycle */
#define STATUS_FAILED 0x2FU        /* failed, this cycle, pending, confirmed, since last clear */
#define NRC_SERVICE_NOT_SUPPORTED 0x11U
#define NRC_SUBFUNCTION_NOT_SUPPORTED 0x12U
#define NRC_INCORRECT_LENGTH 0x13U
#define NRC_REQUEST_OUT_OF_RANGE 0x31U

static bool expired(uint32_t now, uint32_t deadline) { return (int32_t)(now - deadline) >= 0; }

static void send_frame(struct uds_ecu *ecu, const uint8_t *data, unsigned length)
{
    struct can_frame frame;
    memset(&frame, 0, sizeof(frame));
    frame.can_id = DIAG_RESPONSE_ID;
    frame.can_dlc = CAN_MAX_DLEN;
    memset(frame.data, PADDING, sizeof(frame.data));
    memcpy(frame.data, data, length);
    ecu->send(&frame, ecu->context);
}

static void send_flow_control(struct uds_ecu *ecu, uint8_t flow_status)
{
    const uint8_t fc[3] = {(uint8_t)(0x30U | flow_status), 0x00U, 0x00U}; /* BS 0, STmin 0 */
    send_frame(ecu, fc, sizeof(fc));
}

/* Sends a response as single frame, or starts a segmented transmission. */
static void transmit(struct uds_ecu *ecu, const uint8_t *message, uint16_t length, uint32_t now_ms)
{
    ++ecu->responses;
    if (length <= 7U) {
        uint8_t sf[8] = {(uint8_t)length};
        memcpy(&sf[1], message, length);
        send_frame(ecu, sf, 1U + length);
        ecu->tx_state = UDS_TX_IDLE;
        return;
    }
    memcpy(ecu->tx, message, length);
    ecu->tx_length = length;
    uint8_t ff[8] = {(uint8_t)(0x10U | (length >> 8)), (uint8_t)(length & 0xFFU)};
    memcpy(&ff[2], message, 6U);
    send_frame(ecu, ff, sizeof(ff));
    ecu->tx_sent = 6U;
    ecu->tx_sn = 1U;
    ecu->tx_state = UDS_TX_WAIT_FC;
    ecu->tx_deadline_ms = now_ms + UDS_NBS_TIMEOUT_MS;
}

static void negative(struct uds_ecu *ecu, uint8_t sid, uint8_t nrc, bool functional, uint32_t now_ms)
{
    /* ISO 14229-1: no NRC 0x11, 0x12 or 0x31 to functionally addressed requests */
    if (functional && (nrc == NRC_SERVICE_NOT_SUPPORTED || nrc == NRC_SUBFUNCTION_NOT_SUPPORTED ||
                       nrc == NRC_REQUEST_OUT_OF_RANGE))
        return;
    const uint8_t response[3] = {0x7FU, sid, nrc};
    transmit(ecu, response, sizeof(response), now_ms);
}

static void apply_vcu_status(struct uds_ecu *ecu, bool lost)
{
    if (lost) ecu->dtc_status = (uint8_t)((ecu->dtc_status | STATUS_FAILED) & ~STATUS_NOT_COMPLETED);
    else ecu->dtc_status = (uint8_t)(ecu->dtc_status & ~(0x01U | STATUS_NOT_COMPLETED));
}

static uint16_t append_dtc(const struct uds_ecu *ecu, uint8_t *out)
{
    out[0] = (uint8_t)(UDS_DTC_VCU_LOST >> 16);
    out[1] = (uint8_t)(UDS_DTC_VCU_LOST >> 8);
    out[2] = (uint8_t)UDS_DTC_VCU_LOST;
    out[3] = ecu->dtc_status;
    return 4U;
}

static void read_did(struct uds_ecu *ecu, const uint8_t *req, uint16_t len, bool functional, uint32_t now_ms)
{
    if (len != 3U) { negative(ecu, req[0], NRC_INCORRECT_LENGTH, functional, now_ms); return; }
    uint16_t did = (uint16_t)((req[1] << 8) | req[2]);
    uint8_t response[UDS_MAX_MESSAGE] = {0x62U, req[1], req[2]};
    uint16_t length = 3U;
    const char *text = NULL;
    if (did == UDS_DID_SOFTWARE_VERSION) text = ecu->software_version;
    else if (did == UDS_DID_SERIAL_NUMBER) text = ecu->serial_number;
    else if (did == UDS_DID_LIGHTS_STATE) {
        response[length++] = ecu->lights;
        response[length++] = ecu->input_stale ? 1U : 0U;
    } else { negative(ecu, req[0], NRC_REQUEST_OUT_OF_RANGE, functional, now_ms); return; }
    if (text) {
        size_t size = strlen(text);
        if (size > sizeof(response) - length) size = sizeof(response) - length;
        memcpy(&response[length], text, size);
        length = (uint16_t)(length + size);
    }
    transmit(ecu, response, length, now_ms);
}

static void process(struct uds_ecu *ecu, const uint8_t *req, uint16_t len, bool functional, uint32_t now_ms)
{
    ++ecu->requests;
    uint8_t sid = req[0];
    bool suppress = len >= 2U && (req[1] & 0x80U);
    uint8_t sub = len >= 2U ? (uint8_t)(req[1] & 0x7FU) : 0U;
    switch (sid) {
    case 0x10:
        if (len != 2U) { negative(ecu, sid, NRC_INCORRECT_LENGTH, functional, now_ms); return; }
        if (sub != 0x01U && sub != 0x03U) { negative(ecu, sid, NRC_SUBFUNCTION_NOT_SUPPORTED, functional, now_ms); return; }
        ecu->session = sub;
        if (!suppress) {
            /* P2 50 ms, P2* 5000 ms (10 ms resolution) */
            const uint8_t response[6] = {0x50U, sub, 0x00U, 0x32U, 0x01U, 0xF4U};
            transmit(ecu, response, sizeof(response), now_ms);
        }
        return;
    case 0x3E:
        if (len != 2U) { negative(ecu, sid, NRC_INCORRECT_LENGTH, functional, now_ms); return; }
        if (sub != 0x00U) { negative(ecu, sid, NRC_SUBFUNCTION_NOT_SUPPORTED, functional, now_ms); return; }
        if (!suppress) {
            const uint8_t response[2] = {0x7EU, 0x00U};
            transmit(ecu, response, sizeof(response), now_ms);
        }
        return;
    case 0x22:
        read_did(ecu, req, len, functional, now_ms);
        return;
    case 0x19: {
        if (len < 2U) { negative(ecu, sid, NRC_INCORRECT_LENGTH, functional, now_ms); return; }
        uint8_t response[8] = {0x59U, sub, DTC_AVAILABILITY_MASK};
        uint16_t length = 3U;
        if (sub == 0x02U) {
            if (len != 3U) { negative(ecu, sid, NRC_INCORRECT_LENGTH, functional, now_ms); return; }
            if (ecu->dtc_status & req[2] & DTC_AVAILABILITY_MASK) length = (uint16_t)(length + append_dtc(ecu, &response[length]));
        } else if (sub == 0x0AU) {
            if (len != 2U) { negative(ecu, sid, NRC_INCORRECT_LENGTH, functional, now_ms); return; }
            length = (uint16_t)(length + append_dtc(ecu, &response[length]));
        } else { negative(ecu, sid, NRC_SUBFUNCTION_NOT_SUPPORTED, functional, now_ms); return; }
        transmit(ecu, response, length, now_ms);
        return;
    }
    case 0x14: {
        if (len != 4U) { negative(ecu, sid, NRC_INCORRECT_LENGTH, functional, now_ms); return; }
        uint32_t group = ((uint32_t)req[1] << 16) | ((uint32_t)req[2] << 8) | req[3];
        if (group != 0xFFFFFFUL && group != UDS_DTC_VCU_LOST) {
            negative(ecu, sid, NRC_REQUEST_OUT_OF_RANGE, functional, now_ms); return;
        }
        ecu->dtc_status = STATUS_NOT_COMPLETED;
        if (ecu->input_stale) apply_vcu_status(ecu, true); /* still lost: detected again */
        const uint8_t response[1] = {0x54U};
        transmit(ecu, response, sizeof(response), now_ms);
        return;
    }
    default:
        negative(ecu, sid, NRC_SERVICE_NOT_SUPPORTED, functional, now_ms);
        return;
    }
}

void uds_init(struct uds_ecu *ecu, const char *software_version, const char *serial_number,
              uds_send_fn send, void *context)
{
    memset(ecu, 0, sizeof(*ecu));
    ecu->software_version = software_version;
    ecu->serial_number = serial_number;
    ecu->send = send;
    ecu->context = context;
    ecu->session = 0x01U;
    ecu->dtc_status = STATUS_NOT_COMPLETED;
}

bool uds_accepts(const struct can_frame *frame)
{
    return (frame->can_id == DIAG_REQUEST_ID || frame->can_id == DIAG_FUNCTIONAL_ID) &&
           frame->can_dlc >= 1U && frame->can_dlc <= CAN_MAX_DLEN; /* rejects EFF/RTR/ERR flags */
}

static void receive_flow_control(struct uds_ecu *ecu, const struct can_frame *frame, uint32_t now_ms)
{
    if (ecu->tx_state != UDS_TX_WAIT_FC || frame->can_dlc < 3U) return;
    uint8_t status = frame->data[0] & 0x0FU;
    if (status == 0x00U) { /* continue to send */
        uint8_t stmin = frame->data[2];
        ecu->tx_stmin_ms = stmin <= 0x7FU ? stmin : (stmin >= 0xF1U && stmin <= 0xF9U) ? 1U : 0x7FU;
        ecu->tx_block_size = frame->data[1];
        ecu->tx_block_left = frame->data[1];
        ecu->tx_state = UDS_TX_SENDING;
        ecu->tx_next_ms = now_ms;
        uds_tick(ecu, now_ms);
    } else if (status == 0x01U) { /* wait */
        ecu->tx_deadline_ms = now_ms + UDS_NBS_TIMEOUT_MS;
    } else {
        ecu->tx_state = UDS_TX_IDLE; /* overflow or invalid: abort */
    }
}

void uds_frame(struct uds_ecu *ecu, const struct can_frame *frame, uint32_t now_ms)
{
    if (!uds_accepts(frame)) return;
    bool functional = frame->can_id == DIAG_FUNCTIONAL_ID;
    const uint8_t *d = frame->data;
    uint8_t type = d[0] >> 4;
    if (type == 0x0U) { /* single frame */
        uint8_t length = d[0] & 0x0FU;
        if (length == 0U || length > 7U || length + 1U > frame->can_dlc) return;
        ecu->rx_active = false;
        process(ecu, &d[1], length, functional, now_ms);
    } else if (type == 0x1U && !functional && frame->can_dlc == CAN_MAX_DLEN) { /* first frame */
        uint16_t length = (uint16_t)(((d[0] & 0x0FU) << 8) | d[1]);
        if (length < 8U) return;
        if (length > UDS_MAX_MESSAGE) { send_flow_control(ecu, 0x02U); ecu->rx_active = false; return; }
        memcpy(ecu->rx, &d[2], 6U);
        ecu->rx_length = length;
        ecu->rx_received = 6U;
        ecu->rx_sn = 1U;
        ecu->rx_active = true;
        ecu->rx_deadline_ms = now_ms + UDS_NCR_TIMEOUT_MS;
        send_flow_control(ecu, 0x00U);
    } else if (type == 0x2U && !functional && ecu->rx_active) { /* consecutive frame */
        if ((d[0] & 0x0FU) != ecu->rx_sn) { ecu->rx_active = false; return; }
        uint16_t chunk = (uint16_t)(ecu->rx_length - ecu->rx_received);
        if (chunk > 7U) chunk = 7U;
        if (chunk + 1U > frame->can_dlc) { ecu->rx_active = false; return; }
        memcpy(&ecu->rx[ecu->rx_received], &d[1], chunk);
        ecu->rx_received = (uint16_t)(ecu->rx_received + chunk);
        ecu->rx_sn = (uint8_t)((ecu->rx_sn + 1U) & 0x0FU);
        ecu->rx_deadline_ms = now_ms + UDS_NCR_TIMEOUT_MS;
        if (ecu->rx_received == ecu->rx_length) {
            ecu->rx_active = false;
            process(ecu, ecu->rx, ecu->rx_length, false, now_ms);
        }
    } else if (type == 0x3U && !functional) {
        receive_flow_control(ecu, frame, now_ms);
    }
}

void uds_tick(struct uds_ecu *ecu, uint32_t now_ms)
{
    if (ecu->rx_active && expired(now_ms, ecu->rx_deadline_ms)) ecu->rx_active = false; /* N_Cr */
    if (ecu->tx_state == UDS_TX_WAIT_FC && expired(now_ms, ecu->tx_deadline_ms)) ecu->tx_state = UDS_TX_IDLE; /* N_Bs */
    while (ecu->tx_state == UDS_TX_SENDING && expired(now_ms, ecu->tx_next_ms)) {
        uint8_t cf[8] = {(uint8_t)(0x20U | ecu->tx_sn)};
        uint16_t chunk = (uint16_t)(ecu->tx_length - ecu->tx_sent);
        if (chunk > 7U) chunk = 7U;
        memcpy(&cf[1], &ecu->tx[ecu->tx_sent], chunk);
        send_frame(ecu, cf, 1U + chunk);
        ecu->tx_sent = (uint16_t)(ecu->tx_sent + chunk);
        ecu->tx_sn = (uint8_t)((ecu->tx_sn + 1U) & 0x0FU);
        ecu->tx_next_ms = now_ms + ecu->tx_stmin_ms;
        if (ecu->tx_sent >= ecu->tx_length) { ecu->tx_state = UDS_TX_IDLE; break; }
        if (ecu->tx_block_size != 0U && --ecu->tx_block_left == 0U) {
            ecu->tx_state = UDS_TX_WAIT_FC;
            ecu->tx_deadline_ms = now_ms + UDS_NBS_TIMEOUT_MS;
        }
        if (ecu->tx_stmin_ms != 0U) break;
    }
}

void uds_set_lights(struct uds_ecu *ecu, uint8_t lights, bool input_stale)
{
    ecu->lights = (uint8_t)(lights & 0x03U);
    ecu->input_stale = input_stale;
}

void uds_report_vcu_lost(struct uds_ecu *ecu, bool lost)
{
    ecu->input_stale = lost;
    apply_vcu_status(ecu, lost);
}
