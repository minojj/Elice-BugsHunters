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

        stage('Setup Environment') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "🐧 Unix/Linux/Mac 환경"
                            echo "OS: $(uname -a)"
                            python3 --version || python --version
                        '''
                    } else {
                        bat '''
                            echo 🪟 Windows 환경
                            systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
                            python --version
                        '''
                    }
                }
            }
        }

        stage('Install Browser') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "🌐 Unix/Mac: 브라우저 설치 확인..."
                            
                            # Mac (Homebrew)
                            if command -v brew &> /dev/null; then
                                echo "🍎 macOS 감지"
                                brew list --cask google-chrome || brew install --cask google-chrome || true
                                brew list chromedriver || brew install chromedriver || true
                            # Linux
                            else
                                echo "🐧 Linux 감지"
                                apt-get update
                                apt-get install -y chromium chromium-driver wget ca-certificates \
                                    fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \
                                    libcups2 libdbus-1-3 libgbm1 libgtk-3-0 libnspr4 libnss3 \
                                    libxcomposite1 libxdamage1 libxrandr2 xdg-utils || true
                                
                                ln -sf /usr/bin/chromium /usr/bin/google-chrome || true
                                ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver || true
                                chmod +x /usr/bin/chromedriver || true
                            fi
                            
                            # 설치 확인
                            which google-chrome || which chromium || echo "Chrome 없음"
                            which chromedriver || echo "ChromeDriver 없음"
                        '''
                    } else {
                        bat '''
                            echo 🌐 Windows: Chrome 설치 확인...
                            where chrome.exe || echo Chrome이 설치되어 있지 않습니다
                            where chromedriver.exe || echo ChromeDriver가 설치되어 있지 않습니다
                        '''
                    }
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "🐍 Python 의존성 설치 (Unix/Mac)..."
                            if command -v python3 &> /dev/null; then PYTHON_CMD=python3; else PYTHON_CMD=python; fi
                            rm -rf .venv
                            $PYTHON_CMD -m venv .venv
                            . .venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            # webdriver-manager 강제 제거
                            pip uninstall -y webdriver-manager || true
                        '''
                    } else {
                        bat '''
                            echo 🐍 Python 의존성 설치 (Windows)...
                            if exist .venv rmdir /s /q .venv
                            python -m venv .venv
                            call .venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                            REM webdriver-manager 강제 제거
                            pip uninstall -y webdriver-manager || exit /b 0
                        '''
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            set +e
                            . .venv/bin/activate
                            mkdir -p reports screenshots
                            
                            # Chrome 경로 설정
                            export CHROME_BIN=$(which google-chrome || which chromium || echo "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
                            echo "🌐 Chrome 경로: $CHROME_BIN"
                            
                            # ChromeDriver 경로 설정
                            export PATH="/usr/local/bin:/usr/bin:$PATH"
                            
                            # 테스트 실행
                            pytest tests -v \
                                --junitxml=reports/test-results.xml \
                                --html=reports/report.html \
                                --self-contained-html \
                                --tb=short
                            
                            EXIT_CODE=$?
                            echo "📊 테스트 종료 코드: $EXIT_CODE"
                            ls -lh reports/* 2>/dev/null || true
                            exit $EXIT_CODE
                        '''
                    } else {
                        bat '''
                            call .venv\\Scripts\\activate.bat
                            if not exist reports mkdir reports
                            if not exist screenshots mkdir screenshots
                            
                            REM 테스트 실행
                            pytest tests -v ^
                                --junitxml=reports/test-results.xml ^
                                --html=reports/report.html ^
                                --self-contained-html ^
                                --tb=short
                            
                            if errorlevel 1 (
                                echo ❌ 테스트 실패
                                exit /b 1
                            ) else (
                                echo ✅ 테스트 성공
                            )
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
                    archiveArtifacts artifacts: 'reports/**/*,screenshots/**/*.png',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
                success { 
                    echo '✅ 테스트 성공!' 
                }
                failure { 
                    echo '❌ 테스트 실패' 
                }
            }
        }
    }
}