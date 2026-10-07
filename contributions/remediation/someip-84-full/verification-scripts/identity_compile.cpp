#include "score/socom/service_interface_identifier.hpp"
#include <array>
#include <unordered_set>
void check_api() {
    using namespace score::socom;
    Service_interface const configuration{std::string_view{"service"}, {1U, 2U}};
    Service_interface_identifier const identity{std::string_view{"service"}, 1U};
    Service_instance_identifier const offer{identity, 2U, Service_instance{std::string_view{"instance"}}};
    Find_service_request const request{identity, 2U, std::nullopt};
    std::unordered_set<Service_interface_identifier> services{configuration.get_identifier()};
    std::unordered_set<Service_instance_identifier> instances{offer};
    (void)request.matches(offer);
    (void)services;
    (void)instances;
}
