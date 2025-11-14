pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = "1"
        HEADLESS = "true"
        WDM_LOCAL = "1"
        WDM_CACHE = "${WORKSPACE}/.wdm"
        HOME = "${WORKSPACE}"
        PYTHONPATH = "${WORKSPACE}:${PYTHONPATH}"
        
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
                            command -v python3 || true
                            command -v python || true
                        '''
                    } else {
                        bat '''
                            echo 🪟 Windows 환경
                            systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
                            where python || echo python not found
                        '''
                    }
                }
            }
        }
        stage('Bootstrap System (Linux only)') {
            when { expression { return isUnix() } }
            steps {
                sh '''
                    set -e
                    if ! command -v python3 >/dev/null 2>&1; then
                      echo "[setup] Installing python3, venv, pip..."
                      apt-get update -y
                      DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-venv python3-pip
                      ln -sf /usr/bin/python3 /usr/bin/python || true
                    else
                      echo "[setup] python3 already installed"
                    fi

                    # Selenium 실행용 브라우저/드라이버
                    if ! command -v chromium >/dev/null 2>&1 && ! command -v google-chrome >/dev/null 2>&1; then
                      echo "[setup] Installing Chromium & chromedriver..."
                      DEBIAN_FRONTEND=noninteractive apt-get install -y chromium chromium-driver fonts-liberation tzdata || true
                    else
                      echo "[setup] Chromium/Chrome already present"
                    fi

                    python3 --version || true
                    python  --version || true
                    which chromium || which google-chrome || true
                    which chromedriver || true
                '''
            }
        }
        stage('Install Python Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "🐍 Python 의존성 설치 (Unix/Linux 컨테이너)"
                            if command -v python3 &> /dev/null; then PYTHON_CMD=python3; else PYTHON_CMD=python; fi
                            rm -rf .venv
                            $PYTHON_CMD -m venv .venv
                            . .venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                            echo 🐍 Python 의존성 설치 (Windows)
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

        
        stage('Run Tests') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'login-id',
                        usernameVariable: 'MAIN_EMAIL',
                        passwordVariable: 'MAIN_PASSWORD'
                    ),
                    usernamePassword(
                        credentialsId: 'sub-id',
                        usernameVariable: 'SUB_EMAIL',
                        passwordVariable: 'SUB_PASSWORD'
                    )
                ]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set +e
                                . .venv/bin/activate
                                mkdir -p reports screenshots "${WDM_CACHE}"

                                echo "[info] Jenkins 환경변수 사용"
                                
                                export CHROME_BIN=$(which google-chrome || which chromium || which chromium-browser || true)
                                echo "🌐 Chrome 경로: ${CHROME_BIN:-<auto>}"

                                export PATH="/usr/local/bin:/usr/bin:$PATH"
                                which chromedriver || true

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