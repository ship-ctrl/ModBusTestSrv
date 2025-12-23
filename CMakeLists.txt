cmake_minimum_required(VERSION 3.22) # feel free to downgrade on build errors but it's better be 3.22
project(ModbusTestSrv VERSION 0.1 DESCRIPTION "A CMake driven tests 4 LL code" LANGUAGES CXX C HOMEPAGE_URL "https://github.com/ship-ctrl/ModBusTestSrv")

cmake_policy(SET CMP0156 NEW) #deduplicate lib
cmake_policy(SET CMP0179 NEW) #use first occurrence

# Include the module
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(AutoVersion)
include(FetchContent)

# Set the C++ standard to be used
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS_DEBUG_INIT "-Wall -g -O0")
set(CMAKE_CXX_FLAGS_RELEASE_INIT "-Wall -O3 -flto")

set(VERSION_FILE "${CMAKE_SOURCE_DIR}/version_info.txt")

# Increment build number each time CMake runs
increment_and_save_build(${CMAKE_SOURCE_DIR})

# Read back the updated values for use in CMake
read_version_from_file(${CMAKE_SOURCE_DIR})

option(RUNNER_FETCH_ALL "fetching deps via fetchcontent" OFF)
option(INCLUDE_GLOG "fetch glog and link to main target" OFF)
option(INCLUDE_GFLAGS "fetch gflags and link to main target" OFF)

# Choose one method to provide both glog and gflags: either FetchContent or find_package

option(FORCE_FETCH_DEPS "Force fetching dependencies (gflags/glog) via FetchContent" OFF)

if(FORCE_FETCH_DEPS)
    # FetchContent for both gflags and glog
    FetchContent_Declare(
        gflags
        GIT_REPOSITORY https://github.com/gflags/gflags.git
        GIT_TAG main
    )
    FetchContent_Declare(
        glog
        GIT_REPOSITORY https://github.com/google/glog.git
        # GIT_TAG v0.6.0
    )
    set(BUILD_SHARED_LIBS ON CACHE BOOL "Build shared libraries" FORCE)
    set(WITH_GFLAGS OFF CACHE BOOL "Build with gflags")  # Or ON if glog needs it
    set(WITH_UNWIND OFF CACHE BOOL "Build with unwind support")
    FetchContent_MakeAvailable(gflags glog)
else()
    find_package(gflags REQUIRED)
    find_package(glog REQUIRED)
endif()

configure_file( 
    ${CMAKE_SOURCE_DIR}/Version.h.in 
    ${CMAKE_SOURCE_DIR}/Version.h
    )

#find_package(Threads REQUIRED)

option(BUILD_TEST_lo "Build the testing tree" OFF)
option(INCLUDE_BOOST "fetch boost and link to main target" OFF)

if(BUILD_TEST_lo)
    if(INCLUDE_BOOST OR RUNNER_FETCH_ALL)
        FetchContent_Declare(
            Boost
            GIT_REPOSITORY https://github.com/boostorg/boost.git
            #GIT_TAG boost-1.85.0
        )
        FetchContent_MakeAvailable(Boost)
    else()
        message (STATUS "Boost found or RUNNER_FETCH_ALL = ${RUNNER_FETCH_ALL}")
        find_package (Boost COMPONENTS unit_test_framework REQUIRED CONFIG)
    endif(INCLUDE_BOOST OR RUNNER_FETCH_ALL)
    
    enable_testing()
    if(EXISTS "${CMAKE_SOURCE_DIR}/test/CMakeLists.txt")
        add_subdirectory(test)
    endif()
    if(Boost_FOUND)
        message ("Boost found")
    else()
        #message (FATAL_ERROR "Cannot find Boost")
    endif(Boost_FOUND)
endif(BUILD_TEST_lo)

message(STATUS "==========================================")
message(STATUS "Project: ${PROJECT_NAME}")
message(STATUS "Version: ${FULL_VERSION}")
message(STATUS "Build Number: ${BUILD_NUMBER}")
message(STATUS "Minor Version: ${MINOR_VERSION}")
message(STATUS "==========================================")

## find_package(catkin REQUIRED COMPONENTS
##  roscpp
##  std_msgs
##  hydro_msgs
##  realtime_tools
## )

include_directories(
  #${catkin_INCLUDE_DIRS}
  ${Boost_INCLUDE_DIR}
  /usr/include
  /usr/include/modbus
)
if(Enable_Licensing)
    add_subdirectory(Silencer_CLASS) # make it git and auto downloadble
    list(APPEND licLib "silencer")
endif(Enable_Licensing)

#list(APPEND EXTRA_INCLUDES "/usr/include/modbus/modbus.h")

#list(APPEND Mbus_INCLUDES "ModbusRTU.hpp")
#list(APPEND Mbus_INCLUDES "Pump.hpp")
#list(APPEND Mbus_INCLUDES "ModbusSlave.hpp")
#list(APPEND Mbus_INCLUDES "alphafilter.hpp")

if(NOT TESTONLY)
    add_executable(example 
        ./src/example.cxx 
        ${Mbus_INCLUDES} 
        ${YAML_CPP_LIBRARIES} 
        ${EXTRA_INCLUDES}
        )

    target_link_libraries( example
        glog::glog 
        gflags
        #PRIVATE libmodbus.so 
        ${licLib} 
        ${catkin_LIBRARIES}
    )

    add_library(libDumbMserver 
        ./src/DumbMlib.cxx
        ./src/DumbModbus.hpp
        
        ${EXTRA_INCLUDES}
        )

    add_executable(DumbMserver 
        src/DumbMsrv.cxx
        src/DumbModbus.hpp
        ${EXTRA_INCLUDES}
        )

target_link_libraries(libDumbMserver PUBLIC libmodbus.so)
target_link_libraries(DumbMserver PUBLIC libmodbus.so glog::glog gflags)

    # Add post-build command to the target
    add_custom_command(TARGET example POST_BUILD
        COMMAND ${CMAKE_COMMAND} 
        -DDIR=${CMAKE_SOURCE_DIR}
        -P ${CMAKE_SOURCE_DIR}/cmake/IncreaseMinor.cmake
        COMMENT "Updating build information..."
        VERBATIM
    )
endif(NOT TESTONLY)


