#!/bin/bash

DRAGON_DIR=$1
MODULE_DIR=$DRAGON_DIR/modulefiles

echo "Activating Spyral virtual environment .venv and Dragon"

module use /soft/modulefiles
module load conda
conda activate base
source .venv/bin/activate
module use $MODULE_DIR
module load dragon

echo "Spyral environment with Dragon has been acitvated."