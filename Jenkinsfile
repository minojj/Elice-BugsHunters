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
                    # python3 존재 여부 확인
                    if command -v python3 >/dev/null 2>&1; then
                        python3 -m pip install --upgrade pip
                        pip install --no-cache-dir -r requirements.txt
                    else
                        echo "ERROR: python3 not found on this agent. Install Python 3 or run pipeline on an agent with Python (or enable Docker)."
                        exit 127
                    fi
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    # python3/pytest 유무 확인 후 실행
                    if command -v python3 >/dev/null 2>&1 && python3 -m pytest --version >/dev/null 2>&1; then
                        pytest --junitxml=test-results.xml \
                               --html=report.html \
                               --cov=. \
                               --cov-report=xml:coverage.xml \
                               -v
                    else
                        echo "ERROR: pytest not available. Ensure requirements.txt includes pytest and was installed successfully."
                        exit 1
                    fi
                '''
            }
        }
    }
    
    post {
        always {
            // archiveArtifacts는 FilePath(context)가 필요하므로 node 블록에서 실행
            node {
                archiveArtifacts artifacts: 'report.html, test-results.xml, coverage.xml', allowEmptyArchive: true
            }
            echo 'Reports archived (if present): report.html, test-results.xml, coverage.xml'
        }
        failure {
            echo 'Tests failed!'
        }
    }
}