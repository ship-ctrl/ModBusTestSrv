
#include "DumbModbus.hpp"

#include <glog/logging.h>
#include <gflags/gflags.h>

// Validate flag values
static bool ValidatePort(const char* flagname, int32_t value) {
    if (value > 0 && value < 65536) return true;
    std::cout << "Invalid value for --" << flagname << ": " << value << std::endl;
    return false;
}
DEFINE_validator(port, &ValidatePort);

int main(char argc,char* argv)
{
    gflags::ParseCommandLineFlags(&argc, &argv, true);

    // Initialize glog
    google::InitGoogleLogging(argv[0]);

    LOG(INFO) << "Server starting...";
    dumb_Mserver srv;
    srv.ezTreadstart();

    return 0;
}