pipeline {
    agent any

    environment {
        PATH              = "/var/jenkins_home/.local/bin:${env.PATH}"
        DOCKER_IMAGE_NAME = 'hr1thik/iris-mlops-api'
        IMAGE_TAG         = "${BUILD_NUMBER}"
        GIT_REPO_URL      = 'https://github.com/Hr1thik/iris-mlops-devsecops-api.git'
        GIT_BRANCH        = 'main'
        DOCKER_HUB_CREDS  = credentials('dockerhub-creds')
        GITHUB_TOKEN      = credentials('github-pat')
    }

    stages {
        stage('Checkout Source') {
            steps {
                cleanWs()
                checkout scm
            }
        }

        stage('SAST - Python Security Scan') {
            steps {
                echo "Running Static Application Security Testing (Bandit)..."
                sh '''
                    pip3 install --user bandit --break-system-packages || true
                    bandit -r app.py -f json -o bandit-report.json || true
                '''
            }
        }

        stage('SCA - Dependency Vulnerability Scan') {
            steps {
                echo "Scanning requirements.txt for known vulnerabilities..."
                sh '''
                    pip3 install --user safety --break-system-packages || true
                    safety check -r requirements.txt || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${IMAGE_TAG}"
                sh """
                    docker build -t ${DOCKER_IMAGE_NAME}:${IMAGE_TAG} -t ${DOCKER_IMAGE_NAME}:latest .
                """
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                echo "Publishing image to Docker Hub..."
                sh """
                    echo "\$DOCKER_HUB_CREDS_PSW" | docker login -u "\$DOCKER_HUB_CREDS_USR" --password-stdin
                    docker push ${DOCKER_IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${DOCKER_IMAGE_NAME}:latest
                """
            }
        }

        stage('Update GitOps Manifests') {
            steps {
                echo "Updating k8s/deployment.yml with image tag ${IMAGE_TAG}..."
                sh """
                    sed -i "s|image: ${DOCKER_IMAGE_NAME}:.*|image: ${DOCKER_IMAGE_NAME}:${IMAGE_TAG}|g" k8s/deployment.yml
                    git config user.name "jenkins-bot"
                    git config user.email "jenkins@devops.local"
                    git add k8s/deployment.yml
                    git commit -m "ci: update image tag to ${IMAGE_TAG} [skip ci]" || true
                    git push https://\${GITHUB_TOKEN}@github.com/Hr1thik/iris-mlops-devsecops-api.git HEAD:${GIT_BRANCH}
                """
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
        success {
            echo "Pipeline succeeded! ArgoCD will automatically detect the new commit and deploy image tag: ${IMAGE_TAG}."
        }
        failure {
            echo "Pipeline failed. Check stage logs for details."
        }
    }
}