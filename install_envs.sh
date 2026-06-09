#!/bin/bash
set -e  # Stop on error

CONDA_ENV_GLOBUS="globus"

echo "=== Checking conda version ==="
conda --version

# Install mamba if not already present
if ! command -v mamba &> /dev/null; then
    echo "=== Installing mamba (faster dependency solver) ==="
    conda install mamba -c conda-forge -y
fi

echo "=== Creating Conda environment with globus-cli using mamba ==="
mamba create -n ${CONDA_ENV_GLOBUS} -c conda-forge -y globus-cli

echo "=== Environment ready ==="
echo "Activate with: conda activate ${CONDA_ENV_GLOBUS}"