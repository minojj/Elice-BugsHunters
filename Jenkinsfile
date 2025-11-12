pipeline {
    agent {
        docker {
            image 'selenium/standalone-chrome:latest'
            args '--shm-size=2g'
        }
    }

    environment {
        PYTHONUNBUFFERED = "1"
        HEADLESS = "true"
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📥 코드 체크아웃 중...'
                checkout scm
            }
        }

        stage('Install Python & Dependencies') {
            steps {
                sh '''
                    # Python 설치 확인
                    python3 --version || (apt-get update && apt-get install -y python3 python3-pip python3-venv)
                    
                    # venv 생성
                    python3 -m venv .venv
                    . .venv/bin/activate
                    
                    # pip 업그레이드 및 의존성 설치
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    echo "✅ Python 환경 설정 완료"
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    set +e
                    . .venv/bin/activate
                    mkdir -p reports
                    
                    pytest tests -v \
                        --junitxml=reports/test-results.xml \
                        --html=reports/report.html \
                        --self-contained-html \
                        --tb=short
                    
                    EXIT_CODE=$?
                    ls -lh reports/* || true
                    exit $EXIT_CODE
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/test-results.xml'
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'report.html',
                        reportName: 'Pytest Report'
                    ])
                    archiveArtifacts artifacts: 'reports/**/*,**/screenshots/**/*.png',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
                success { echo '✅ 테스트 성공' }
                failure { echo '❌ 테스트 실패' }
            }
        }
    }
}