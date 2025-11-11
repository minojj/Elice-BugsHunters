pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            agent {
                docker {
                    image 'python:3.11'
                    args '-v $WORKSPACE:/workspace'
                }
            }
            steps {
                sh '''
                    python3 -m pip install --upgrade pip
                    pip install --no-cache-dir -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            agent {
                docker {
                    image 'python:3.11'
                    args '-v $WORKSPACE:/workspace'
                }
            }
            steps {
                sh '''
                    pytest --junitxml=test-results.xml \
                           --html=report.html \
                           --cov=. \
                           --cov-report=xml:coverage.xml \
                           -v
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'report.html, test-results.xml, coverage.xml', allowEmptyArchive: true
            echo 'Reports archived (if present): report.html, test-results.xml, coverage.xml'
        }
        failure {
            echo 'Tests failed!'
        }
    }
}