#!/bin/bash
set -ex
# env vars: CLUSTER_NAME, CONFIG_BRANCH, CONFIG_REPO, NAMESPACE, DEPLOYMENT_YAML

. ${BASH_SOURCE%/*}/../docker/bin/set_git_env_vars.sh # sets DEPLOYMENT_DOCKER_IMAGE
pushd $(mktemp -d)
git clone --depth=1 -b ${CONFIG_BRANCH:=master} ${CONFIG_REPO:=github-mozmar-robot:mozmeao/nucleus-config} nucleus-config
cd nucleus-config

set -u
sed -i -e "s|image: .*|image: ${DEPLOYMENT_DOCKER_IMAGE}|" ${CLUSTER_NAME:=iowa-b}/${NAMESPACE:=nucleus-dev}/${DEPLOYMENT_YAML:=deploy.yaml}
git add ${CLUSTER_NAME}/${NAMESPACE}/${DEPLOYMENT_YAML}
git commit -m "set image to ${DEPLOYMENT_DOCKER_IMAGE} in ${CLUSTER_NAME}" || echo "nothing new to commit"
git push
popd
