// SPDX-License-Identifier: Apache-2.0
//
// cruise_ecu: stand-in for the other team's cruise control app, a plain
// SOME/IP application (COVESA vsomeip) on its own ECU. Link ⑥.
//
//   offers   0x4300.0001  event 0x8001 cruise_status (eventgroup 0x8001), every 100 ms
//   consumes 0x4301.0001  event 0x8001 inject_fault  (eventgroup 0x8001), from the vehicle computer
//
// Behaviour is our assumption, to confirm with the other team (same as demo/gateway/crates/cruise_sim):
// holds 100 km/h; while inject_fault is 1 the speed signal freezes; after FAULT_MS of frozen
// signal the cruise control becomes unavailable; after release it waits in standby and the
// simulated driver resumes it RESUME_MS later (0 = never).
//
// Environment: VSOMEIP_CONFIGURATION (required), CRUISE_ECU_FAULT_MS=5000,
// CRUISE_ECU_RESUME_MS=3000, CRUISE_ECU_STATS=<file> (JSON, rewritten every 500 ms).

#include <vsomeip/vsomeip.hpp>

#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>

namespace {

constexpr vsomeip::service_t kStatusService = 0x4300;
constexpr vsomeip::service_t kInjectionService = 0x4301;
constexpr vsomeip::instance_t kInstance = 0x0001;
constexpr vsomeip::event_t kEvent = 0x8001;
constexpr vsomeip::eventgroup_t kGroup = 0x8001;
constexpr double kSetSpeed = 100.0;
constexpr vsomeip::major_version_t kMajor = 1;  // interface version, must match the vehicle side

using Clock = std::chrono::steady_clock;

long env_ms(const char* name, long fallback) {
    const char* v = std::getenv(name);
    return v != nullptr ? std::atol(v) : fallback;
}

enum class State : std::uint8_t { Standby = 0, Active = 1, Unavailable = 2 };

const char* name(State s) {
    switch (s) {
        case State::Standby: return "standby";
        case State::Active: return "active";
        case State::Unavailable: return "unavailable";
    }
    return "?";
}

// Same state machine as cruise_sim::App.
class App {
   public:
    App(Clock::duration fault_detect, Clock::duration resume_after)
        : started_{Clock::now()}, fault_detect_{fault_detect}, resume_after_{resume_after} {}

    struct Status {
        float speed;
        State state;
        bool set_valid;
    };

    Status step(bool inject, Clock::time_point now) {
        if (inject && !inject_since_) {
            frozen_at_ = live_speed(now);
            inject_since_ = true;
            inject_at_ = now;
        } else if (!inject && inject_since_) {
            inject_since_ = false;
            if (state_ == State::Unavailable) {
                state_ = State::Standby;
                standby_at_ = now;
                standby_ = true;
            }
        }
        if (inject_since_ && now - inject_at_ >= fault_detect_) state_ = State::Unavailable;
        if (standby_ && resume_after_.count() > 0 && now - standby_at_ >= resume_after_) {
            state_ = State::Active;
            standby_ = false;
        }
        return {static_cast<float>(inject_since_ ? frozen_at_ : live_speed(now)), state_,
                state_ == State::Active};
    }

   private:
    double live_speed(Clock::time_point now) const {
        const double t = std::chrono::duration<double>(now - started_).count();
        return std::round((kSetSpeed + 0.4 * std::sin(t * 0.7)) * 10.0) / 10.0;
    }

    Clock::time_point started_;
    Clock::duration fault_detect_, resume_after_;
    State state_{State::Active};
    double frozen_at_{0};
    bool inject_since_{false};
    Clock::time_point inject_at_{};
    bool standby_{false};
    Clock::time_point standby_at_{};
};

void put_be_float(vsomeip::byte_t* p, float v) {
    std::uint32_t u;
    std::memcpy(&u, &v, sizeof u);
    p[0] = static_cast<vsomeip::byte_t>(u >> 24);
    p[1] = static_cast<vsomeip::byte_t>(u >> 16);
    p[2] = static_cast<vsomeip::byte_t>(u >> 8);
    p[3] = static_cast<vsomeip::byte_t>(u);
}

}  // namespace

int main() {
    auto rt = vsomeip::runtime::get();
    auto app = rt->create_application("cruise_ecu");
    if (!app->init()) {
        std::cerr << "[cruise_ecu] vsomeip init failed (VSOMEIP_CONFIGURATION?)\n";
        return 1;
    }

    std::atomic<bool> inject{false};
    std::atomic<std::uint64_t> injects_received{0}, notifications{0};
    std::atomic<bool> injection_available{false};

    app->register_state_handler([&](vsomeip::state_type_e st) {
        if (st != vsomeip::state_type_e::ST_REGISTERED) return;
        app->offer_event(kStatusService, kInstance, kEvent, {kGroup},
                         vsomeip::event_type_e::ET_EVENT, std::chrono::milliseconds::zero(), false,
                         true, nullptr, vsomeip::reliability_type_e::RT_UNRELIABLE);
        app->offer_service(kStatusService, kInstance, kMajor, 0);
        app->request_event(kInjectionService, kInstance, kEvent, {kGroup},
                           vsomeip::event_type_e::ET_EVENT, vsomeip::reliability_type_e::RT_UNRELIABLE);
        app->request_service(kInjectionService, kInstance, kMajor);
        std::cout << "[cruise_ecu] registered: offering 0x4300 cruise_status, requesting 0x4301 inject_fault"
                  << std::endl;
    });
    app->register_availability_handler(kInjectionService, kInstance,
                                       [&](vsomeip::service_t, vsomeip::instance_t, bool up) {
                                           injection_available = up;
                                           std::cout << "[cruise_ecu] 0x4301 inject_fault service "
                                                     << (up ? "available" : "gone") << std::endl;
                                           if (up) app->subscribe(kInjectionService, kInstance, kGroup, kMajor);
                                       });
    app->register_message_handler(kInjectionService, kInstance, kEvent,
                                  [&](const std::shared_ptr<vsomeip::message>& msg) {
                                      auto pl = msg->get_payload();
                                      if (pl->get_length() < 1) return;
                                      const bool v = pl->get_data()[0] != 0;
                                      injects_received++;
                                      if (inject.exchange(v) != v)
                                          std::cout << "[cruise_ecu] inject_fault = " << v << std::endl;
                                  });

    std::thread io([&] { app->start(); });

    App cruise{std::chrono::milliseconds(env_ms("CRUISE_ECU_FAULT_MS", 5000)),
               std::chrono::milliseconds(env_ms("CRUISE_ECU_RESUME_MS", 3000))};
    const char* stats_path = std::getenv("CRUISE_ECU_STATS");
    State last = State::Active;
    auto last_stats = Clock::now();
    for (;;) {
        const auto now = Clock::now();
        const auto s = cruise.step(inject.load(), now);
        if (s.state != last) {
            std::cout << "[cruise_ecu] state " << name(last) << " -> " << name(s.state) << std::endl;
            last = s.state;
        }
        vsomeip::byte_t buf[12]{};
        put_be_float(buf, s.speed);
        put_be_float(buf + 4, s.set_valid ? static_cast<float>(kSetSpeed) : 0.0F);
        buf[8] = static_cast<vsomeip::byte_t>(s.state);
        buf[9] = s.set_valid ? 1 : 0;
        auto payload = rt->create_payload();
        payload->set_data(buf, sizeof buf);
        app->notify(kStatusService, kInstance, kEvent, payload, true);
        notifications++;

        if (stats_path != nullptr && now - last_stats >= std::chrono::milliseconds(500)) {
            last_stats = now;
            char json[320];
            std::snprintf(json, sizeof json,
                          "{\"speed\":%.1f,\"state\":\"%s\",\"inject\":%s,\"notifications_sent\":%llu,"
                          "\"injects_received\":%llu,\"injection_service\":%s}",
                          s.speed, name(s.state), inject.load() ? "true" : "false",
                          static_cast<unsigned long long>(notifications.load()),
                          static_cast<unsigned long long>(injects_received.load()),
                          injection_available.load() ? "true" : "false");
            const std::string tmp = std::string(stats_path) + ".tmp";
            {
                std::ofstream f(tmp);
                f << json;
            }
            std::rename(tmp.c_str(), stats_path);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}
