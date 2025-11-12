pipeline {
    agent any

    environment {
        PYTHONPATH = "${WORKSPACE}"
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
                        if ! command -v python3 >/dev/null 2>&1; then
                            echo "❌ Python3이 설치되어 있지 않습니다."
                            exit 1
                        fi
                        
                        python3 --version
                        
                        # pip 업그레이드
                        python3 -m pip install --upgrade pip --user
                        
                        # requirements.txt 설치
                        if [ -f requirements.txt ]; then
                            echo "📦 requirements.txt 설치 중..."
                            python3 -m pip install -r requirements.txt --user
                            echo "✅ 설치 완료"
                        else
                            echo "❌ requirements.txt를 찾을 수 없습니다."
                            exit 1
                        fi
                        
                        # 설치 확인
                        echo "📋 설치된 패키지:"
                        python3 -m pip list --user | grep -E "selenium|pytest|webdriver"
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
                            find tests -name "*.py" -type f
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
                script {
                    echo '🧪 테스트 실행 중...'
                    sh '''
                        set +e  # 테스트 실패해도 계속 진행
                        
                        echo "📍 PYTHONPATH: $PYTHONPATH"
                        echo "📍 작업 디렉토리: $(pwd)"
                        
                        # pytest 실행
                        python3 -m pytest tests/ -v \
                            --junitxml=reports/test-results.xml \  // 경로 수정
                            --html=reports/report.html \  // 경로 수정
                            --self-contained-html \
                            --tb=short \
                            || EXIT_CODE=$?
                        
                        # Exit code 처리
                        if [ -z "$EXIT_CODE" ]; then
                            echo "✅ 모든 테스트 통과!"
                            EXIT_CODE=0
                        elif [ $EXIT_CODE -eq 1 ]; then
                            echo "⚠️ 일부 테스트 실패 (exit code: 1)"
                        elif [ $EXIT_CODE -eq 5 ]; then
                            echo "❌ 테스트를 찾을 수 없습니다 (exit code: 5)"
                            echo ""
                            echo "🔍 체크사항:"
                            echo "  1. tests/ 디렉토리 존재 확인"
                            echo "  2. test_*.py 또는 TEST_*.py 파일 존재"
                            echo "  3. test_ 로 시작하는 함수 존재"
                            echo "  4. __init__.py 파일 존재"
                            exit 1
                        else
                            echo "❌ pytest 실행 오류 (exit code: $EXIT_CODE)"
                        fi
                        
                        # 생성된 리포트 확인
                        echo ""
                        echo "📊 생성된 리포트 파일:"
                        ls -lh test-results.xml report.html 2>/dev/null || echo "일부 파일 생성 실패"
                        
                        exit $EXIT_CODE
                    '''
                }
            }
        }
    }

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