pipeline {
    agent {
        docker {
            // Python이 설치된 공식 이미지 사용 (에이전트에 python3가 없음으로 인한 문제 해결)
            image 'python:3.11-slim'
            args '-u root:root'
        }
    }
    
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
                    # 컨테이너 안에서 실행되므로 venv 불필요
                    python3 -m pip install --upgrade pip
                    pip install --no-cache-dir -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    # pytest로 리포트와 커버리지 생성
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
            // Jenkins에 junit/publishHTML/publishCoverage 플러그인이 없을 수 있으므로 아카이브로 대체
            archiveArtifacts artifacts: 'report.html, test-results.xml, coverage.xml', allowEmptyArchive: true
            echo 'Reports archived: report.html, test-results.xml, coverage.xml'
        }
        failure {
            echo 'Tests failed!'
        }
    }
}