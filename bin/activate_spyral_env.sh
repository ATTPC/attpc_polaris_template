#!/bin/bash

source .env
if [ ! -d ".venv" ]
then
    echo "The virtual environment .venv does not exist!"
    echo "Please use create_spyral_env.sh to make the venv"
    echo "before trying to activate it."
    return
fi
echo "Activating Spyral virtual environment .venv and Dragon"
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
echo "Activating Spyral virtual environment..."
source .venv/bin/activate
if ! command -v dragon 2>&1 >/dev/null
then
    echo "Failed to load dragon!"
    echo "dragon was not found in the path."
    return
fi

echo "Spyral environment with Dragon has been acitvated."
