#include "diagnostic_publisher.h"
#include <cassert>
#include <chrono>
#include <cstdlib>
#include <string>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

int main() {
    const std::string path = "/tmp/sdv-sender-test-" + std::to_string(getpid()) + ".sock";
    setenv("SCORE_DIAGNOSTIC_SOCKET", path.c_str(), 1);
    sdv_diagnostics::Publisher publisher;
    const auto start = std::chrono::steady_clock::now();
    // Missing receiver must not block.
    for (int i = 0; i < 10000; ++i) publisher.Send("{}");
    assert(std::chrono::steady_clock::now() - start < std::chrono::seconds(2));
    const int receiver = socket(AF_UNIX, SOCK_DGRAM | SOCK_NONBLOCK, 0);
    assert(receiver >= 0);
    sockaddr_un address{}; address.sun_family = AF_UNIX;
    std::copy(path.begin(), path.end(), address.sun_path);
    assert(bind(receiver, reinterpret_cast<sockaddr*>(&address), sizeof(address)) == 0);
    publisher.Send("{\"value\":42}");
    char bytes[256]{};
    const auto size = recv(receiver, bytes, sizeof(bytes), 0);
    assert(size > 0 && std::string(bytes, size) == "{\"value\":42}");
    // Fill the queue then keep sending: it must drop rather than block.
    for (int i = 0; i < 10000; ++i) publisher.Send("{}");
    assert(std::chrono::steady_clock::now() - start < std::chrono::seconds(2));
    close(receiver); unlink(path.c_str());
    return 0;
}
