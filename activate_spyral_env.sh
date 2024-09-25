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
module use /soft/modulefiles
module load conda
if [ ! -x conda ]
then
    echo "Failed to load conda! conda was not found in the path."
    return
fi
echo "Activating conda base environment..."
conda activate base
if [ ! -x python ]
then
    echo "Failed to activate the conda base environment!"
    echo "python was not found in the path."
    return
fi
echo "Activating Spyral virtual environment..."
source .venv/bin/activate
echo "Loading Dragon modules..."
module use $MODULE_DIR
module load dragon
if [ ! -x dragon ]
then
    echo "Failed to load dragon!"
    echo "dragon was not found in the path."
    return
fi

echo "Spyral environment with Dragon has been acitvated."