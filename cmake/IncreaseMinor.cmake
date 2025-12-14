set(AV_VERSION "0.1.0")

# Simple build success handler
#string(TIMESTAMP NOW)

# Include the module
#temp solution is to step some backwards to dir
list(APPEND CMAKE_MODULE_PATH "${DIR}/cmake")
include(AutoVersion)

increment_and_save_min_ver(${DIR})
