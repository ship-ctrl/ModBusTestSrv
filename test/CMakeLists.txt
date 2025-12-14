cmake_minimum_required(VERSION 3.20)
project(tests)

include(Exclusions)
include(FetchContent)
# Enable testing
enable_testing()

# Configuration options
option(TEST_SOURCE_DIR "Directory containing test files" ".")
option(ENABLE_EXCLUSIONS "Enable file name exclusions" ON)


set(TEST_DIR ${TEST_SOURCE_DIR})
set(TEST_EXTENSIONS "cxx;c;cpp" CACHE STRING "File extensions to treat as tests")
#message(STATUS "testdir ${TEST_DIR}")

#option(EXCLUDE_TESTS "Tests by source files" 
#    "main"           # Exclude files named main.cpp, main.c, etc.
#    "utils"          # Exclude utils.cpp
#    "common"         # Exclude common.cpp
#    )

# Configure file exclusions (modify this list as needed)
set(EXCLUDED_FILES
    #${EXCLUDE_TESTS}
    "main"           # Exclude files named main.cpp, main.c, etc.
    "utils"          # Exclude utils.cpp
    "common"         # Exclude common.cpp
    # Add more patterns here
    CACHE STRING "File name patterns to exclude (without extension)"
)

option(EXCLUDE_FILES "Tests by source files" "")

# Alternative: Exclude by full filename
set(EXCLUDED_FULLNAMES
    ${EXCLUDE_FILES}
    CACHE STRING "Full file names to exclude (with extension)"
)

# Set the C++ standard to be used
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS_DEBUG_INIT "-Wall -g -O0")
set(CMAKE_CXX_FLAGS_RELEASE_INIT "-Wall -O3 -flto")

#find_package (Boost COMPONENTS unit_test_framework REQUIRED CONFIG)
if(Boost_FOUND)
        message ("Boost found")
    else()
        #message (FATAL_ERROR "Cannot find Boost")
        FetchContent_Declare(
            boost
            GIT_REPOSITORY https://github.com/boostorg/boost.git
            #GIT_TAG boost-1.85.0
        )
        FetchContent_MakeAvailable(boost)
endif(Boost_FOUND)
#find_package (yaml-cpp  REQUIRED CONFIG)

include_directories(${CMAKE_SOURCE_DIR})

# Find all source files
set(ALL_SOURCE_FILES "")
foreach(ext ${TEST_EXTENSIONS})
    file(GLOB files "*.${ext}")
    #get_filename_component(filename ${files} NAME)
    list(APPEND ALL_SOURCE_FILES "${files}")
endforeach()

#message(STATUS "list ${ALL_SOURCE_FILES}")

# Process each source file
set(CREATED_TESTS "")
foreach(source_file ${ALL_SOURCE_FILES})
    get_filename_component(filename ${source_file} NAME)

    # Check if file should be excluded
    if(ENABLE_EXCLUSIONS)
        should_exclude_file(${source_file} IS_EXCLUDED)
        if(IS_EXCLUDED)
            message(STATUS "Excluding: ${filename}")
            continue()
        endif()
    endif()
    
    # Create test target
    get_filename_component(test_name ${source_file} NAME_WE)
    add_executable(${test_name} ${source_file})
    target_link_libraries(${test_name}
        PUBLIC ${Boost_LIBRARIES}
        # LINK extra libs here
        )
    add_test(NAME ${test_name}
             COMMAND ${test_name}
             WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
    
    list(APPEND CREATED_TESTS ${test_name})
    message(STATUS "Created test: ${test_name}")
endforeach()

# Summary
message(STATUS "Total files found: ${ALL_SOURCE_FILES}")
message(STATUS "Tests created: ${CREATED_TESTS}")

if(NOT CREATED_TESTS)
    message(WARNING "No tests were created!")
endif()


# script based test examples
# add_test(testTkInter "/usr/bin/python" "-c" "import Tkinter")

# Add post-build command to the target
# TODO find list targets add here
add_custom_command(TARGET ${CREATED_TESTS} POST_BUILD
    COMMAND ${CMAKE_COMMAND} 
        -DACT=1
        -DDIR=${CMAKE_SOURCE_DIR}
        -P ${CMAKE_SOURCE_DIR}/cmake/AutoVersion.cmake
    COMMENT "Updating build information..."
    VERBATIM
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)


