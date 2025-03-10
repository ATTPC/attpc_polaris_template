#!/bin/bash

source .env

echo "Preparing a Spyral environment with Dragon..."
echo "Loading conda to get Python..."
module use /soft/modulefiles
module load conda
if ! command -v conda 2>&1 >/dev/null
then
    echo "Failed to load conda! conda was not found in the path."
    return
fi
echo "Activating conda base environment..."
conda activate base
if ! command -v python 2>&1 >/dev/null 
then
    echo "Failed to activate the conda base environment!"
    echo "python was not found in the path."
    return
fi
echo "Creating a new virtual environment..."
python -m venv .venv --system-site-packages
source .venv/bin/activate
echo "Installing Dragon specific wheels..."
# Hack the Jinja version. The one installed by default is old
pip install --ignore-installed Jinja2
pip install dragonhpc 
echo "Installing Spyral and dependencies..."
pip install attpc_spyral
if [ ! -d "$LIBFABRIC_PATH" ]
then
    echo "The LIBFABRIC_PATH environment variable is not set, or is invalid"
    echo "Please set this variable using the .env file included with this directory"
    echo "Current value: ${LIBFABRIC_PATH}"
    echo "If this is not set at installation, dragonhpc will not use the fast slingshot"
    echo "protocol, and instead default to slow TCP for interconnect."
else
    echo "Setting up dragonhpc HSTA..."
    dragon-config -a "ofi-runtime-lib=${LIBFABRIC_PATH}"
fi

if ! command -v dragon 2>&1 >/dev/null
then
    echo "Failed to load dragon!"
    echo "dragon was not found in the path."
    return
fi

echo "A virtual envorinment .venv has been created and loaded with the appropriate Dragon configuration"
