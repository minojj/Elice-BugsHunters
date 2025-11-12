pipeline {
    agent {
        docker {
            image 'python:3.11-bookworm'   // 다중 아키텍처 지원
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
                script {
                    echo '🐍 Python 의존성 설치 중...'
                    sh '''
                        # Python3 확인
                        set -eu
                        python -c "import sys; print('Python:', sys.version)"
                        python -c "print('Try importing ssl...'); import ssl; print('ssl OK:', ssl.OPENSSL_VERSION)" || echo "❌ ssl 모듈 로드 실패"
                        python -m venv .venv
                        .venv/bin/python -c "print('Venv ssl test'); import ssl; print('ssl OK (venv):', ssl.OPENSSL_VERSION)" || echo "❌ venv ssl 실패"
                        .venv/bin/pip install --upgrade pip
                        .venv/bin/pip install -r requirements.txt
                    '''
                }
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
        stage('Python Env') {
            steps {
                sh '''
                  set -eux
                  python -m venv .venv
                  . .venv/bin/activate
                  pip install --upgrade pip
                  pip install --upgrade pip
                  python -m pip install -r requirements.txt
                  python -m venv .venv
                  .venv/bin/pip install --upgrade pip
                  .venv/bin/pip install -r requirements.txt
                  # python -c "import pyautogui..." 라인 삭제
                script {
                    echo '🧪 테스트 실행 중...'
                    sh '''
                        set +e
                        . .venv/bin/activate
                        mkdir -p reports
                        pytest tests -v \
                            --junitxml=reports/test-results.xml \
                            --html=reports/report.html \
                        mkdir -p reports
                        .venv/bin/pytest tests -v \
                            --junitxml=reports/test-results.xml \
                            --html=reports/report.html \
                            --self-contained-html --tb=short
                        EXIT_CODE=$?
                        echo "리포트 목록:"
                        ls -lh reports/test-results.xml reports/report.html || true
                        exit $EXIT_CODE
                        '''

    post {
        always {
            script {
                echo '📊 테스트 결과 수집 중...'
                
                // JUnit 테스트 결과
                try {
                    junit allowEmptyResults: true, testResults: '**/test-results.xml'
                } catch (Exception e) {
                    echo "⚠️ JUnit 결과 처리 실패: ${e.message}"
                }
                
                // HTML 리포트 발행
                try {
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'report.html',
                        reportName: 'Pytest HTML Report',
                        reportTitles: 'Test Report'
                    ])
                } catch (Exception e) {
                    echo "⚠️ HTML 리포트 발행 실패: ${e.message}"
                }
                
                // 아티팩트 저장
                try {
                    archiveArtifacts artifacts: '''
                        **/report.html,
                        **/test-results.xml,
                        **/screenshots/**/*.png
                    ''', allowEmptyArchive: true, fingerprint: true
                } catch (Exception e) {
                    echo "⚠️ 아티팩트 저장 실패: ${e.message}"
                }
            }
        }
        
        success {
            echo '✅ 빌드 성공!'
        }
        
        failure {
            echo '❌ 빌드 실패!'
        }
        
        unstable {
            echo '⚠️ 빌드 불안정 (일부 테스트 실패)'
        }
    }
}