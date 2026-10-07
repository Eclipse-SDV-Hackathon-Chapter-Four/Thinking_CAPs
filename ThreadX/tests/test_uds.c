/* SPDX-License-Identifier: Apache-2.0 */
#include "uds_ecu.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr, "Failed line %d: %s\n", __LINE__, #x); exit(1); } } while (0)

static struct can_frame sent[64];
static unsigned sent_count;

static void capture(const struct can_frame *frame, void *context)
{
    (void)context;
    CHECK(sent_count < sizeof(sent) / sizeof(sent[0]));
    sent[sent_count++] = *frame;
}

static struct can_frame frame(canid_t id, const uint8_t *data, unsigned length)
{
    struct can_frame f;
    memset(&f, 0, sizeof(f));
    f.can_id = id;
    f.can_dlc = 8;
    memset(f.data, 0xAA, sizeof(f.data));
    memcpy(f.data, data, length);
    return f;
}

/* Sends a request of up to 7 bytes as single frame. */
static void single(struct uds_ecu *ecu, canid_t id, const uint8_t *request, unsigned length, uint32_t now)
{
    uint8_t data[8] = {(uint8_t)length};
    memcpy(&data[1], request, length);
    struct can_frame f = frame(id, data, 1 + length);
    uds_frame(ecu, &f, now);
}

static void expect_single(unsigned index, const uint8_t *response, unsigned length)
{
    CHECK(index < sent_count);
    CHECK(sent[index].can_id == DIAG_RESPONSE_ID && sent[index].can_dlc == 8);
    CHECK(sent[index].data[0] == length);
    CHECK(memcmp(&sent[index].data[1], response, length) == 0);
    for (unsigned i = 1 + length; i < 8; ++i) CHECK(sent[index].data[i] == 0xCC);
}

static void reset(struct uds_ecu *ecu)
{
    sent_count = 0;
    uds_init(ecu, "THREADX-LIGHTS 1.1.0", "TXZL-SIM-0001", capture, NULL);
}

int main(void)
{
    struct uds_ecu ecu;
    reset(&ecu);

    /* frame acceptance */
    struct can_frame f = frame(DIAG_REQUEST_ID, (const uint8_t[]){0x02, 0x3E, 0x00}, 3);
    CHECK(uds_accepts(&f));
    f.can_id = DIAG_FUNCTIONAL_ID; CHECK(uds_accepts(&f));
    f.can_id = DIAG_REQUEST_ID | CAN_EFF_FLAG; CHECK(!uds_accepts(&f));
    f.can_id = DIAG_REQUEST_ID | CAN_RTR_FLAG; CHECK(!uds_accepts(&f));
    f.can_id = 0x1F1; CHECK(!uds_accepts(&f));
    f.can_id = DIAG_REQUEST_ID; f.can_dlc = 0; CHECK(!uds_accepts(&f));

    /* TesterPresent, suppressed, wrong sub-function, physical and functional */
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x3E, 0x00}, 2, 0);
    expect_single(0, (const uint8_t[]){0x7E, 0x00}, 2);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x3E, 0x80}, 2, 0);
    single(&ecu, DIAG_FUNCTIONAL_ID, (const uint8_t[]){0x3E, 0x80}, 2, 0);
    CHECK(sent_count == 1);
    single(&ecu, DIAG_FUNCTIONAL_ID, (const uint8_t[]){0x3E, 0x00}, 2, 0);
    expect_single(1, (const uint8_t[]){0x7E, 0x00}, 2);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x3E, 0x01}, 2, 0);
    expect_single(2, (const uint8_t[]){0x7F, 0x3E, 0x12}, 3);
    single(&ecu, DIAG_FUNCTIONAL_ID, (const uint8_t[]){0x3E, 0x01}, 2, 0); /* no NRC 0x12 functionally */
    CHECK(sent_count == 3);

    /* sessions; incorrect length; unsupported service physical and functional */
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x10, 0x03}, 2, 0);
    expect_single(3, (const uint8_t[]){0x50, 0x03, 0x00, 0x32, 0x01, 0xF4}, 6);
    CHECK(ecu.session == 0x03);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x10, 0x81}, 2, 0);
    CHECK(sent_count == 4 && ecu.session == 0x01);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x10, 0x02}, 2, 0);
    expect_single(4, (const uint8_t[]){0x7F, 0x10, 0x12}, 3);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x10}, 1, 0);
    expect_single(5, (const uint8_t[]){0x7F, 0x10, 0x13}, 3);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x2E, 0xF1, 0x90}, 3, 0);
    expect_single(6, (const uint8_t[]){0x7F, 0x2E, 0x11}, 3);
    single(&ecu, DIAG_FUNCTIONAL_ID, (const uint8_t[]){0x2E, 0xF1, 0x90}, 3, 0);
    CHECK(sent_count == 7);

    /* ReadDataByIdentifier: lights state (single frame), unknown DID, length */
    uds_set_lights(&ecu, 0x02, false);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x22, 0x4C, 0x01}, 3, 0);
    expect_single(7, (const uint8_t[]){0x62, 0x4C, 0x01, 0x02, 0x00}, 5);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x22, 0x12, 0x34}, 3, 0);
    expect_single(8, (const uint8_t[]){0x7F, 0x22, 0x31}, 3);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x22, 0xF1}, 2, 0);
    expect_single(9, (const uint8_t[]){0x7F, 0x22, 0x13}, 3);

    /* segmented response (F195, 23 bytes): FF, flow control with STmin 5 ms, CFs paced */
    sent_count = 0;
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x22, 0xF1, 0x95}, 3, 100);
    CHECK(sent_count == 1 && sent[0].data[0] == 0x10 && sent[0].data[1] == 23);
    CHECK(memcmp(&sent[0].data[2], "\x62\xF1\x95THR", 6) == 0);
    CHECK(ecu.tx_state == UDS_TX_WAIT_FC);
    struct can_frame fc = frame(DIAG_REQUEST_ID, (const uint8_t[]){0x30, 0x00, 0x05}, 3);
    uds_frame(&ecu, &fc, 110);
    CHECK(sent_count == 2 && sent[1].data[0] == 0x21);
    uds_tick(&ecu, 114);
    CHECK(sent_count == 2);
    uds_tick(&ecu, 115);
    CHECK(sent_count == 3 && sent[2].data[0] == 0x22);
    uds_tick(&ecu, 120);
    CHECK(sent_count == 4 && sent[3].data[0] == 0x23);
    CHECK(ecu.tx_state == UDS_TX_IDLE);
    char text[32] = {0};
    memcpy(text, &sent[0].data[5], 3); memcpy(text + 3, &sent[1].data[1], 7);
    memcpy(text + 10, &sent[2].data[1], 7); memcpy(text + 17, &sent[3].data[1], 3);
    CHECK(strcmp(text, "THREADX-LIGHTS 1.1.0") == 0);

    /* block size 1 waits for a new flow control; WAIT extends N_Bs; N_Bs expiry aborts */
    sent_count = 0;
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x22, 0xF1, 0x95}, 3, 200);
    fc = frame(DIAG_REQUEST_ID, (const uint8_t[]){0x30, 0x01, 0x00}, 3);
    uds_frame(&ecu, &fc, 210);
    CHECK(sent_count == 2 && ecu.tx_state == UDS_TX_WAIT_FC);
    struct can_frame wait = frame(DIAG_REQUEST_ID, (const uint8_t[]){0x31, 0x00, 0x00}, 3);
    uds_frame(&ecu, &wait, 1100);
    uds_tick(&ecu, 1209);
    CHECK(ecu.tx_state == UDS_TX_WAIT_FC);
    uds_tick(&ecu, 2100);
    CHECK(ecu.tx_state == UDS_TX_IDLE && sent_count == 2);
    /* overflow aborts; a flow control without transmission is ignored */
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x22, 0xF1, 0x8C}, 3, 3000);
    struct can_frame overflow = frame(DIAG_REQUEST_ID, (const uint8_t[]){0x32, 0x00, 0x00}, 3);
    uds_frame(&ecu, &overflow, 3001);
    CHECK(ecu.tx_state == UDS_TX_IDLE);
    uds_frame(&ecu, &fc, 3002);
    CHECK(ecu.tx_state == UDS_TX_IDLE);
    /* STmin 0xF1..0xF9 (100-900 us) is rounded up to 1 ms */
    sent_count = 0;
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x22, 0xF1, 0x95}, 3, 4000);
    fc = frame(DIAG_REQUEST_ID, (const uint8_t[]){0x30, 0x00, 0xF5}, 3);
    uds_frame(&ecu, &fc, 4000);
    CHECK(ecu.tx_stmin_ms == 1 && sent_count == 2);
    uds_tick(&ecu, 4001);
    uds_tick(&ecu, 4002);
    CHECK(sent_count == 4 && ecu.tx_state == UDS_TX_IDLE);

    /* segmented request: FF + CFs with flow control; wrong sequence number aborts; N_Cr */
    sent_count = 0;
    uint8_t ff[8] = {0x10, 0x0A, 0x22, 0x12, 0x34, 0x00, 0x00, 0x00};
    f = frame(DIAG_REQUEST_ID, ff, 8);
    uds_frame(&ecu, &f, 5000);
    CHECK(sent[0].data[0] == 0x30 && sent[0].data[1] == 0x00 && sent[0].data[2] == 0x00);
    f = frame(DIAG_REQUEST_ID, (const uint8_t[]){0x21, 0x00, 0x00, 0x00, 0x00}, 5);
    uds_frame(&ecu, &f, 5005);
    expect_single(1, (const uint8_t[]){0x7F, 0x22, 0x13}, 3); /* 10-byte 0x22: wrong length */
    sent_count = 0;
    uds_frame(&ecu, &(struct can_frame){0}, 5006); /* not addressed: ignored */
    f = frame(DIAG_REQUEST_ID, ff, 8);
    uds_frame(&ecu, &f, 6000);
    f = frame(DIAG_REQUEST_ID, (const uint8_t[]){0x22, 0x00}, 2);
    uds_frame(&ecu, &f, 6001);
    CHECK(!ecu.rx_active && sent_count == 1);
    f = frame(DIAG_REQUEST_ID, ff, 8);
    uds_frame(&ecu, &f, 7000);
    uds_tick(&ecu, 8000);
    CHECK(!ecu.rx_active);
    /* too long for the buffer: overflow; first frame below 8 bytes and functional: ignored */
    sent_count = 0;
    uint8_t big[8] = {0x10, 0x41, 0x22};
    f = frame(DIAG_REQUEST_ID, big, 8);
    uds_frame(&ecu, &f, 9000);
    CHECK(sent_count == 1 && sent[0].data[0] == 0x32);
    uint8_t small[8] = {0x10, 0x07, 0x22};
    f = frame(DIAG_REQUEST_ID, small, 8);
    uds_frame(&ecu, &f, 9001);
    f = frame(DIAG_FUNCTIONAL_ID, ff, 8);
    uds_frame(&ecu, &f, 9002);
    CHECK(sent_count == 1 && !ecu.rx_active);

    /* DTC U0293: not completed after start; failed on loss; passed on recovery; clear */
    reset(&ecu);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x19, 0x0A}, 2, 0);
    expect_single(0, (const uint8_t[]){0x59, 0x0A, 0x7F, 0xC2, 0x93, 0x00, 0x50}, 7);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x19, 0x02, 0x09}, 3, 0);
    expect_single(1, (const uint8_t[]){0x59, 0x02, 0x7F}, 3);
    uds_report_vcu_lost(&ecu, true);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x19, 0x02, 0x09}, 3, 0);
    expect_single(2, (const uint8_t[]){0x59, 0x02, 0x7F, 0xC2, 0x93, 0x00, 0x2F}, 7);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x14, 0xFF, 0xFF, 0xFF}, 4, 0);
    expect_single(3, (const uint8_t[]){0x54}, 1);
    CHECK(ecu.dtc_status == 0x2F); /* still lost: detected again */
    uds_report_vcu_lost(&ecu, false);
    CHECK(ecu.dtc_status == 0x2E);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x14, 0xC2, 0x93, 0x00}, 4, 0);
    expect_single(4, (const uint8_t[]){0x54}, 1);
    CHECK(ecu.dtc_status == 0x50);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x14, 0x12, 0x34, 0x56}, 4, 0);
    expect_single(5, (const uint8_t[]){0x7F, 0x14, 0x31}, 3);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x14, 0xFF}, 2, 0);
    expect_single(6, (const uint8_t[]){0x7F, 0x14, 0x13}, 3);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x19, 0x01, 0xFF}, 3, 0);
    expect_single(7, (const uint8_t[]){0x7F, 0x19, 0x12}, 3);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x19, 0x02}, 2, 0);
    expect_single(8, (const uint8_t[]){0x7F, 0x19, 0x13}, 3);
    single(&ecu, DIAG_REQUEST_ID, (const uint8_t[]){0x19}, 1, 0);
    expect_single(9, (const uint8_t[]){0x7F, 0x19, 0x13}, 3);
    CHECK(ecu.requests == 10 && ecu.responses == 10);

    puts("UDS server: addressing, ISO-TP segmentation and flow control, services, NRCs and DTC checks passed");
    return 0;
}
