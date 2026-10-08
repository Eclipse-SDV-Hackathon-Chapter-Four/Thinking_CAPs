add_library(transportConfiguration src/transport/TransportConfiguration.cpp)

target_include_directories(transportConfiguration PUBLIC include)

target_link_libraries(transportConfiguration PUBLIC transport etl configuration)

# gateway: functional address and tester range come from the generated routing config
target_include_directories(transportConfiguration PUBLIC ${CMAKE_BINARY_DIR}/generated
                                                         ${CMAKE_SOURCE_DIR}/lib/include)
add_dependencies(transportConfiguration gatewayRoutingConfig)
