pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = "1"
        HEADLESS         = "true"
        WDM_LOCAL        = "1"
        WDM_CACHE        = "${WORKSPACE}/.wdm"
        HOME             = "${WORKSPACE}"
        PYTHONPATH       = "${WORKSPACE}:${PYTHONPATH}"

        REPORT_DIR       = "reports"
        SCREENSHOT_DIR   = "screenshots"
        DOCKER_IMAGE     = "elice-bugshunters"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -f Dockerfile .
                        docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Run Tests in Container') {
            steps {
                withCredentials([
                    // TODO: 실제 Jenkins 크리덴셜 ID로 바꿔주세요
                    usernamePassword(credentialsId: 'login-id', usernameVariable: 'MAIN_EMAIL', passwordVariable: 'MAIN_PASSWORD'),
                    usernamePassword(credentialsId: 'sub-id',   usernameVariable: 'SUB_EMAIL',  passwordVariable: 'SUB_PASSWORD')
                ]) {
                    sh '''
                        
                        rm -rf "${WORKSPACE}/${REPORT_DIR}" "${WORKSPACE}/${SCREENSHOT_DIR}"
                        mkdir -p "${WORKSPACE}/${REPORT_DIR}" "${WORKSPACE}/${SCREENSHOT_DIR}"

                        
                        docker run --rm \
                          --shm-size=2g \
                          -e HEADLESS=true \
                          -e WDM_SKIP=1 \
                          -e CHROME_BIN=/usr/bin/chromium \
                          -e CHROMEDRIVER=/usr/bin/chromedriver \
                          -e MAIN_EMAIL="${MAIN_EMAIL}" \
                          -e MAIN_PASSWORD="${MAIN_PASSWORD}" \
                          -e SUB_EMAIL="${SUB_EMAIL}" \
                          -e SUB_PASSWORD="${SUB_PASSWORD}" \
                          -v "${WORKSPACE}/${REPORT_DIR}:/app/${REPORT_DIR}" \
                          -v "${WORKSPACE}/${SCREENSHOT_DIR}:/app/${SCREENSHOT_DIR}" \
                          ${DOCKER_IMAGE}:latest \
                          pytest tests -v \
                            --junitxml=${REPORT_DIR}/test-results.xml \
                            --html=${REPORT_DIR}/report.html \
                            --self-contained-html \
                            --tb=short

                        echo "📂 생성된 리포트 파일 목록"
                        ls -lah "${WORKSPACE}/${REPORT_DIR}" || true
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo "📦 JUnit 리포트 수집 시도"
                // JUnit 테스트 결과 수집 (없어도 빌드 실패는 막기)
                try {
                    junit "${REPORT_DIR}/test-results.xml"
                } catch (err) {
                    echo "JUnit 리포트를 찾지 못했습니다: ${err}"
                }

                echo "📊 HTML 리포트 게시 시도"
                try {
                    publishHTML(target: [
                        allowMissing:          true,
                        alwaysLinkToLastBuild: true,
                        keepAll:               true,
                        reportDir:             "${REPORT_DIR}",
                        reportFiles:           "report.html",
                        reportName:            "Pytest HTML Report"
                    ])
                } catch (err) {
                    echo "HTML 리포트를 게시하지 못했습니다: ${err}"
                }

                // 리포트/스크린샷 아카이브
                def reportExists = fileExists("${REPORT_DIR}/report.html")
                echo "리포트 파일 존재: ${reportExists}"

                if (reportExists) {
                    archiveArtifacts(
                        artifacts: "${REPORT_DIR}/**/*,${SCREENSHOT_DIR}/**/*",
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                    echo "✅ 리포트/스크린샷 아카이브 완료"
                    echo "📊 HTML 리포트: ${BUILD_URL}artifact/${REPORT_DIR}/report.html"
                } else {
                    echo "❌ 리포트 파일이 생성되지 않았습니다"
                    echo "테스트가 실패했거나 pytest-html 플러그인이 없을 수 있습니다"
                }
            }

            // 선택: Docker 자원 정리 (원치 않으면 주석 처리)
            sh 'docker system prune -f || true'
        }
    }
}
