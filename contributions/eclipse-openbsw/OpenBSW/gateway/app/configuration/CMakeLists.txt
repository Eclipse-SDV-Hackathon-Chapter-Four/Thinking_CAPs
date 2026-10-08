add_library(configuration common/src/busid/BusId.cpp)

target_include_directories(configuration PUBLIC include)

target_link_libraries(configuration PUBLIC common async)

# python -m blob binary -i routing.jsonl -c blob.routing.table | python -m blob
# header data -n CONFIGURATION_BLOB > include/blob/configuration.h

# python -m blob.routing header ${BLOB_INPUT_FILE} > include/routing/channelId.h

# python -m blob header config-type > include/blob/ConfigType.h
target_include_directories(blobConfiguration INTERFACE include)
target_include_directories(routingConfiguration INTERFACE include)

# gateway: LOGICAL_ADDRESS comes from the generated routing config
target_include_directories(configuration PUBLIC ${CMAKE_BINARY_DIR}/generated
                                                ${CMAKE_SOURCE_DIR}/lib/include)
add_dependencies(configuration gatewayRoutingConfig)
