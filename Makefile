# Default target - builds both libraries
.PHONY: all
all: check-deps  gflags glog libmodbus

mkfile_path := $(PWD)
# Directories
GLOG_DIR ?= glog
GLOG_BUILD_DIR = build/$(GLOG_DIR)

MODBUS_DIR ?= libmodbus
MODBUS_BUILD_DIR = build/$(MODBUS_DIR)

GFLAGS_DIR ?= gflags
GFLAGS_BUILD_DIR = build/$(GFLAGS_DIR)

mkfile_path := $(PWD)
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))

# Add both submodules
.PHONY: submodules
submodules: glog-submodule gflags-submodule modbus-submodule update-submodules

# GLOG submodule
.PHONY: glog-submodule
glog-submodule:
	@if [ ! -f "$(GLOG_DIR)/CMakeLists.txt" ]; then \
		echo "Adding glog submodule..."; \
		git submodule add https://github.com/google/glog.git $(GLOG_DIR); \
	else \
		echo "Glog submodule already exists"; \
	fi
	@if [ ! -f "$(GLOG_DIR)/CMakeLists.txt" ]; then \
		git submodule update --init --recursive $(GLOG_DIR); \
	fi

# LIBMODBUS submodule
.PHONY: modbus-submodule
modbus-submodule:
	@if [ ! -d "$(MODBUS_DIR)/.git" ]; then \
		echo "Adding libmodbus submodule..."; \
		git submodule add https://github.com/stephane/libmodbus.git $(MODBUS_DIR); \
	else \
		echo "Libmodbus submodule already exists"; \
	fi
	@if [ ! -f "$(MODBUS_DIR)/configure.ac" ]; then \
		git submodule update --init --recursive $(MODBUS_DIR); \
	fi

# Update all submodules
.PHONY: update-submodules
update-submodules:
	@echo "Updating all submodules..."
	git submodule update --remote --merge --recursive

glog-configure: glog-submodule
	@echo "Configure glog to $(GLOG_BUILD_DIR) ..."
	@cd $(mkfile_path) 
	@mkdir -p $(GLOG_BUILD_DIR)
	cd $(GLOG_DIR)  && \
	cmake .. --trace \
		-G "Unix Makefiles" \
		-B $(GLOG_BUILD_DIR) \
		-DCMAKE_BUILD_TYPE=Release \
		-DBUILD_SHARED_LIBS=ON 

# Build and install glog (CMake-based)
.PHONY: glog
glog: glog-submodule glog-configure
	@echo "Building and installing glog..."
	cd $(mkfile_path) 
	cd $(GLOG_BUILD_DIR) && $(MAKE) -j$(shell nproc 2>/dev/null || echo 4)
	cd $(GLOG_BUILD_DIR) && sudo $(MAKE) install
	@echo "Glog installed successfully"

# Build and install libmodbus (autoconf-based)
.PHONY: libmodbus
libmodbus: modbus-submodule
	@echo "Building and installing libmodbus..."
	@cd $(mkfile_path) 
	cd $(MODBUS_DIR) && \
	autoreconf -f -i 2>/dev/null || autoreconf -i
	@mkdir -p $(MODBUS_BUILD_DIR)
	cd $(MODBUS_BUILD_DIR) && \
	../../libmodbus/configure \
		--prefix=/usr/local \
		--enable-shared \
		--disable-static
	cd $(MODBUS_BUILD_DIR) && $(MAKE) -j$(shell nproc 2>/dev/null || echo 4)
	cd $(MODBUS_BUILD_DIR) && sudo $(MAKE) install
	@echo "Libmodbus installed successfully"

# Local installations (no sudo required)

.PHONY: glog-local
glog-local: glog-submodule
	@echo "Building and installing glog locally..."
	@mkdir -p $(GLOG_BUILD_DIR)
	cd $(GLOG_BUILD_DIR) && \
	cmake .. \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_INSTALL_PREFIX=$$(pwd)/install \
		-DBUILD_SHARED_LIBS=ON \
		-DWITH_GFLAGS=OFF \
		-DWITH_UNWIND=ON
	cd $(GLOG_BUILD_DIR) && $(MAKE) -j$(shell nproc 2>/dev/null || echo 4)
	cd $(GLOG_BUILD_DIR) && $(MAKE) install
	@echo "Glog installed to: $(GLOG_BUILD_DIR)/install"

.PHONY: libmodbus-local
libmodbus-local: modbus-submodule
	@echo "Building and installing libmodbus locally..."
	cd $(MODBUS_DIR) && \
	autoreconf -f -i 2>/dev/null || autoreconf -i
	@mkdir -p $(MODBUS_BUILD_DIR)
	cd $(MODBUS_BUILD_DIR) && \
	../configure \
		--prefix=$$(pwd)/install \
		--enable-shared \
		--disable-static
	cd $(MODBUS_BUILD_DIR) && $(MAKE) -j$(shell nproc 2>/dev/null || echo 4)
	cd $(MODBUS_BUILD_DIR) && $(MAKE) install
	@echo "Libmodbus installed to: $(MODBUS_BUILD_DIR)/install"

# Combined local installation
.PHONY: local
local: glog-local libmodbus-local

# Development mode (with debugging symbols)
.PHONY: glog-dev
glog-dev: glog-submodule
	@mkdir -p $(GLOG_BUILD_DIR)
	cd $(GLOG_BUILD_DIR) && \
	cmake .. \
		-DCMAKE_BUILD_TYPE=Debug \
		-DCMAKE_INSTALL_PREFIX=/usr/local \
		-DBUILD_SHARED_LIBS=ON \
		-DWITH_GFLAGS=OFF \
		-DWITH_UNWIND=ON
	cd $(GLOG_BUILD_DIR) && $(MAKE) -j$(shell nproc 2>/dev/null || echo 4)
	cd $(GLOG_BUILD_DIR) && sudo $(MAKE) install

.PHONY: libmodbus-dev
libmodbus-dev: modbus-submodule
	cd $(MODBUS_DIR) && \
	autoreconf -f -i 2>/dev/null || autoreconf -i
	@mkdir -p $(MODBUS_BUILD_DIR)
	cd $(MODBUS_BUILD_DIR) && \
	../configure \
		--prefix=/usr/local \
		--enable-shared \
		--disable-static \
		CFLAGS="-g -O0"
	cd $(MODBUS_BUILD_DIR) && $(MAKE) -j$(shell nproc 2>/dev/null || echo 4)
	cd $(MODBUS_BUILD_DIR) && sudo $(MAKE) install

# Clean targets
.PHONY: clean
clean: clean-glog clean-modbus

.PHONY: clean-glog
clean-glog:
	rm -rf $(GLOG_BUILD_DIR)

.PHONY: clean-modbus
clean-modbus:
	rm -rf $(MODBUS_BUILD_DIR)

# Distclean (remove everything including submodules)
.PHONY: distclean
distclean: clean
	@echo "Removing submodules..."
	-git submodule deinit -f $(GLOG_DIR)
	-git submodule deinit -f $(MODBUS_DIR)
	-git rm -f $(GLOG_DIR)
	-git rm -f $(MODBUS_DIR)
	rm -rf .git/modules/$(GLOG_DIR)
	rm -rf .git/modules/$(MODBUS_DIR)
	rm -rf $(GLOG_DIR)
	rm -rf $(MODBUS_DIR)

# Check dependencies
.PHONY: check-deps
check-deps:
	@echo "Checking build dependencies..."
	@command -v cmake >/dev/null 2>&1 || echo "CMake is not installed"
	@command -v autoreconf >/dev/null 2>&1 || echo "autoconf is not installed"
	@command -v make >/dev/null 2>&1 || echo "make is not installed"
	@command -v gcc >/dev/null 2>&1 || echo "gcc is not installed"
	@echo "Dependency check complete"
	@export CC=/usr/bin/clang
	@export CXX=/usr/bin/clang++

gflags-submodule:
	@if [ ! -f "$(GFLAGS_DIR)/CMakeLists.txt" ]; then \
		echo "Adding gflags submodule..."; \
		git submodule add https://github.com/gflags/gflags.git $(GLOG_DIR); \
	else \
		echo "gflags submodule already exists"; \
		git submodule update --init --recursive $(GFLAGS_DIR); \
	fi

gflags-configure:
	@echo "Configure gflags to $(GFLAGS_BUILD_DIR) ..."
	@cd $(mkfile_path) 
	@mkdir -p $(GFLAGS_BUILD_DIR)
	cd $(GFLAGS_DIR)  && \
	cmake .. --trace \
		-G "Unix Makefiles" \
		-B $(GFLAGS_BUILD_DIR) \
		-DCMAKE_BUILD_TYPE=Release \
		-DBUILD_SHARED_LIBS=ON 

gflags: gflags-submodule gflags-configure
	@echo "Building and installing gflags..."
	@cd $(mkfile_path) 
	cd $(GFLAGS_BUILD_DIR) && $(MAKE) -j$(shell nproc 2>/dev/null || echo 4)
	cd $(GFLAGS_BUILD_DIR) && sudo $(MAKE) install
	@echo "gflags installed successfully"

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo ""
	@echo "  all              - Build and install both glog and libmodbus system-wide"
	@echo "  local            - Build and install both libraries locally"
	@echo "  submodules       - Only add submodules"
	@echo "  update-submodules - Update all submodules to latest"
	@echo ""
	@echo "Individual library targets (system-wide):"
	@echo "  glog             - Build and install glog (requires sudo)"
	@echo "  libmodbus        - Build and install libmodbus (requires sudo)"
	@echo ""
	@echo "Individual library targets (local):"
	@echo "  glog-local       - Build and install glog locally"
	@echo "  libmodbus-local  - Build and install libmodbus locally"
	@echo ""
	@echo "Development targets:"
	@echo "  glog-dev         - Build glog with debug symbols"
	@echo "  libmodbus-dev    - Build libmodbus with debug symbols"
	@echo ""
	@echo "Clean targets:"
	@echo "  clean            - Remove all build files"
	@echo "  clean-glog       - Remove glog build files"
	@echo "  clean-modbus     - Remove libmodbus build files"
	@echo "  distclean        - Completely remove both libraries including submodules"
	@echo ""
	@echo "Utility targets:"
	@echo "  check-deps       - Check for required build tools"
	@echo "  help             - Show this help message"