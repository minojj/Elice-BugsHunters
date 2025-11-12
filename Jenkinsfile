pipeline {
    agent {
        docker {
            image 'python:3.11'
            args '-u root:root --shm-size=2g'
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
                        echo "🐍 Python 버전: $(python3 --version)"
                        echo "📂 현재 디렉토리: $(pwd)"
                    '''
                }
            }
        }

        stage('Install Chrome & ChromeDriver') {
            steps {
                script {
                    echo '🌐 Chrome 및 ChromeDriver 설치 중...'
                    sh '''
                        # 패키지 업데이트
                        apt-get update
                        
                        # Chrome 관련 의존성 설치
                        apt-get install -y \
                            wget \
                            gnupg \
                            ca-certificates \
                            fonts-liberation \
                            libasound2 \
                            libatk-bridge2.0-0 \
                            libatk1.0-0 \
                            libc6 \
                            libcairo2 \
                            libcups2 \
                            libdbus-1-3 \
                            libexpat1 \
                            libfontconfig1 \
                            libgbm1 \
                            libglib2.0-0 \
                            libgtk-3-0 \
                            libnspr4 \
                            libnss3 \
                            libpango-1.0-0 \
                            libpangocairo-1.0-0 \
                            libstdc++6 \
                            libx11-6 \
                            libx11-xcb1 \
                            libxcb1 \
                            libxcomposite1 \
                            libxcursor1 \
                            libxdamage1 \
                            libxext6 \
                            libxfixes3 \
                            libxi6 \
                            libxrandr2 \
                            libxrender1 \
                            libxss1 \
                            libxtst6 \
                            lsb-release \
                            xdg-utils \
                            unzip \
                            curl
                        
                        # Google Chrome 설치 (최신 방식)
                        wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
                        apt-get install -y /tmp/google-chrome.deb || true
                        rm /tmp/google-chrome.deb
                        
                        # 설치 확인
                        google-chrome --version || echo "⚠️  Chrome 설치 실패 (ARM64 아키텍처)"
                        
                        # ARM64용 Chromium 설치 (대안)
                        if ! command -v google-chrome &> /dev/null; then
                            echo "🔄 Chromium 설치 중 (ARM64 대안)..."
                            apt-get install -y chromium chromium-driver
                            
                            # chromium 심볼릭 링크 생성
                            ln -sf /usr/bin/chromium /usr/bin/google-chrome || true
                            chromium --version
                        fi
                        
                        echo "✅ 브라우저 설치 완료"
                    '''
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                sh '''
                    set -eu
                    python -c "import sys; print('Python:', sys.version)"
                    
                    # venv 재생성
                    rm -rf .venv
                    python -m venv .venv
                    . .venv/bin/activate
                    
                    # pip 업그레이드
                    python -m pip install --upgrade pip
                    
                    # 의존성 설치
                    pip install -r requirements.txt
                    
                    # 설치 확인
                    pip list | grep -E 'selenium|pytest' || true
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
                    '''
                }
            }
        }
              
        stage('Run Tests') {
            steps {
                sh '''
                    set +e
                    . .venv/bin/activate
                    mkdir -p reports
                    
                    # Chrome 경로 확인
                    export CHROME_BIN=$(which google-chrome || which chromium)
                    echo "Chrome 경로: $CHROME_BIN"
                    
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