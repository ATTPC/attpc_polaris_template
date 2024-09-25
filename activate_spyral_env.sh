#!/bin/bash

source .env
if [ ! -d "$DRAGON_DIR" ]
then
    echo "The DRAGON_DIR environment variable is not set, or is invalid"
    echo "Please set this variable using the .env file included with this directory"
    echo "Current value: ${DRAGON_DIR}"
    return
fi
MODULE_DIR=$DRAGON_DIR/modulefiles

echo "Activating Spyral virtual environment .venv and Dragon"

echo "Loading conda to get Python..."
module use /soft/modulefiles &> /dev/null
module load conda
echo "Activating conda base environment..."
conda activate base
echo "Activating Spyral virtual environment..."
source .venv/bin/activate
echo "Loading Dragon modules..."
module use $MODULE_DIR
module load dragon

echo "Spyral environment with Dragon has been acitvated."