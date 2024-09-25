#!/bin/bash

DRAGON_DIR=$0
DRAGON_WHEEL=$(ls $DRAGON_DIR/dragon*.whl)
PYCAPNP_WHEEL=$(ls $DRAGON_DIR/pycapnp*.whl)
MODULE_DIR=$DRAGON_DIR/modulefiles

echo "Preparing a Spyral environment with Dragon from ${DRAGON_DIR}"

module use /soft/modulefiles
module load conda
conda activate base
python -m venv .venv
source .venv/bin/activate
pip install $PYCAPNP_WHEEL
pip install $DRAGON_WHEEL
module use $MODULE_DIR
module load dragon

echo "A virtual envorinment .venv has been created and loaded with the appropriate Dragon configuration"
