#!/bin/bash

source .env
if [ ! -d "$DRAGON_DIR" ]
then
    echo "The DRAGON_DIR environment variable is not set, or is invalid"
    echo "Please set this variable using the .env file included with this directory"
    echo "Current value: ${DRAGON_DIR}"
    return
fi
DRAGON_WHEEL=$(ls $DRAGON_DIR/dragon*.whl)
PYCAPNP_WHEEL=$(ls $DRAGON_DIR/pycapnp*.whl)
MODULE_DIR=$DRAGON_DIR/modulefiles

echo "Preparing a Spyral environment with Dragon from ${DRAGON_DIR}"

echo "Loading conda to get Python..."
module use /soft/modulefiles &> /dev/null
module load conda
echo "Activating conda base environment..."
conda activate base
echo "Creating a new virtual environment..."
python -m venv .venv
source .venv/bin/activate
echo "Installing Dragon specific wheels..."
pip install $PYCAPNP_WHEEL
pip install $DRAGON_WHEEL
echo "Installing Spyral and dependencies..."
pip install attpc_spyral
echo "Loading Dragon modules..."
module use $MODULE_DIR
module load dragon

echo "A virtual envorinment .venv has been created and loaded with the appropriate Dragon configuration"
