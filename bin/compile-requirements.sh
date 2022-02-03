#!/bin/bash

set -exo pipefail

export CUSTOM_COMPILE_COMMAND="make compile-requirements"

# We need this installed, but we don't want it to live in the main requirements
# We will need to periodically review this pinning
pip install --upgrade "pip<22"  # Temporary until pip-tools is fixed.
pip install --upgrade pip-tools==6.4.0  # Needs at least this version to build.
pip install --upgrade pip-compile-multi

pip-compile-multi \
  --generate-hashes prod \
  --generate-hashes dev \
  --header=/app/requirements/.pip-compile-multi-header.txt
