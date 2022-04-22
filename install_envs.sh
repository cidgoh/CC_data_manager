#!/bin/bash
set -e  # Stop on error

SCRIPT_DIR="$(cd $(dirname $0) && pwd)"
. ${SCRIPT_DIR}/requirements/requirements.txt

CONDA_ENV_GLOBUS=globus

echo "=== Checking conda version ==="
conda --version

echo "=== Installing pipeline's Conda environments ==="

if [[ "$1" == mamba ]];then
  conda install mamba -y -c conda-forge
  mamba create -n ${CONDA_ENV_GLOBUS} -y -c conda-forge globus-cli=$globlus_cli
else
  echo
  echo "If it takes too long to resolve conflicts, then try with mamba."
  echo
  echo "Usage: ./install_conda_env.sh mamba"
  echo
  echo "mamba will resolve conflicts much faster then the original conda."
  echo "If you get another conflict in the mamba installation step itself "
  echo "Then you may need to clean-install miniconda3 and re-login."
  echo
  conda create -n ${CONDA_ENV_GLOBUS} -y -c conda-forge globus-cli=$globus_cli
fi


echo "=== Configuring for pipeline's Conda environments ==="
CONDA_PREFIX_GLOBUS=$(conda env list | grep -E "\b${CONDA_ENV_GLOBUS}[[:space:]]" | awk '{if (NF==3) print $3; else print $2}')

if [ ! "${CONDA_PREFIX_GLOBUS}" ];
then
	echo "Error: Pipeline's Conda environments not found."
	echo "Try to reinstall pipeline's Conda environments."
	echo
	echo "1) $ bash uninstall_conda_env.sh"
	echo "2) $ bash install_conda_env.sh"
	exit 1
fi


echo "=== All done successfully ==="
