pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t elice-bugshunters:test .'
            }
        }
        stage('Run Tests') {
            steps {
                sh 'docker run --rm elice-bugshunters:test'
            }
        }
        // 필요하다면 아래에 배포 스테이지 추가
    }
}
