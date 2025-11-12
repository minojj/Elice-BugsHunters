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
                            libgcc1 \
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
                            xdg-utils
                        
                        # Google Chrome 설치
                        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
                        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
                        apt-get update
                        apt-get install -y google-chrome-stable
                        
                        # 설치 확인
                        google-chrome --version
                        which google-chrome
                        
                        # ChromeDriver는 selenium이 자동으로 관리하도록 설정
                        echo "✅ Chrome 설치 완료"
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
                    
                    # selenium-manager가 ChromeDriver를 자동으로 다운로드할 수 있도록 webdriver-manager 제거
                    # (selenium 4.6+ 는 자동 드라이버 관리 기능 내장)
                    
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
                    export CHROME_BIN=$(which google-chrome)
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