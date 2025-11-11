pipeline {
    agent any

    environment {
        PYTHONPATH = "${WORKSPACE}"
        PYTHONUNBUFFERED = "1"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Up Python Environment') {
            steps {
                script {
                    if (isUnix()) {
                        // Mac/Linux: Docker로 의존성 설치 (호스트의 워크스페이스를 컨테이너에 마운트)
                        sh '''
                            docker run --rm \
                              -v "$WORKSPACE":/workspace \
                              -w /workspace \
                              python:3.11 bash -lc "
                                python -m pip install --upgrade pip
                                if [ -f requirements.txt ]; then
                                  pip install -r requirements.txt
                                else
                                  pip install pytest pytest-cov pytest-html
                                fi
                              "
                        '''
                    } else {
                        // Windows: 로컬 venv 사용
                        bat '''
                            @echo off
                            py -3 -m venv venv || python -m venv venv
                            call venv\\Scripts\\activate.bat
                            python -m pip install -U pip
                            if exist requirements.txt (
                                pip install -r requirements.txt
                            ) else (
                                pip install pytest pytest-cov pytest-html
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
                        sh '''
                            docker run --rm \
                              -v "$WORKSPACE":/workspace \
                              -w /workspace \
                              python:3.11 bash -lc "
                                if [ -f requirements.txt ]; then
                                  pip install -r requirements.txt
                                else
                                  pip install pytest pytest-cov pytest-html
                                fi
                                
                                echo '📂 테스트 파일 찾기...'
                                find . -name 'test_*.py' -o -name '*_test.py'
                                
                                echo '🧪 pytest 실행...'
                                if pytest -v \
                                  --junitxml=test-results.xml \
                                  --html=report.html \
                                  --self-contained-html \
                                  --cov=. \
                                  --cov-report=xml:coverage.xml \
                                  --cov-report=html \
                                  --cov-report=term; then
                                  echo '✅ Tests executed successfully.'
                                else
                                  EXIT_CODE=\$?
                                  echo '⚠️ No tests found or tests failed (exit code: '\$EXIT_CODE')'
                                  if [ \$EXIT_CODE -eq 5 ]; then
                                    echo '❌ ERROR: No tests were collected. Check:'
                                    echo '   1. Test files start with test_ or end with _test.py'
                                    echo '   2. Test functions start with test_'
                                    echo '   3. Test files are in the correct location'
                                  fi
                                  exit \$EXIT_CODE
                                fi
                              "
                        '''
                    } else {
                        bat '''
                            @echo off
                            call venv\\Scripts\\activate.bat
                            if pytest -q --junitxml=test-results.xml --html=report.html --cov=. --cov-report=xml:coverage.xml; (
                                echo Tests executed successfully.
                            ) else (
                                echo No tests found or tests failed, check the logs for details.
                            )
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            // 테스트 결과와 리포트 수집 (경로 수정)
            junit allowEmptyResults: true, testResults: '**/test-results.xml'
            archiveArtifacts artifacts: '**/report.html, **/test-results.xml, **/coverage.xml, **/htmlcov/**', allowEmptyArchive: true
        }
    }
}