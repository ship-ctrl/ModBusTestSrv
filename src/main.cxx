#include <iostream>
#include <glog/logging.h>
#include <gflags/gflags.h>

// Define command-line flags using gflags
DEFINE_string(config, "default.conf", "Path to configuration file");
DEFINE_int32(port, 8080, "Server port number");
DEFINE_bool(verbose, false, "Enable verbose logging");
DEFINE_double(threshold, 0.5, "Score threshold");

// Validate flag values
static bool ValidatePort(const char* flagname, int32_t value) {
    if (value > 0 && value < 65536) return true;
    std::cout << "Invalid value for --" << flagname << ": " << value << std::endl;
    return false;
}
DEFINE_validator(port, &ValidatePort);

int main(int argc, char* argv[]) {
    // Initialize gflags
    gflags::ParseCommandLineFlags(&argc, &argv, true);
    
    // Initialize glog
    google::InitGoogleLogging(argv[0]);
    
    // Set log directory (logs will be written to /tmp)
    FLAGS_log_dir = "/tmp";
    
    // Set log level based on verbose flag
    if (FLAGS_verbose) {
        FLAGS_minloglevel = 0;  // INFO level
    } else {
        FLAGS_minloglevel = 1;  // WARNING level
    }
    
    // Log messages at different severity levels
    LOG(INFO) << "Application starting...";
    LOG(INFO) << "Using config file: " << FLAGS_config;
    LOG(INFO) << "Server port: " << FLAGS_port;
    LOG(INFO) << "Threshold: " << FLAGS_threshold;
    
    // Conditional logging
    VLOG(1) << "Verbose log message 1";
    VLOG(2) << "Verbose log message 2";
    
    // Log every N times
    for (int i = 0; i < 100; ++i) {
        LOG_EVERY_N(INFO, 20) << "Log every 20 iterations. i = " << i;
    }
    
    // Check and log
    CHECK(FLAGS_port > 1024) << "Port should be above 1024 for non-root users";
    
    // DLOG for debug mode only (removed in non-debug builds)
    DLOG(INFO) << "This is debug-only log";
    
    // Simulate some work
    try {
        LOG(WARNING) << "This is a warning message";
        
        if (FLAGS_threshold > 0.8) {
            LOG(ERROR) << "Threshold is too high!";
        } else {
            LOG(INFO) << "Threshold is acceptable";
        }
        
        // Fatal error example (commented out to prevent crash)
        // LOG(FATAL) << "Fatal error occurred!";
        
    } catch (const std::exception& e) {
        LOG(ERROR) << "Exception caught: " << e.what();
    }
    
    LOG(INFO) << "Application shutting down...";
    
    // Shutdown glog
    google::ShutdownGoogleLogging();
    
    return 0;
}