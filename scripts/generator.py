#!/usr/bin/env python3
"""
Makefile Generator for Git Submodules with Different Build Systems
Usage: python generate_makefile.py [config_file.json]
"""

import json
import os
import sys
import argparse
from typing import Dict, List, Any

TEMPLATE = """# Generated Makefile for managing submodules with different build systems
# To regenerate: python {generator_script}

# Default target - builds all libraries
.PHONY: all
all: {all_targets}

# Directory definitions
{submodule_vars}

# Submodule management targets
{submodule_targets}

# Update all submodules
.PHONY: update-submodules
update-submodules:
	@echo "Updating all submodules..."
	git submodule update --remote --merge

# Build targets (system-wide installation)
{build_targets}

# Local installation targets (no sudo required)
{local_targets}

# Development mode targets (with debugging symbols)
{dev_targets}

# Clean targets
.PHONY: clean
clean: {clean_targets}

{individual_clean_targets}

# Distclean (remove everything including submodules)
.PHONY: distclean
distclean: clean
	@echo "Removing all submodules..."
{distclean_commands}

# Check dependencies
.PHONY: check-deps
check-deps:
	@echo "Checking build dependencies..."
{dependency_checks}
	@echo "Dependency check complete"

# Install build dependencies (Ubuntu/Debian)
.PHONY: install-deps
install-deps:
	sudo apt-get update
	sudo apt-get install -y {apt_dependencies}

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo ""
	@echo "  all              - Build and install all libraries system-wide"
	@echo "  local            - Build and install all libraries locally"
	@echo "  submodules       - Only add all submodules"
	@echo "  update-submodules - Update all submodules to latest"
	@echo ""
	@echo "Individual library targets (system-wide):"
{system_targets_help}
	@echo ""
	@echo "Individual library targets (local):"
{local_targets_help}
	@echo ""
	@echo "Development targets:"
{dev_targets_help}
	@echo ""
	@echo "Clean targets:"
	@echo "  clean            - Remove all build files"
{clean_targets_help}
	@echo "  distclean        - Completely remove all libraries including submodules"
	@echo ""
	@echo "Utility targets:"
	@echo "  check-deps       - Check for required build tools"
	@echo "  install-deps     - Install build dependencies (Ubuntu/Debian)"
	@echo "  help             - Show this help message"
"""

class SubmoduleConfig:
    """Configuration for a single submodule"""
    
    def __init__(self, name: str, url: str, build_system: str, **kwargs):
        self.name = name
        self.url = url
        self.build_system = build_system.lower()
        self.directory = kwargs.get('directory', name)
        self.build_dir = f"{self.directory}/build"
        self.dependencies = kwargs.get('dependencies', [])
        self.build_options = kwargs.get('build_options', {})
        
        # Validate build system
        valid_systems = ['cmake', 'autoconf', 'make', 'meson']
        if self.build_system not in valid_systems:
            raise ValueError(f"Invalid build system: {self.build_system}. Must be one of {valid_systems}")

class MakefileGenerator:
    """Generates Makefiles for managing submodules"""
    
    def __init__(self, configs: List[SubmoduleConfig], output_file: str = "Makefile"):
        self.configs = configs
        self.output_file = output_file
        self.generator_script = os.path.basename(__file__)
        
    def generate(self):
        """Generate the complete Makefile"""
        content = TEMPLATE.format(
            generator_script=self.generator_script,
            all_targets=" ".join([config.name for config in self.configs]),
            submodule_vars=self._generate_submodule_vars(),
            submodule_targets=self._generate_submodule_targets(),
            build_targets=self._generate_build_targets(),
            local_targets=self._generate_local_targets(),
            dev_targets=self._generate_dev_targets(),
            clean_targets=" ".join([f"clean-{config.name}" for config in self.configs]),
            individual_clean_targets=self._generate_individual_clean_targets(),
            distclean_commands=self._generate_distclean_commands(),
            dependency_checks=self._generate_dependency_checks(),
            apt_dependencies=self._generate_apt_dependencies(),
            system_targets_help=self._generate_system_targets_help(),
            local_targets_help=self._generate_local_targets_help(),
            dev_targets_help=self._generate_dev_targets_help(),
            clean_targets_help=self._generate_clean_targets_help()
        )
        
        with open(self.output_file, 'w') as f:
            f.write(content)
        
        print(f"Makefile generated successfully: {self.output_file}")
        os.chmod(self.output_file, 0o755)
    
    def _generate_submodule_vars(self) -> str:
        """Generate directory variable definitions"""
        lines = []
        for config in self.configs:
            lines.append(f"{config.name.upper()}_DIR ?= {config.directory}")
            lines.append(f"{config.name.upper()}_BUILD_DIR = $({config.name.upper()}_DIR)/build")
        return "\n".join(lines)
    
    def _generate_submodule_targets(self) -> str:
        """Generate submodule addition targets"""
        targets = []
        
        # Combined submodules target
        targets.append(".PHONY: submodules")
        targets.append(f"submodules: {' '.join([f'{config.name}-submodule' for config in self.configs])}")
        targets.append("")
        
        # Individual submodule targets
        for config in self.configs:
            targets.append(f".PHONY: {config.name}-submodule")
            targets.append(f"{config.name}-submodule:")
            targets.append(f"\t@if [ ! -d \"$({config.name.upper()}_DIR)/.git\" ]; then \\")
            targets.append(f"\t\techo \"Adding {config.name} submodule...\"; \\")
            targets.append(f"\t\tgit submodule add {config.url} $({config.name.upper()}_DIR); \\")
            targets.append(f"\telse \\")
            targets.append(f"\t\techo \"{config.name} submodule already exists\"; \\")
            targets.append(f"\tfi")
            
            # Check for build system files and update if needed
            if config.build_system == 'cmake':
                check_file = "CMakeLists.txt"
            elif config.build_system == 'autoconf':
                check_file = "configure.ac"
            elif config.build_system == 'make':
                check_file = "Makefile"
            else:  # meson
                check_file = "meson.build"
                
            targets.append(f"\t@if [ ! -f \"$({config.name.upper()}_DIR)/{check_file}\" ]; then \\")
            targets.append(f"\t\tgit submodule update --init --recursive $({config.name.upper()}_DIR); \\")
            targets.append(f"\tfi")
            targets.append("")
        
        return "\n".join(targets)
    
    def _get_build_commands(self, config: SubmoduleConfig, install_prefix: str, build_type: str = "Release") -> str:
        """Generate build commands for a specific submodule"""
        commands = []
        
        if config.build_system == 'cmake':
            cmake_options = config.build_options.get('cmake_options', [])
            cmake_flags = " \\\n\t\t".join([f"-D{opt}" for opt in cmake_options])
            
            commands.append(f"\t@mkdir -p $({config.name.upper()}_BUILD_DIR)")
            commands.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && \\")
            
            base_cmd = f"cmake .. \\\n\t\t-DCMAKE_BUILD_TYPE={build_type} \\\n\t\t-DCMAKE_INSTALL_PREFIX={install_prefix} \\\n\t\t-DBUILD_SHARED_LIBS=ON"
            
            if cmake_flags:
                base_cmd += f" \\\n\t\t{cmake_flags}"
                
            commands.append(f"\t{base_cmd}")
            commands.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && $(MAKE) -j$$(shell nproc 2>/dev/null || echo 4)")
            
        elif config.build_system == 'autoconf':
            autoconf_options = config.build_options.get('autoconf_options', [])
            configure_flags = " \\\n\t\t".join([f"--{opt}" for opt in autoconf_options])
            
            commands.append(f"\tcd $({config.name.upper()}_DIR) && \\")
            commands.append(f"\tautoreconf -f -i 2>/dev/null || autoreconf -i")
            commands.append(f"\t@mkdir -p $({config.name.upper()}_BUILD_DIR)")
            commands.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && \\")
            
            base_cmd = f"../configure \\\n\t\t--prefix={install_prefix} \\\n\t\t--enable-shared \\\n\t\t--disable-static"
            
            if configure_flags:
                base_cmd += f" \\\n\t\t{configure_flags}"
                
            commands.append(f"\t{base_cmd}")
            commands.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && $(MAKE) -j$$(shell nproc 2>/dev/null || echo 4)")
            
        elif config.build_system == 'make':
            make_options = config.build_options.get('make_options', {})
            env_vars = " ".join([f"{k}={v}" for k, v in make_options.items()])
            
            commands.append(f"\tcd $({config.name.upper()}_DIR) && \\")
            if env_vars:
                commands.append(f"\t{env_vars} $(MAKE) -j$$(shell nproc 2>/dev/null || echo 4)")
            else:
                commands.append(f"\t$(MAKE) -j$$(shell nproc 2>/dev/null || echo 4)")
                
        elif config.build_system == 'meson':
            meson_options = config.build_options.get('meson_options', [])
            meson_flags = " ".join([f"-D{opt}" for opt in meson_options])
            
            commands.append(f"\t@mkdir -p $({config.name.upper()}_BUILD_DIR)")
            commands.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && \\")
            commands.append(f"\tmeson setup .. --buildtype={build_type.lower()} --prefix={install_prefix} {meson_flags}")
            commands.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && ninja")
        
        return "\n".join(commands)
    
    def _generate_build_targets(self) -> str:
        """Generate build targets for system-wide installation"""
        targets = []
        
        for config in self.configs:
            targets.append(f".PHONY: {config.name}")
            targets.append(f"{config.name}: {config.name}-submodule")
            targets.append(f"\t@echo \"Building and installing {config.name}...\"")
            
            commands = self._get_build_commands(config, "/usr/local", "Release")
            targets.append(commands)
            
            if config.build_system in ['cmake', 'autoconf', 'meson']:
                targets.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && sudo $(MAKE) install")
            elif config.build_system == 'make':
                targets.append(f"\tcd $({config.name.upper()}_DIR) && sudo $(MAKE) install")
                
            targets.append(f"\t@echo \"{config.name} installed successfully\"")
            targets.append("")
        
        return "\n".join(targets)
    
    def _generate_local_targets(self) -> str:
        """Generate local installation targets"""
        targets = []
        
        # Combined local target
        local_targets = [f"{config.name}-local" for config in self.configs]
        targets.append(".PHONY: local")
        targets.append(f"local: {' '.join(local_targets)}")
        targets.append("")
        
        # Individual local targets
        for config in self.configs:
            targets.append(f".PHONY: {config.name}-local")
            targets.append(f"{config.name}-local: {config.name}-submodule")
            targets.append(f"\t@echo \"Building and installing {config.name} locally...\"")
            
            if config.build_system in ['cmake', 'autoconf', 'meson']:
                install_prefix = f"$$(pwd)/install"
                commands = self._get_build_commands(config, install_prefix, "Release")
                targets.append(commands)
                targets.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && $(MAKE) install")
                targets.append(f"\t@echo \"{config.name} installed to: $({config.name.upper()}_BUILD_DIR)/install\"")
            elif config.build_system == 'make':
                targets.append(f"\t@echo \"Note: make build system may not support local installation\"")
                targets.append(f"\tcd $({config.name.upper()}_DIR) && \\")
                targets.append(f"\t$(MAKE) -j$$(shell nproc 2>/dev/null || echo 4) PREFIX=$$(pwd)/install")
                targets.append(f"\tcd $({config.name.upper()}_DIR) && $(MAKE) PREFIX=$$(pwd)/install install")
                
            targets.append("")
        
        return "\n".join(targets)
    
    def _generate_dev_targets(self) -> str:
        """Generate development targets with debug symbols"""
        targets = []
        
        for config in self.configs:
            targets.append(f".PHONY: {config.name}-dev")
            targets.append(f"{config.name}-dev: {config.name}-submodule")
            targets.append(f"\t@echo \"Building {config.name} with debug symbols...\"")
            
            if config.build_system == 'cmake':
                commands = self._get_build_commands(config, "/usr/local", "Debug")
                targets.append(commands)
                targets.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && sudo $(MAKE) install")
            elif config.build_system == 'autoconf':
                config.build_options.setdefault('autoconf_options', []).append('CFLAGS=-g -O0')
                commands = self._get_build_commands(config, "/usr/local", "Release")
                targets.append(commands)
                targets.append(f"\tcd $({config.name.upper()}_BUILD_DIR) && sudo $(MAKE) install")
            else:
                targets.append(f"\t@echo \"Debug build not configured for {config.build_system} build system\"")
                
            targets.append("")
        
        return "\n".join(targets)
    
    def _generate_individual_clean_targets(self) -> str:
        """Generate individual clean targets"""
        targets = []
        
        for config in self.configs:
            targets.append(f".PHONY: clean-{config.name}")
            targets.append(f"clean-{config.name}:")
            targets.append(f"\trm -rf $({config.name.upper()}_BUILD_DIR)")
            if config.build_system == 'make':
                targets.append(f"\tcd $({config.name.upper()}_DIR) && make clean 2>/dev/null || true")
            targets.append("")
        
        return "\n".join(targets)
    
    def _generate_distclean_commands(self) -> str:
        """Generate distclean commands"""
        commands = []
        
        for config in self.configs:
            commands.append(f"\t-git submodule deinit -f $({config.name.upper()}_DIR)")
            commands.append(f"\t-git rm -f $({config.name.upper()}_DIR)")
            commands.append(f"\trm -rf .git/modules/$({config.name.upper()}_DIR)")
            commands.append(f"\trm -rf $({config.name.upper()}_DIR)")
        
        return "\n".join(commands)
    
    def _generate_dependency_checks(self) -> str:
        """Generate dependency check commands"""
        checks = []
        build_systems = set(config.build_system for config in self.configs)
        
        if 'cmake' in build_systems:
            checks.append('\t@command -v cmake >/dev/null 2>&1 || echo "CMake is not installed"')
        if 'autoconf' in build_systems:
            checks.append('\t@command -v autoreconf >/dev/null 2>&1 || echo "autoconf is not installed"')
        if 'meson' in build_systems:
            checks.append('\t@command -v meson >/dev/null 2>&1 || echo "meson is not installed"')
            checks.append('\t@command -v ninja >/dev/null 2>&1 || echo "ninja is not installed"')
        
        checks.append('\t@command -v make >/dev/null 2>&1 || echo "make is not installed"')
        checks.append('\t@command -v gcc >/dev/null 2>&1 || echo "gcc is not installed"')
        checks.append('\t@command -v git >/dev/null 2>&1 || echo "git is not installed"')
        
        return "\n".join(checks)
    
    def _generate_apt_dependencies(self) -> str:
        """Generate apt dependencies list"""
        deps = ["git", "build-essential", "gcc", "g++"]
        build_systems = set(config.build_system for config in self.configs)
        
        if 'cmake' in build_systems:
            deps.append("cmake")
        if 'autoconf' in build_systems:
            deps.extend(["autoconf", "automake", "libtool"])
        if 'meson' in build_systems:
            deps.extend(["meson", "ninja-build"])
        
        return " ".join(deps)
    
    def _generate_system_targets_help(self) -> str:
        """Generate help text for system targets"""
        lines = []
        for config in self.configs:
            lines.append(f"  {config.name:15} - Build and install {config.name} (requires sudo)")
        return "\n".join(lines)
    
    def _generate_local_targets_help(self) -> str:
        """Generate help text for local targets"""
        lines = []
        for config in self.configs:
            lines.append(f"  {config.name + '-local':15} - Build and install {config.name} locally")
        return "\n".join(lines)
    
    def _generate_dev_targets_help(self) -> str:
        """Generate help text for dev targets"""
        lines = []
        for config in self.configs:
            lines.append(f"  {config.name + '-dev':15} - Build {config.name} with debug symbols")
        return "\n".join(lines)
    
    def _generate_clean_targets_help(self) -> str:
        """Generate help text for clean targets"""
        lines = []
        for config in self.configs:
            lines.append(f"  clean-{config.name:10} - Remove {config.name} build files")
        return "\n".join(lines)

def load_config_from_json(filename: str) -> List[SubmoduleConfig]:
    """Load configuration from JSON file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    configs = []
    for item in data.get('submodules', []):
        configs.append(SubmoduleConfig(**item))
    
    return configs

def interactive_config() -> List[SubmoduleConfig]:
    """Interactive configuration mode"""
    configs = []
    
    print("=== Makefile Generator for Git Submodules ===")
    print("Enter submodule configurations (leave name empty when done):")
    
    while True:
        print(f"\nSubmodule #{len(configs) + 1}:")
        name = input("Name (e.g., glog, libmodbus): ").strip()
        if not name:
            break
            
        url = input(f"Git URL for {name}: ").strip()
        if not url:
            print("URL is required!")
            continue
            
        print("Available build systems: cmake, autoconf, make, meson")
        build_system = input(f"Build system for {name}: ").strip().lower()
        
        directory = input(f"Directory name [default: {name}]: ").strip()
        if not directory:
            directory = name
        
        config = SubmoduleConfig(
            name=name,
            url=url,
            build_system=build_system,
            directory=directory
        )
        
        configs.append(config)
        print(f"Added {name}")
    
    return configs

def main():
    parser = argparse.ArgumentParser(description='Generate Makefile for managing git submodules')
    parser.add_argument('config', nargs='?', help='JSON configuration file')
    parser.add_argument('-o', '--output', default='Makefile', help='Output Makefile name')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive:
        configs = interactive_config()
    elif args.config:
        configs = load_config_from_json(args.config)
    else:
        # Example configuration
        configs = [
            SubmoduleConfig(
                name="glog",
                url="https://github.com/google/glog.git",
                build_system="cmake",
                build_options={
                    "cmake_options": ["WITH_GFLAGS=OFF", "WITH_UNWIND=ON"]
                }
            ),
            SubmoduleConfig(
                name="libmodbus",
                url="https://github.com/stephane/libmodbus.git",
                build_system="autoconf",
                build_options={
                    "autoconf_options": ["enable-shared", "disable-static"]
                }
            )
        ]
    
    if not configs:
        print("No submodules configured. Exiting.")
        return
    
    generator = MakefileGenerator(configs, args.output)
    generator.generate()
    
    # Also save configuration to JSON for future reference
    config_data = {
        "submodules": [
            {
                "name": config.name,
                "url": config.url,
                "build_system": config.build_system,
                "directory": config.directory,
                "build_options": config.build_options
            }
            for config in configs
        ]
    }
    
    config_filename = f"{args.output}.config.json"
    with open(config_filename, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"Configuration saved to: {config_filename}")
    print("\nUsage examples:")
    print(f"  make all                    # Build and install all libraries")
    print(f"  make {configs[0].name}     # Build and install specific library")
    print(f"  make local                  # Local installation")
    print(f"  make check-deps            # Check dependencies")
    print(f"  make help                  # Show all targets")

if __name__ == "__main__":
    main()