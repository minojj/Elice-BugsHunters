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
                            # 캐시 정리 후 재빌드
                            docker builder prune -f || true
                            docker build --no-cache -t elice-bugshunters:${BUILD_NUMBER} -f Dockerfile .
                            docker tag elice-bugshunters:${BUILD_NUMBER} elice-bugshunters:latest
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
                            --tb=short || true

                        # 리포트 파일 확인
                        echo "📊 생성된 파일 목록:"
                        ls -lah "${REPORT_DIR}/" || echo "리포트 디렉토리가 비어있습니다"
                        
                        # 권한 수정
                        if [ -f "${REPORT_DIR}/report.html" ]; then
                            chmod -R 755 "${REPORT_DIR}"
                            echo "✅ report.html 생성 성공"
                        else
                            echo "❌ report.html 생성 실패"
                        fi
                        
                    '''
                }
            }
            post {
                always {
                    script {
                        // 리포트 파일 존재 확인
                        def reportExists = fileExists('reports/report.html')
                        echo "리포트 파일 존재: ${reportExists}"
                        
                        if (reportExists) {
                            // Artifacts 아카이브
                            archiveArtifacts(
                                artifacts: 'reports/**/*',
                                allowEmptyArchive: true,
                                fingerprint: true
                            )
                            echo "✅ 리포트 아카이브 완료"
                            echo "📊 HTML 리포트: ${BUILD_URL}artifact/reports/report.html"
                        } else {
                            echo "❌ 리포트 파일이 생성되지 않았습니다"
                            echo "테스트가 실패했거나 pytest-html 플러그인이 없을 수 있습니다"
                        }
                    }
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

