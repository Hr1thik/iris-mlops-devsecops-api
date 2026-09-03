pipeline {
    agent any

    environment {
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
                bat '''
                    pip install bandit
                    bandit -r app.py -f json -o bandit-report.json || exit 0
                '''
            }
        }

        stage('SCA - Dependency Vulnerability Scan') {
            steps {
                echo "Scanning requirements.txt for known vulnerabilities using Trivy..."
                bat '''
                    trivy fs --severity HIGH,CRITICAL requirements.txt || exit 0
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${IMAGE_TAG}"
                bat """
                    docker build -t ${DOCKER_IMAGE_NAME}:${IMAGE_TAG} -t ${DOCKER_IMAGE_NAME}:latest .
                """
            }
        }

        stage('Container Image Security Scan') {
            steps {
                echo "Scanning built container image with Trivy..."
                bat """
                    trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE_NAME}:${IMAGE_TAG} || exit 0
                """
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                echo "Publishing image to Docker Hub..."
                bat """
                    echo %DOCKER_HUB_CREDS_PSW% | docker login -u %DOCKER_HUB_CREDS_USR% --password-stdin
                    docker push ${DOCKER_IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${DOCKER_IMAGE_NAME}:latest
                """
            }
        }

        stage('Update GitOps Manifests') {
            steps {
                echo "Updating k8s/deployment.yaml with image tag ${IMAGE_TAG}..."
                bat """
                    powershell -Command "(Get-Content k8s/deployment.yaml) -replace 'image: ${DOCKER_IMAGE_NAME}:.*', 'image: ${DOCKER_IMAGE_NAME}:${IMAGE_TAG}' | Set-Content k8s/deployment.yaml"
                    git config user.name "jenkins-bot"
                    git config user.email "jenkins@devops.local"
                    git add k8s/deployment.yaml
                    git commit -m "ci: update image tag to ${IMAGE_TAG} [skip ci]" || exit 0
                    git push https://%GITHUB_TOKEN%@github.com/Hr1thik/iris-mlops-devsecops-api.git HEAD:${GIT_BRANCH}
                """
            }
        }
    }

    post {
        always {
            bat 'docker logout || exit 0'
        }
        success {
            echo "Pipeline succeeded! ArgoCD will automatically detect the new commit and deploy image tag: ${IMAGE_TAG}."
        }
        failure {
            echo "Pipeline failed. Check stage logs for details."
        }
    }
}