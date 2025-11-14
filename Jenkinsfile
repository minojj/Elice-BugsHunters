pipeline {
    agent any

    environment {
        REPORT_DIR       = "reports"
        SCREENSHOT_DIR   = "screenshots"
        DOCKER_IMAGE     = "elice-bugshunters"
        PYTHONUNBUFFERED = "1"
        HEADLESS         = "true"
        WDM_LOCAL        = "1"
        WDM_CACHE        = "${WORKSPACE}/.wdm"
        HOME             = "${WORKSPACE}"
        PYTHONPATH       = "${WORKSPACE}:${PYTHONPATH}"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                        docker builder prune -f || true
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -f Dockerfile .
                        docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }

        stage('Run Tests in Container') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'login-id', usernameVariable: 'MAIN_EMAIL', passwordVariable: 'MAIN_PASSWORD'),
                    usernamePassword(credentialsId: 'sub-id',   usernameVariable: 'SUB_EMAIL',  passwordVariable: 'SUB_PASSWORD')
                ]) {
                    sh '''
                        set -eux

                        echo "➡ PWD in shell:"
                        pwd
                        echo "➡ WORKSPACE env:"
                        echo "${WORKSPACE}"

                        REPORT_DIR_HOST="${WORKSPACE}/reports"
                        REPORT_DIR_CONT="/app/reports"

                        echo "🧹 기존 리포트 정리"
                        rm -rf "${REPORT_DIR_HOST}"
                        mkdir -p "${REPORT_DIR_HOST}"

                        echo "🐳 docker run"
                        docker run --rm \
                        --shm-size=2g \
                        -e CHROME_BIN=/usr/bin/chromium \
                        -e CHROMEDRIVER=/usr/bin/chromedriver \
                        -e MAIN_EMAIL="${MAIN_EMAIL}" \
                        -e MAIN_PASSWORD="${MAIN_PASSWORD}" \
                        -e SUB_EMAIL="${SUB_EMAIL}" \
                        -e SUB_PASSWORD="${SUB_PASSWORD}" \
                        -v "${REPORT_DIR_HOST}:${REPORT_DIR_CONT}" \
                        ${DOCKER_IMAGE}:latest \
                        tests -v \
                            --junitxml=${REPORT_DIR_CONT}/test-results.xml \
                            --html=${REPORT_DIR_CONT}/report.html \
                            --self-contained-html \
                            --tb=short

                        echo "📂 WORKSPACE reports 내용:"
                        ls -lah "${REPORT_DIR_HOST}" || true
                    '''
                }
            }
        }

    }

    post {
        always {
            script {
                echo "📦 JUnit 리포트 수집 시도"
                try {
                    junit 'reports/test-results.xml'
                } catch (err) {
                    echo "JUnit 리포트를 찾지 못했습니다: ${err}"
                }

                echo "📊 HTML 리포트 게시 시도"
                try {
                    publishHTML(target: [
                        allowMissing:          true,
                        alwaysLinkToLastBuild: true,
                        keepAll:               true,
                        reportDir:             'reports',
                        reportFiles:           'report.html',
                        reportName:            'Pytest HTML Report'
                    ])
                } catch (err) {
                    echo "HTML 리포트를 게시하지 못했습니다: ${err}"
                }

                def reportExists = fileExists('reports/report.html')
                echo "리포트 파일 존재: ${reportExists}"

                if (reportExists) {
                    archiveArtifacts(
                        artifacts: 'reports/**/*,screenshots/**/*',
                        allowEmptyArchive: true,
                        fingerprint: true
                    )
                    echo "✅ 리포트/스크린샷 아카이브 완료"
                    echo "📊 HTML 리포트: ${BUILD_URL}artifact/reports/report.html"
                } else {
                    echo "❌ 리포트 파일이 생성되지 않았습니다"
                    echo "테스트가 실패했거나 pytest-html 플러그인이 없을 수 있습니다"
                }
            }

            sh 'docker system prune -f || true'
        }
    }
}
