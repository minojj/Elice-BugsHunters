pipeline {
    agent {
        docker {
            image 'python:3.11'   // 다중 아키텍처 지원
            args '-u root:root'            // root 로 패키지 설치
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

        stage('Setup Environment') {
            steps {
                script {
                    echo '🔧 환경 설정 중...'
                    sh '''
                        echo "🐧 운영체제: $(uname -a)"
                        echo "🐍 Python 버전: $(python3 --version 2>&1 || echo 'Python3 없음')"
                        echo "📂 현재 디렉토리: $(pwd)"
                        echo "📝 디렉토리 내용:"
                        ls -la
                    '''
                }
            }
        }

        stage('Install Chrome & ChromeDriver') {
            steps {
                script {
                    echo '🌐 Chrome 및 ChromeDriver 설치 중...'
                    sh '''
                        # 패키지 목록 업데이트
                        apt-get update || echo "⚠️ apt-get update 실패 (권한 문제 가능)"
                        
                        # Chrome 설치
                        if ! command -v google-chrome >/dev/null 2>&1; then
                            echo "⚠️ Chrome이 설치되어 있지 않습니다. Chromium을 설치합니다."
                            apt-get install -y chromium || echo "⚠️ Chromium 설치 실패"
                        else
                            echo "✅ Chrome이 이미 설치되어 있습니다."
                            google-chrome --version
                        fi
                        
                        # ChromeDriver 설치
                        if ! command -v chromedriver >/dev/null 2>&1; then
                            echo "⚠️ ChromeDriver가 없습니다. 설치를 시도합니다."
                            apt-get install -y chromium-chromedriver || echo "⚠️ ChromeDriver 설치 실패"
                        else
                            echo "✅ ChromeDriver가 이미 설치되어 있습니다."
                            chromedriver --version
                        fi
                    '''
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                sh '''
                    set -eu
                    python -c "import sys; print('Python:', sys.version)"
                    python -c "import ssl; print('SSL:', ssl.OPENSSL_VERSION)"
                    
                    # 기존 venv 완전 제거
                    rm -rf .venv
                    
                    # venv 재생성 (--without-pip 없이 기본 방식)
                    python -m venv .venv
                    
                    # venv 활성화
                    . .venv/bin/activate
                    
                    # pip 업그레이드
                    python -m pip install --upgrade pip
                    
                    # 의존성 설치
                    pip install -r requirements.txt
                    
                    # 설치 확인
                    pip list | grep -E 'selenium|pytest|webdriver' || true
                '''
            }
        }
        
        stage('Verify Project Structure') {
            steps {
                script {
                    echo '🔍 프로젝트 구조 확인 중...'
                    sh '''
                        echo "📂 프로젝트 루트:"
                        ls -la
                        
                        echo ""
                        echo "📂 tests 디렉토리:"
                        if [ -d "tests" ]; then
                            ls -la tests/
                            echo ""
                            echo "🔎 발견된 테스트 파일:"
                            find tests -name "test_*.py" -type f
                        else
                            echo "❌ tests 디렉토리가 없습니다!"
                            exit 1
                        fi
                        
                        echo ""
                        echo "📂 src 디렉토리:"
                        if [ -d "src" ]; then
                            ls -la src/
                        else
                            echo "⚠️ src 디렉토리가 없습니다."
                        fi
                        
                        echo ""
                        echo "📄 필수 파일 확인:"
                        for file in conftest.py pytest.ini requirements.txt; do
                            if [ -f "$file" ]; then
                                echo "✅ $file 존재"
                            else
                                echo "⚠️ $file 없음"
                            fi
                        done
                    '''
                }
            }
        }
        
              
        stage('Run Tests') {
            steps {
                sh '''
                    set +e
                    mkdir -p reports
                    pytest tests -v \
                        --junitxml=reports/test-results.xml \
                        --html=reports/report.html \
                        --self-contained-html --tb=short
                    EXIT_CODE=$?
                    ls -lh reports/* || true
                    exit $EXIT_CODE
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/test-results.xml'
                    publishHTML([
                        reportDir: 'reports',
                        reportFiles: 'report.html',
                        reportName: 'Pytest Report',
                        keepAll: true,
                        allowMissing: true
                    ])
                    archiveArtifacts artifacts: 'reports/**/*,**/screenshots/**/*.png',
                                     allowEmptyArchive: true, fingerprint: true
                }
                success { echo '✅ 성공' }
                failure { echo '❌ 실패' }
            }
        }
    }
}   