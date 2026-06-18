#!/bin/bash

source $CONDA_SOURCE
conda activate $CONDA_ENV_ROOT/_CMEC_npjphase_env

python $CMEC_CODE_DIR/Compute_NPJregime_stats.py 
