#!/bin/bash -e

# Set env vars used in docker-compose.yml and other scripts
source docker/bin/set_git_env_vars.sh
docker-compose "$@"
