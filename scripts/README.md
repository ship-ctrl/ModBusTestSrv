# Generate Makefile interactively
python generate_makefile.py -i

# Generate from JSON configuration
python generate_makefile.py config.json

# Generate with custom output name
python generate_makefile.py config.json -o MyMakefile

# Use the generated Makefile
make all
make glog
make local
make check-deps
make help