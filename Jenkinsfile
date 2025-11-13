pipeline {
    agent {
         dockerfile {
            filename 'Dockerfile'
            args '--shm-size=2g'
     }
   }

    environment {
        PYTHONUNBUFFERED = "1"
        HEADLESS = "true"
        WDM_LOCAL = "1"
        WDM_CACHE = "${WORKSPACE}/.wdm"
        HOME = "${WORKSPACE}"
        PYTHONPATH = "${WORKSPACE}:${PYTHONPATH}"
        CHROMEDRIVER = "/usr/bin/chromedriver" // 시스템 드라이버 고정
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

        // Dockerfile에서 이미 chromium/chromedriver 설치됨 → 이 stage는 있어도 무관
        stage('Install Browser') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "🌐 브라우저 설치 확인 (컨테이너에 이미 설치됨)"
                            which chromium || true
                            which chromedriver || true
                        '''
                    } else {
                        bat '''
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
                            # webdriver-manager는 테스트에서 import할 수 있으므로 제거하지 않음
                        '''
                    } else {
                        bat '''
                            echo 🐍 Python 의존성 설치 (Windows)...
                            if exist .venv rmdir /s /q .venv
                            python -m venv .venv
                            call .venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }
            }
        }
        stage('Generate and Load .env') {
            steps {
        withCredentials([
            usernamePassword(
                credentialsId: 'login-id',
                usernameVariable: 'MAIN_EMAIL',
                passwordVariable: 'MAIN_PASSWORD'
            )
        ]) {
            sh '''
                echo "[info] generate .env file..."
                umask 077
                cat >.env <<EOF
MAIN_EMAIL=${MAIN_EMAIL}
MAIN_PASSWORD=${MAIN_PASSWORD}
EOF
                echo "[info] .env created at $(pwd)/.env"

                echo "[info] using .env file..."
                set -a
                if [ -f .env ]; then
                set +a
                # echo "loaded MAIN_EMAIL: $MAIN_EMAIL"  # 이메일 노출 방지를 위해 로그 출력 제거
            '''
                echo "loaded MAIN_EMAIL: $MAIN_EMAIL"
            '''
        }
    }
}
        stage('Run Tests') {
            steps {
                script {
                        sh '''
                            set +e
                            . .venv/bin/activate
                            mkdir -p reports screenshots "${WDM_CACHE}"

                            # .env 파일에서 환경변수 로드
                            if [ -f .env ]; then
                                set -a
                                . .env
                                set +a
                                echo "[info] .env 환경변수 로드 완료"
                            fi

                            # Chrome 경로 설정(있으면만)
                            export CHROME_BIN=$(which google-chrome || which chromium || which chromium-browser || true)
                            echo "🌐 Chrome 경로: ${CHROME_BIN:-<auto>}"

                            # 시스템 chromedriver 우선 (Dockerfile에서 /usr/bin/chromedriver 설치됨)
                            export PATH="/usr/local/bin:/usr/bin:$PATH"
                            which chromedriver || true

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
                        '''
                    } else {
                        bat '''
                            call .venv\\Scripts\\activate.bat
                            if not exist reports mkdir reports
                            if not exist screenshots mkdir screenshots

                            pytest tests -v ^
                                --junitxml=reports/test-results.xml ^
                                --html=reports/report.html ^
                                --self-contained-html ^
                                --tb=short

                            if errorlevel 1 exit /b 1
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
            }
        }
    }
}