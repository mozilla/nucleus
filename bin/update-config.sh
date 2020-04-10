#!/bin/bash
set -ex

. ${BASH_SOURCE%/*}/../docker/bin/set_git_env_vars.sh # sets DOCKER_IMAGE_TAG & DOCKER_REPOSITORY

# env vars: CLUSTER_NAME, CONFIG_BRANCH, CONFIG_REPO, NAMESPACE
: "${CLUSTER_NAME:=frankfurt}"
: "${CONFIG_BRANCH:=master}"
: "${CONFIG_REPO:=github-mozmar-robot:mozmeao/nucleus-config}"
: "${NAMESPACE:=basket-dev}"

pushd "$(mktemp -d)"
git clone --depth=1 -b "${CONFIG_BRANCH}" "${CONFIG_REPO}" nucleus-config
cd nucleus-config

set -u
for DEPLOYMENT_FILE in "${CLUSTER_NAME}/${NAMESPACE}"/*-deploy.yaml; do
    sed -i -e "s|image: .*|image: ${DOCKER_IMAGE_TAG}|" "${DEPLOYMENT_FILE}"
    git add "${DEPLOYMENT_FILE}"
done

git commit -m "set image to ${DOCKER_IMAGE_TAG} in ${CLUSTER_NAME}" || echo "nothing new to commit"
git push
popd
