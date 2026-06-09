#!/bin/bash
set -e  # Stop on error

ENV_DIR="globus_venv"
PYTHON_CMD="python3"

echo "=== Creating Python virtual environment in ./${ENV_DIR} ==="
${PYTHON_CMD} -m venv ${ENV_DIR}

echo "=== Activating environment and upgrading pip ==="
source ${ENV_DIR}/bin/activate
pip install --upgrade pip

echo "=== Installing globus-cli ==="
pip install globus-cli

echo "=== Installation complete ==="
echo "To activate the environment: source ./${ENV_DIR}/bin/activate"
echo "Then run: python cc_data_manager.py [options]"