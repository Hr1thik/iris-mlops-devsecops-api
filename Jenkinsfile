pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDS = credentials('docker-hub-credentials')
        SONAR_TOKEN      = credentials('sonar-token')
        IMAGE_NAME       = 'hr1thik/iris-mlops-api'
        IMAGE_TAG        = "${BUILD_NUMBER}"
    }

    stages {
        stage('SAST - SonarQube Scan') {
            steps {
                withSonarQubeEnv('SonarCloud') {
                    sh 'sonar-scanner'
                }
            }
        }

        stage('SCA - Dependency Scan') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip
                    python3 -m pip install safety
                    safety check -r requirements.txt --continue-on-error
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"
            }
        }

        stage('Container Security Scan (Trivy)') {
            steps {
                sh "trivy image --severity HIGH,CRITICAL --exit-code 0 ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh '''
                    echo "$DOCKER_HUB_CREDS_PSW" | docker login -u "$DOCKER_HUB_CREDS_USR" --password-stdin
                    docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Update GitOps Repo') {
            steps {
                // Jenkins updates the deployment image tag so ArgoCD can sync it
                sh """
                    git clone https://github.com/Hr1thik/iris-mlops-k8s.git
                    cd iris-mlops-k8s
                    sed -i 's|${IMAGE_NAME}:.*|${IMAGE_NAME}:${IMAGE_TAG}|g' deployment.yaml
                    git config user.name "jenkins-bot"
                    git config user.email "jenkins@zoople.local"
                    git commit -am "chore(cd): update image tag to ${IMAGE_TAG}"
                    git push origin main
                """
            }
        }
    }
}