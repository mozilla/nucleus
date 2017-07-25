milestone()
stage ('Build Images') {
    // make sure we should continue
    env.DOCKER_REPOSITORY = 'mozmeao/nucleus'
    env.DOCKER_IMAGE_TAG = "${env.DOCKER_REPOSITORY}:${env.GIT_COMMIT}"
    if ( config.require_tag ) {
        try {
            sh 'docker/bin/check_if_tag.sh'
        } catch(err) {
            utils.ircNotification([stage: 'Git Tag Check', status: 'failure'])
            throw err
        }
    }
    utils.ircNotification([stage: 'Test & Deploy', status: 'starting'])
    lock ("nucleus-docker-${env.GIT_COMMIT}") {
        try {
            sh 'docker/bin/build_images.sh'
            sh 'docker/bin/run_tests.sh'
        } catch(err) {
            utils.ircNotification([stage: 'Docker Build', status: 'failure'])
            throw err
        }
    }
}

milestone()
stage ('Push Public Images') {
    try {
        utils.pushDockerhub()
    } catch(err) {
        utils.ircNotification([stage: 'Dockerhub Push', status: 'failure'])
        throw err
    }
}

if ( config.apps ) {
    milestone()
    // default to frankfurt
    def regions = config.regions ?: ['frankfurt']
    for (regionId in regions) {
        for (appname in config.apps) {
            appURL = "https://${appname}.${regionId}.moz.works"
            stageName = "Deploy ${appname}-${regionId}"
            lock (stageName) {
                milestone()
                stage (stageName) {
                    withEnv(["DEIS_PROFILE=${regionId}",
                             "RUN_POST_DEPLOY=true",
                             "DEIS_APPLICATION=${appname}"]) {
                        try {
                            retry(2) {
                                sh 'docker/bin/push2deis.sh'
                            }
                        } catch(err) {
                            utils.ircNotification([stage: stageName, status: 'failure'])
                            throw err
                        }
                    }
                    utils.ircNotification([message: appURL, status: 'shipped'])
                }
            }
        }
    }
}
