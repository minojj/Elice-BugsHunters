pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = "1"
        HEADLESS = "true"
        WDM_LOCAL = "1"
        WDM_CACHE = "${WORKSPACE}/.wdm"
        HOME = "${WORKSPACE}"
        PYTHONPATH = "${WORKSPACE}:${PYTHONPATH}"
        REPORT_DIR = "reports"
        SCREENSHOT_DIR = "screenshots"
        DOCKER_IMAGE = "elice-bugshunters"
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            pytest tests -v \
                                --junitxml=reports/test-results.xml \
                                --html=reports/report.html \
                                --self-contained-html \
                                --tb=short

                            EXIT_CODE=$?
                            echo "📊 테스트 종료 코드: $EXIT_CODE"

                            echo "=== 컨테이너 안에서 reports 디렉토리 내용 확인 ==="
                            pwd
                            ls -R
                            ls -lh reports || echo "reports 디렉토리 없음"
                            ls -lh reports/report.html || echo "report.html 없음"

                            # 🔥 Jenkins 워크스페이스로 리포트 복사 + 권한 풀기
                            mkdir -p "$WORKSPACE/reports"
                            cp -r reports/* "$WORKSPACE/reports/" || true
                            chmod -R 777 "$WORKSPACE/reports" || true

                            exit $EXIT_CODE
                        '''
                    } else {
                        bat '''
                            docker builder prune -f || exit 0
                            docker build --no-cache -t elice-bugshunters:%BUILD_NUMBER% -f Dockerfile .
                            docker tag elice-bugshunters:%BUILD_NUMBER% elice-bugshunters:latest
                        '''
                    }
                }
            }
        }

        stage('Run Tests in Container') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'login-id', usernameVariable: 'MAIN_EMAIL', passwordVariable: 'MAIN_PASSWORD'),
                    usernamePassword(credentialsId: 'sub-id',  usernameVariable: 'SUB_EMAIL',  passwordVariable: 'SUB_PASSWORD')
                ]) {
                    sh '''
                        rm -rf "${REPORT_DIR}"
                        mkdir -p "${REPORT_DIR}"

                        docker run --rm \
                          --shm-size=2g \
                          -e HEADLESS=true \
                          -e WDM_SKIP=1 \
                          -e CHROME_BIN=/usr/bin/chromium \
                          -e CHROMEDRIVER=/usr/bin/chromedriver \
                          -e WDM_CACHE=/app/.wdm \
                          -e MAIN_EMAIL="${MAIN_EMAIL}" \
                          -e MAIN_PASSWORD="${MAIN_PASSWORD}" \
                          -e SUB_EMAIL="${SUB_EMAIL}" \
                          -e SUB_PASSWORD="${SUB_PASSWORD}" \
                          -v "${PWD}/.wdm:/app/.wdm" \
                          -v "${PWD}/${REPORT_DIR}:/app/${REPORT_DIR}" \
                          elice-bugshunters:latest \
                          tests -v \
                            --junitxml=${REPORT_DIR}/test-results.xml \
                            --html=${REPORT_DIR}/report.html \
                            --self-contained-html \
                            --tb=short
                        chmod -R 755 "${REPORT_DIR}"
                        
                    '''
                }
            }
            post {
                always {
                    script {
                        // HTML 리포트 퍼블리시 (에러 무시)
                        try {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: false,
                                keepAll: true,
                                reportDir: 'reports',
                                reportFiles: 'report.html',
                                reportName: 'Pytest HTML Report',
                                reportTitles: '',
                                includes: '**/*',
                                useWrapperFileDirectly: true
                            ])
                        } catch (Exception e) {
                            echo "HTML 리포트 퍼블리시 실패: ${e.message}"
                        }
                    }
                    
                    // Artifacts로 대체 (항상 성공)
                    archiveArtifacts(
                        artifacts: 'reports/**/*',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                }
            }
        }
    }
    
    post {
        always {
            // 빌드 후 Docker 정리
            sh 'docker system prune -f || true'
        }
    }
}

