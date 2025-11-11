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
                        // Mac/Linux: Docker 사용
                        sh '''
                            docker run --rm -v $WORKSPACE:/workspace python:3.11 bash -c "
                                cd /workspace
                                pip install --upgrade pip
                                if [ -f requirements.txt ]; then
                                    pip install -r requirements.txt
                                else
                                    pip install pytest
                                fi
                            "
                        '''
                    } else {
                        // Windows: venv 사용 (Docker 대신)
                        bat '''
                            @echo off
                            py -3 -m venv venv || python -m venv venv
                            call venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            if exist requirements.txt (
                                pip install -r requirements.txt
                            ) else (
                                pip install pytest
                            )
                        '''
                    }
                }
            }
        }

        stage('Run pytest') {
            steps {
                script {
                    if (isUnix()) {
                        // Mac/Linux: Docker 사용
                        sh '''
                            docker run --rm -v $WORKSPACE:/workspace python:3.11 bash -c "
                                cd /workspace
                                if [ -f requirements.txt ]; then
                                    pip install -r requirements.txt
                                else
                                    pip install pytest
                                fi
                                pytest tests/ --junitxml=pytest-report.xml
                            "
                        '''
                    } else {
                        // Windows: venv 사용
                        bat '''
                            @echo off
                            call venv\\Scripts\\activate.bat
                            pytest tests/ --junitxml=pytest-report.xml
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'pytest-report.xml'
        }
        success {
            echo '테스트 자동화가 성공적으로 완료되었습니다!'
        }
        failure {
            echo '테스트 자동화 중 일부 테스트가 실패했습니다. 리포트를 확인해주세요.'
        }
    }
}