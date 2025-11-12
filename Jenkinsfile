pipeline {
    agent any

    environment {
        PYTHONPATH = "${WORKSPACE}"
        PYTHONUNBUFFERED = "1"
        HEADLESS = "true"  // Jenkins에서는 항상 headless 모드
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📥 코드 체크아웃 중...'
                checkout scm
            }
        }

        stage('Install System Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        echo '🔧 시스템 의존성 설치 중...'
                        sh '''
                            # Chrome/Chromium 설치 확인
                            if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null; then
                                echo "⚠️ Chrome이 설치되어 있지 않습니다. 설치를 시도합니다..."
                                
                                # macOS
                                if [[ "$OSTYPE" == "darwin"* ]]; then
                                    if command -v brew &> /dev/null; then
                                        brew install --cask google-chrome
                                    else
                                        echo "❌ Homebrew가 필요합니다."
                                        exit 1
                                    fi
                                # Linux
                                else
                                    sudo apt-get update
                                    sudo apt-get install -y chromium-browser chromium-chromedriver
                                fi
                            else
                                echo "✅ Chrome이 이미 설치되어 있습니다."
                            fi
                        '''
                    } else {
                        echo '🪟 Windows 환경: Chrome 설치 확인 생략'
                    }
                }
            }
        }

        stage('Set Up Python Environment') {
            steps {
                script {
                    if (isUnix()) {
                        echo '🐍 Python 가상환경 설정 중 (Unix)...'
                        sh '''
                            # Python3 확인
                            if ! command -v python3 &> /dev/null; then
                                echo "❌ Python3이 설치되어 있지 않습니다."
                                exit 1
                            fi
                            
                            # 가상환경 생성
                            python3 -m venv venv
                            
                            # 가상환경 활성화 및 의존성 설치
                            . venv/bin/activate
                            python -m pip install --upgrade pip
                            
                            if [ -f requirements.txt ]; then
                                pip install -r requirements.txt
                                echo "✅ requirements.txt 설치 완료"
                            else
                                echo "❌ requirements.txt를 찾을 수 없습니다."
                                exit 1
                            fi
                            
                            # 설치된 패키지 확인
                            echo "📦 설치된 패키지 목록:"
                            pip list
                        '''
                    } else {
                        echo '🐍 Python 가상환경 설정 중 (Windows)...'
                        bat '''
                            @echo off
                            echo Python 버전 확인...
                            python --version || py -3 --version
                            
                            echo 가상환경 생성...
                            py -3 -m venv venv || python -m venv venv
                            
                            echo 가상환경 활성화...
                            call venv\\Scripts\\activate.bat
                            
                            echo pip 업그레이드...
                            python -m pip install --upgrade pip
                            
                            if exist requirements.txt (
                                echo requirements.txt 설치 중...
                                pip install -r requirements.txt
                                echo 설치 완료!
                            ) else (
                                echo requirements.txt를 찾을 수 없습니다.
                                exit /b 1
                            )
                            
                            echo 설치된 패키지 목록:
                            pip list
                        '''
                    }
                }
            }
        }

        stage('Verify Test Files') {
            steps {
                script {
                    if (isUnix()) {
                        echo '🔍 테스트 파일 확인 중...'
                        sh '''
                            echo "현재 디렉토리: $(pwd)"
                            echo ""
                            echo "프로젝트 구조:"
                            ls -la
                            echo ""
                            echo "tests 디렉토리 내용:"
                            if [ -d "tests" ]; then
                                ls -la tests/
                                echo ""
                                echo "발견된 테스트 파일:"
                                find tests -name "test_*.py" -o -name "TEST_*.py" -o -name "*_test.py"
                            else
                                echo "❌ tests 디렉토리를 찾을 수 없습니다."
                                exit 1
                            fi
                        '''
                    } else {
                        bat '''
                            @echo off
                            echo 현재 디렉토리: %CD%
                            echo.
                            echo 프로젝트 구조:
                            dir
                            echo.
                            if exist tests (
                                echo tests 디렉토리 내용:
                                dir tests
                            ) else (
                                echo ❌ tests 디렉토리를 찾을 수 없습니다.
                                exit /b 1
                            )
                        '''
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    if (isUnix()) {
                        echo '🧪 테스트 실행 중 (Unix)...'
                        sh '''
                            . venv/bin/activate
                            
                            echo "PYTHONPATH: $PYTHONPATH"
                            echo "현재 디렉토리: $(pwd)"
                            
                            # pytest 실행
                            set +e  # 에러가 발생해도 계속 진행
                            pytest tests/ -v \
                              --junitxml=test-results.xml \
                              --html=report.html \
                              --self-contained-html \
                              --cov=src \
                              --cov-report=xml:coverage.xml \
                              --cov-report=html:htmlcov \
                              --cov-report=term
                            
                            EXIT_CODE=$?
                            set -e
                            
                            if [ $EXIT_CODE -eq 0 ]; then
                                echo "✅ 모든 테스트 통과!"
                            elif [ $EXIT_CODE -eq 1 ]; then
                                echo "⚠️ 일부 테스트 실패"
                            elif [ $EXIT_CODE -eq 5 ]; then
                                echo "❌ 테스트를 찾을 수 없습니다."
                                echo "체크 사항:"
                                echo "  1. tests/ 디렉토리 존재 여부"
                                echo "  2. test_*.py 파일명 패턴"
                                echo "  3. test_ 함수명 패턴"
                                exit 1
                            else
                                echo "❌ pytest 실행 실패 (exit code: $EXIT_CODE)"
                            fi
                            
                            # 리포트 파일 확인
                            echo ""
                            echo "생성된 리포트 파일:"
                            ls -lh test-results.xml report.html coverage.xml 2>/dev/null || echo "일부 리포트 파일 생성 실패"
                            
                            exit $EXIT_CODE
                        '''
                    } else {
                        echo '🧪 테스트 실행 중 (Windows)...'
                        bat '''
                            @echo off
                            call venv\\Scripts\\activate.bat
                            
                            echo PYTHONPATH: %PYTHONPATH%
                            echo 현재 디렉토리: %CD%
                            
                            pytest tests\\ -v ^
                              --junitxml=test-results.xml ^
                              --html=report.html ^
                              --self-contained-html ^
                              --cov=src ^
                              --cov-report=xml:coverage.xml ^
                              --cov-report=html:htmlcov ^
                              --cov-report=term
                            
                            set PYTEST_EXIT=%ERRORLEVEL%
                            
                            if %PYTEST_EXIT% EQU 0 (
                                echo ✅ 모든 테스트 통과!
                            ) else if %PYTEST_EXIT% EQU 1 (
                                echo ⚠️ 일부 테스트 실패
                            ) else if %PYTEST_EXIT% EQU 5 (
                                echo ❌ 테스트를 찾을 수 없습니다.
                                exit /b 1
                            ) else (
                                echo ❌ pytest 실행 실패
                            )
                            
                            echo.
                            echo 생성된 리포트 파일:
                            dir test-results.xml report.html coverage.xml 2>nul
                            
                            exit /b %PYTEST_EXIT%
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            echo '📊 테스트 결과 수집 중...'
            
            // JUnit 테스트 결과
            junit allowEmptyResults: true, testResults: '**/test-results.xml'
            
            // 아티팩트 저장
            archiveArtifacts artifacts: '''
                **/report.html,
                **/test-results.xml,
                **/coverage.xml,
                **/htmlcov/**,
                **/screenshots/**
            ''', allowEmptyArchive: true
            
            // 코드 커버리지 (Cobertura 플러그인 설치 필요)
            script {
                try {
                    publishCoverage adapters: [coberturaAdapter('**/coverage.xml')]
                } catch (Exception e) {
                    echo "⚠️ 코드 커버리지 리포트 생성 실패: ${e.message}"
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