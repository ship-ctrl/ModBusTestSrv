set(AV_VERSION "0.1.0")

# Simple build success handler
string(TIMESTAMP NOW)

# Function to read version from file
function(read_version_from_file dir)
    if(EXISTS ${VERSION_FILE})
        file(STRINGS ${VERSION_FILE} VERSION_LINES)
        foreach(LINE ${VERSION_LINES})
            if(LINE MATCHES "^BUILD_NUMBER=([0-9]+)$")
                set(BUILD_NUMBER ${CMAKE_MATCH_1} PARENT_SCOPE)
            elseif(LINE MATCHES "^MINOR_VERSION=([0-9]+)$")
                set(MINOR_VERSION ${CMAKE_MATCH_1} PARENT_SCOPE)
            endif()
        endforeach()
    else()
        # Initialize if file doesn't exist
        set(BUILD_NUMBER 0 PARENT_SCOPE)
        set(MINOR_VERSION 0 PARENT_SCOPE)
    endif()
endfunction()

# Function to increment and save BUILD_NUMBER
function(increment_and_save_build dir)
    # Read current values
    read_version_from_file(${dir})
    
    if(NOT BUILD_NUMBER)
        set(BUILD_NUMBER 0)
    endif()
    if(NOT MINOR_VERSION)
        set(MINOR_VERSION 0)
    endif()
    
    # Increment values
    math(EXPR NEW_BUILD_NUMBER "${BUILD_NUMBER} + 1")
    #math(EXPR NEW_MINOR_VERSION "${MINOR_VERSION} + 1")
    
    # Write to file
    file(WRITE ${VERSION_FILE}
        "BUILD_NUMBER=${NEW_BUILD_NUMBER}\n"
        "MINOR_VERSION=${MINOR_VERSION}\n"  # Note: We only increment build number on each run
        "LAST_BUILD=${CMAKE_SYSTEM_NAME} ${CMAKE_SYSTEM_PROCESSOR}\n"
        "TIMESTAMP=${NOW}\n"
    )
    
    # Make values available globally
    set(BUILD_NUMBER ${NEW_BUILD_NUMBER} PARENT_SCOPE)
    set(MINOR_VERSION ${MINOR_VERSION} PARENT_SCOPE)  # Unchanged minor version
    message(STATUS "Incremented build number to: ${NEW_BUILD_NUMBER}")
endfunction()

# Function to increment and save MINOR_VERSION
function(increment_and_save_min_ver dir)
    # Read current values
    read_version_from_file(${dir})
    
    if(NOT BUILD_NUMBER)
        set(BUILD_NUMBER 0)
    endif()
    if(NOT MINOR_VERSION)
        set(MINOR_VERSION 0)
    endif()
    
    # Increment values
    #math(EXPR NEW_BUILD_NUMBER "${BUILD_NUMBER} + 1")
    math(EXPR NEW_MINOR_VERSION "${MINOR_VERSION} + 1")
    #message("see ${VERSION_FILE}")
    # Write to file
    file(WRITE ${VERSION_FILE}
        "BUILD_NUMBER=${BUILD_NUMBER}\n"
        "MINOR_VERSION=${NEW_MINOR_VERSION}\n"  # Note: We only increment build number on each run
        "LAST_BUILD=${CMAKE_SYSTEM_NAME} ${CMAKE_SYSTEM_PROCESSOR}\n"
        "TIMESTAMP=${NOW}\n"
    )
    
    # Make values available globally
    set(BUILD_NUMBER ${NEW_BUILD_NUMBER} PARENT_SCOPE)
    set(MINOR_VERSION ${MINOR_VERSION} PARENT_SCOPE)  # Unchanged minor version
    message(STATUS "Incremented MINOR_VERSION number to: ${NEW_MINOR_VERSION}")
endfunction()

if(ACT)
    set(VERSION_FILE "${CMAKE_SOURCE_DIR}/version_info.txt")
    increment_and_save_min_ver(${DIR})
endif(ACT)

# usage example for minor version
# # Add post-build command to the target
# add_custom_command(TARGET test1 test2 POST_BUILD
#     COMMAND ${CMAKE_COMMAND} 
#         -DACT=1
#         -DDIR=${CMAKE_SOURCE_DIR}
#         -P ${CMAKE_SOURCE_DIR}/cmake/AutoVersion.cmake
#     COMMENT "Updating build information..."
#     VERBATIM
#     WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
# )