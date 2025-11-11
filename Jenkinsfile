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
            steps {
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    source venv/bin/activate
                    pytest --junitxml=test-results.xml \
                           --html=report.html \
                           --cov=. \
                           --cov-report=xml \
                           -v
                '''
            }
        }
    }
    
    post {
        always {
            junit 'test-results.xml'
            publishHTML([
                reportDir: '.',
                reportFiles: 'report.html',
                reportName: 'Test Report'
            ])
            publishCoverage adapters: [coberturaAdapter('coverage.xml')]
        }
        failure {
            echo 'Tests failed!'
        }
    }
}