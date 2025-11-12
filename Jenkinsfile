pipeline {
    agent any

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

        stage('Detect OS') {
            steps {
                script {
                    if (isUnix()) {
                        def uname = sh(script: 'uname', returnStdout: true).trim()
                        if (uname == 'Darwin') {
                            env.OS_TYPE = 'macos'
                            echo '🍎 macOS 감지됨'
                        } else {
                            env.OS_TYPE = 'linux'
                            echo '🐧 Linux 감지됨'
                        }
                    } else {
                        env.OS_TYPE = 'windows'
                        echo '🪟 Windows 감지됨'
                    }
                    echo "운영체제: ${env.OS_TYPE}"
                }
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    echo '🔧 환경 설정 중...'
                    if (env.OS_TYPE == 'windows') {
                        bat '''
                            echo 🪟 운영체제: Windows
                            python --version
                            echo 📂 현재 디렉토리: %CD%
                        '''
                    } else {
                        sh '''
                            echo "🐧 운영체제: $(uname -a)"
                            python3 --version
                            echo "📂 현재 디렉토리: $(pwd)"
                        '''
                    }
                }
            }
        }

        stage('Install Browser') {
            steps {
                script {
                    if (env.OS_TYPE == 'linux') {
                        echo '🌐 Chrome 설치 (Linux)...'
                        sh '''
                            # apt 사용 가능 여부 확인
                            if command -v apt-get &> /dev/null; then
                                echo "📦 apt-get 패키지 관리자 사용"
                                
                                # 패키지 업데이트
                                apt-get update
                                
                                # Chrome 관련 의존성 설치
                                apt-get install -y \
                                    wget gnupg ca-certificates \
                                    fonts-liberation libasound2 libatk-bridge2.0-0 \
                                    libatk1.0-0 libc6 libcairo2 libcups2 \
                                    libdbus-1-3 libexpat1 libfontconfig1 libgbm1 \
                                    libglib2.0-0 libgtk-3-0 libnspr4 \
                                    libnss3 libpango-1.0-0 libpangocairo-1.0-0 \
                                    libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
                                    libxcomposite1 libxcursor1 libxdamage1 libxext6 \
                                    libxfixes3 libxi6 libxrandr2 libxrender1 \
                                    libxss1 libxtst6 lsb-release xdg-utils \
                                    unzip curl
                                
                                # Google Chrome 설치
                                wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
                                echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
                                apt-get update
                                apt-get install -y google-chrome-stable
                                
                                google-chrome --version
                                echo "✅ Chrome 설치 완료"
                            else
                                echo "⚠️  apt-get을 사용할 수 없습니다. Chrome을 수동으로 설치해주세요."
                            fi
                        '''
                    } else if (env.OS_TYPE == 'macos') {
                        echo '🌐 Chrome 확인 (macOS)...'
                        sh '''
                            # Homebrew가 설치되어 있는지 확인
                            if ! command -v brew &> /dev/null; then
                                echo "⚠️  Homebrew가 설치되어 있지 않습니다."
                                
                                # Chrome이 이미 설치되어 있는지 확인
                                if [ -d "/Applications/Google Chrome.app" ]; then
                                    echo "✅ Chrome이 이미 설치되어 있습니다."
                                    /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version
                                else
                                    echo "⚠️  Chrome을 수동으로 설치해주세요."
                                    echo "Chrome 다운로드: https://www.google.com/chrome/"
                                fi
                            else
                                # Chrome이 설치되어 있는지 확인
                                if [ ! -d "/Applications/Google Chrome.app" ]; then
                                    echo "Chrome 설치 중..."
                                    brew install --cask google-chrome
                                else
                                    echo "✅ Chrome이 이미 설치되어 있습니다."
                                fi
                                
                                # Chrome 버전 확인
                                /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version
                            fi
                        '''
                    } else {
                        echo '🌐 Chrome 확인 (Windows)...'
                        bat '''
                            where chrome.exe >nul 2>&1
                            if %errorlevel% neq 0 (
                                echo ⚠️  Chrome이 설치되어 있지 않습니다.
                                echo Chrome 다운로드: https://www.google.com/chrome/
                                exit /b 0
                            ) else (
                                echo ✅ Chrome이 설치되어 있습니다.
                                chrome.exe --version
                            )
                        '''
                    }
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                script {
                    if (env.OS_TYPE == 'windows') {
                        bat '''
                            python --version
                            
                            REM venv 재생성
                            if exist .venv rmdir /s /q .venv
                            python -m venv .venv
                            call .venv\\Scripts\\activate.bat
                            
                            REM pip 업그레이드
                            python -m pip install --upgrade pip
                            
                            REM 의존성 설치
                            pip install -r requirements.txt
                            
                            REM 설치 확인
                            pip list | findstr /I "selenium pytest"
                        '''
                    } else {
                        sh '''
                            set -eu
                            python3 -c "import sys; print('Python:', sys.version)"
                            
                            # venv 재생성
                            rm -rf .venv
                            python3 -m venv .venv
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
            }
        }
        
        stage('Verify Project Structure') {
            steps {
                script {
                    echo '🔍 프로젝트 구조 확인 중...'
                    if (env.OS_TYPE == 'windows') {
                        bat '''
                            echo 📂 프로젝트 루트:
                            dir
                            
                            echo.
                            echo 📂 tests 디렉토리:
                            if exist tests (
                                dir tests
                                echo.
                                echo 🔎 발견된 테스트 파일:
                                dir /s /b tests\\test_*.py
                            ) else (
                                echo ❌ tests 디렉토리가 없습니다!
                                exit /b 1
                            )
                        '''
                    } else {
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
        }
              
        stage('Run Tests') {
            steps {
                script {
                    if (env.OS_TYPE == 'windows') {
                        bat '''
                            call .venv\\Scripts\\activate.bat
                            if not exist reports mkdir reports
                            
                            pytest tests -v ^
                                --junitxml=reports/test-results.xml ^
                                --html=reports/report.html ^
                                --self-contained-html ^
                                --tb=short
                            
                            set EXIT_CODE=%errorlevel%
                            dir reports
                            exit /b %EXIT_CODE%
                        '''
                    } else {
                        sh '''
                            set +e
                            . .venv/bin/activate
                            mkdir -p reports
                            
                            # Chrome 경로 설정
                            if [ "${OS_TYPE}" = "macos" ]; then
                                export CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                            else
                                export CHROME_BIN=$(which google-chrome)
                            fi
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
                }
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