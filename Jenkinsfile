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
                    usernamePassword(credentialsId: 'login-id', usernameVariable: 'MAIN_EMAIL', passwordVariable: 'MAIN_PASSWORD'),
                    usernamePassword(credentialsId: 'sub-id',   usernameVariable: 'SUB_EMAIL',  passwordVariable: 'SUB_PASSWORD')
                ]) {
                    sh '''
                        set -eux

                        REPORT_DIR_HOST="${WORKSPACE}/reports"
                        REPORT_DIR_CONT="/app/reports"

                        rm -rf "${REPORT_DIR_HOST}"
                        mkdir -p "${REPORT_DIR_HOST}"

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
                        -v "${REPORT_DIR_HOST}:${REPORT_DIR_CONT}" \
                        elice-bugshunters:latest \
                        tests -v \
                            --junitxml=${REPORT_DIR_CONT}/test-results.xml \
                            --html=${REPORT_DIR_CONT}/report.html \
                            --self-contained-html \
                            --tb=short

                        echo "📂 Jenkins 워크스페이스 리포트 디렉토리 내용:"
                        ls -lah "${REPORT_DIR_HOST}"
                    '''
                    }
            }
        }
    
    }
    

    post {
        always {
            script {
                try {
                    junit 'reports/test-results.xml'
                } catch (err) {
                    echo "JUnit 리포트를 찾지 못했습니다: ${err}"
                }

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
            }
        }
    }

}
