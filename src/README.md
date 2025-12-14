# Create build directory
```sh
mkdir build && cd build
```

# Build with CMake
```sh
cmake ..
make
```

# Run with default flags
```sh
./example
```
# Run with custom flags
```sh
./example --config=myapp.conf --port=9090 --verbose=true --threshold=0.7
```


# See help message
```sh
./example --help
```

# Save logs to specific directory
```sh
./example --log_dir=./logs
```