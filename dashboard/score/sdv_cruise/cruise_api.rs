// SPDX-License-Identifier: Apache-2.0
//! Rust side of the mw::com interfaces in `cruise_types.h`, plus the SOME/IP
//! payload layout they carry (see the header for the byte table).

use score_com::{interface, CommData, ProviderInfo, Publisher, Reloc, Subscriber};

/// `PreSerializedData<16>`: size, then the payload aligned to 16.
#[repr(C, align(16))]
#[derive(Clone, Copy, Debug, Default, Reloc, CommData)]
#[comm_data(id = "CruiseStatusSample")]
pub struct CruiseStatusSample {
    pub size: usize,
    _pad: u64,
    pub data: [u8; 16],
}

/// `PreSerializedData<8>`.
#[repr(C, align(16))]
#[derive(Clone, Copy, Debug, Default, Reloc, CommData)]
#[comm_data(id = "InjectFaultSample")]
pub struct InjectFaultSample {
    pub size: usize,
    _pad: u64,
    pub data: [u8; 8],
}

interface!(
    interface SdvCruiseStatus {
        Id = "SdvCruiseStatus",
        cruise_status_: Event<CruiseStatusSample>,
    }
);

interface!(
    interface SdvDiagInjection {
        Id = "SdvDiagInjection",
        inject_fault_: Event<InjectFaultSample>,
    }
);

/// Cruise control state as sent on the wire.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum State {
    Standby,
    Active,
    Unavailable,
}

impl State {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Standby => "standby",
            Self::Active => "active",
            Self::Unavailable => "unavailable",
        }
    }
}

/// Decoded `cruise_status` payload.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CruiseStatus {
    pub speed_kmh: f32,
    pub set_speed_kmh: Option<f32>,
    pub state: State,
}

pub const CRUISE_STATUS_BYTES: usize = 12;

impl CruiseStatus {
    /// Decodes the 12-byte big-endian SOME/IP payload.
    pub fn decode(payload: &[u8]) -> Option<Self> {
        if payload.len() < CRUISE_STATUS_BYTES {
            return None;
        }
        let f = |i: usize| f32::from_be_bytes([payload[i], payload[i + 1], payload[i + 2], payload[i + 3]]);
        let state = match payload[8] {
            0 => State::Standby,
            1 => State::Active,
            2 => State::Unavailable,
            _ => return None,
        };
        Some(Self {
            speed_kmh: f(0),
            set_speed_kmh: (payload[9] & 1 == 1).then(|| f(4)),
            state,
        })
    }
}

impl CruiseStatusSample {
    pub fn payload(&self) -> &[u8] {
        &self.data[..self.size.min(self.data.len())]
    }
}

impl InjectFaultSample {
    pub fn new(stuck: bool) -> Self {
        let mut data = [0u8; 8];
        data[0] = u8::from(stuck);
        Self { size: 1, _pad: 0, data }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn layout_matches_pre_serialized_data() {
        assert_eq!(core::mem::size_of::<CruiseStatusSample>(), 32);
        assert_eq!(core::mem::align_of::<CruiseStatusSample>(), 16);
        assert_eq!(core::mem::size_of::<InjectFaultSample>(), 32);
        assert_eq!(core::mem::align_of::<InjectFaultSample>(), 16);
        // C++ aligns `data` to alignof(std::max_align_t) = 16.
        assert_eq!(core::mem::offset_of!(CruiseStatusSample, data), 16);
        assert_eq!(core::mem::offset_of!(InjectFaultSample, data), 16);
    }

    #[test]
    fn decodes_the_wire_format() {
        let mut p = [0u8; 12];
        p[0..4].copy_from_slice(&99.5f32.to_be_bytes());
        p[4..8].copy_from_slice(&100.0f32.to_be_bytes());
        p[8] = 1;
        p[9] = 1;
        let s = CruiseStatus::decode(&p).unwrap();
        assert_eq!(s.state, State::Active);
        assert_eq!(s.speed_kmh, 99.5);
        assert_eq!(s.set_speed_kmh, Some(100.0));
        p[8] = 9;
        assert!(CruiseStatus::decode(&p).is_none());
    }
}
