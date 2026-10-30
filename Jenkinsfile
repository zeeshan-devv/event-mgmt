pipeline {
    agent any

    environment {
        PATH = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh 'python3 -m py_compile event-service/app.py booking-service/app.py'
            }
        }

        stage('Build Images') {
            steps {
                sh '''
                    docker build -t event-service:${BUILD_NUMBER} event-service
                    docker build -t booking-service:${BUILD_NUMBER} booking-service
                    docker build -t frontend:${BUILD_NUMBER} frontend
                '''
            }
        }

        stage('Load Images into Cluster') {
            steps {
                sh '''
                    minikube image load event-service:${BUILD_NUMBER}
                    minikube image load booking-service:${BUILD_NUMBER}
                    minikube image load frontend:${BUILD_NUMBER}
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    for f in k8s/*.yaml; do
                        sed "s/BUILD_TAG/${BUILD_NUMBER}/g" $f | kubectl apply -f -
                    done
                    kubectl rollout status deployment/postgres --timeout=180s
                    kubectl rollout status deployment/event-service --timeout=180s
                    kubectl rollout status deployment/booking-service --timeout=180s
                    kubectl rollout status deployment/frontend --timeout=180s
                '''
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    kubectl get pods
                    kubectl get svc
                    kubectl get pvc
                    curl -s --retry 5 --retry-delay 3 --retry-connrefused http://$(minikube ip):30080/api/events
                '''
            }
        }
    }

    post {
        success { echo 'Deployment successful' }
        failure { echo 'Pipeline failed, check console output' }
    }
}
