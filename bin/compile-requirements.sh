#!/bin/bash

set -exo pipefail

export CUSTOM_COMPILE_COMMAND="make compile-requirements"

# Purge old requirements/*.txt files so we get our subdeps automatically upgraded if allowed
rm -f requirements/*.txt

# We need this installed, but we don't want it to live in the main requirements
# We will need to periodically review this pinning
pip install --upgrade pip
pip install --upgrade pip-tools
pip install --upgrade pip-compile-multi

pip-compile-multi \
  --generate-hashes prod \
  --generate-hashes dev \
  --header=/app/requirements/.pip-compile-multi-header.txt
