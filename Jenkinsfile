// Pipeline: build Docker image, run container and test /health, push to Docker Hub.
// Trigger: Configure the job with "Generic Webhook Trigger" and point GitHub (or other) webhook to it.
// Optional post-content parameters the plugin can pass (e.g. from GitHub push):
//   - ref (e.g. refs/heads/main or refs/tags/v1.0.0)
//   - repository.name (or $.repository.name in JSON path)
// Jenkins credentials: add a "Username and password" credential with Docker Hub login (ID: dockerhub-credentials).

pipeline {
  agent any

  environment {
    // Image name: set DOCKERHUB_USERNAME and DOCKER_IMAGE_REPO in Jenkins env, or use params
    DOCKER_IMAGE = "${env.DOCKERHUB_USERNAME ?: params.DOCKERHUB_USERNAME}/${env.DOCKER_IMAGE_REPO ?: params.DOCKER_IMAGE_REPO}"
    DOCKER_TAG = "${env.DOCKER_TAG ?: params.DOCKER_TAG}"
    FULL_IMAGE = "${DOCKER_IMAGE}:${DOCKER_TAG}"
  }

  triggers {
    genericWebhook {
      allowPostContentParameter = true
      triggerPhrase = 'jenkins build'
      contentTypes = ['application/json']
    }
  }

  options {
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timeout(time: 30, unit: 'MINUTES')
  }

  parameters {
    string(name: 'DOCKERHUB_USERNAME', defaultValue: '', description: 'Docker Hub username (or set in Jenkins env)')
    string(name: 'DOCKER_IMAGE_REPO', defaultValue: 'python-service', description: 'Docker image repo name (e.g. repo name)')
    string(name: 'DOCKER_TAG', defaultValue: 'latest', description: 'Tag (e.g. latest or v1.0.0). Generic webhook can override from ref.')
  }

  stages {
    stage('Resolve tag from ref') {
      when { expression { return env.ref?.trim() } }
      steps {
        script {
          def ref = env.ref
          if (ref?.startsWith('refs/tags/')) {
            env.DOCKER_TAG = ref.replaceFirst('refs/tags/', '').trim()
          } else {
            env.DOCKER_TAG = 'latest'
          }
          env.FULL_IMAGE = "${env.DOCKER_IMAGE}:${env.DOCKER_TAG}"
          echo "Using image ${env.FULL_IMAGE}"
        }
      }
    }

    stage('Build') {
      steps {
        script {
          def username = env.DOCKERHUB_USERNAME ?: params.DOCKERHUB_USERNAME
          if (!username?.trim()) error 'DOCKERHUB_USERNAME (parameter or env) is required'
        }
        sh 'docker build -t "${FULL_IMAGE}" .'
      }
    }

    stage('Run and test health') {
      steps {
        sh '''
          set +e
          CONTAINER_ID=$(docker run -d -p 8000:8000 "${FULL_IMAGE}")
          trap "docker stop ${CONTAINER_ID}; docker rm ${CONTAINER_ID}" EXIT
          for i in $(seq 1 15); do
            if curl -sf http://localhost:8000/health > /dev/null; then
              echo "Health check passed"
              exit 0
            fi
            if [ "$i" -eq 15 ]; then
              echo "Health check failed after 15 attempts"
              exit 1
            fi
            sleep 2
          done
        '''
      }
    }

    stage('Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin'
          sh 'docker push "${FULL_IMAGE}"'
        }
      }
    }
  }

  post {
    always {
      sh 'docker logout || true'
    }
    cleanup {
      sh 'docker rm -f $(docker ps -aq --filter "ancestor=${FULL_IMAGE}") 2>/dev/null || true'
    }
  }
}
