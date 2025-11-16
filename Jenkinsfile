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
                deleteDir()
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                        set -eux
                        echo "🐳 Docker 이미지 빌드 시작"
                        docker builder prune -f || true
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -f Dockerfile .
                        docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                        docker images | head
                    '''
                }
            }
        }

    stage('Run Tests in Container') {
        steps {
            withCredentials([
                usernamePassword(
                    credentialsId: 'login-id',
                    usernameVariable: 'MAIN_EMAIL',
                    passwordVariable: 'MAIN_PASSWORD'
                ),
                usernamePassword(
                    credentialsId: 'sub-id',
                    usernameVariable: 'SUB_EMAIL',
                    passwordVariable: 'SUB_PASSWORD'
                )
            ]) {
                sh '''
                    set -eux

                    echo "➡ PWD:"
                    pwd
                    echo "➡ WORKSPACE:"
                    echo "$WORKSPACE"

                    # 워크스페이스 기준 경로 (Jenkins 컨테이너, 테스트 컨테이너 둘 다 동일하게 사용)
                    REPORT_DIR="reports"
                    SCREENSHOT_DIR="screenshots"

                    echo "🧹 기존 리포트/스크린샷 정리"
                    rm -rf "$REPORT_DIR" "$SCREENSHOT_DIR"
                    mkdir -p "$REPORT_DIR" "$SCREENSHOT_DIR"

                    echo "🐳 테스트 컨테이너 실행 (Jenkins 볼륨 공유)"
                    docker run --rm \
                    --volumes-from elice-jenkins \
                    -w "$WORKSPACE" \
                    --shm-size=2g \
                    -e HEADLESS=true \
                    -e WDM_SKIP=1 \
                    -e CHROME_BIN=/usr/bin/chromium \
                    -e CHROMEDRIVER=/usr/bin/chromedriver \
                    -e MAIN_EMAIL="$MAIN_EMAIL" \
                    -e MAIN_PASSWORD="$MAIN_PASSWORD" \
                    -e SUB_EMAIL="$SUB_EMAIL" \
                    -e SUB_PASSWORD="$SUB_PASSWORD" \
                    ${DOCKER_IMAGE}:latest \
                    pytest tests -v \
                        --junitxml=${REPORT_DIR}/test-results.xml \
                        --html=${REPORT_DIR}/report.html \
                        --self-contained-html \
                        --tb=short

                    echo "📂 docker run 이후 리포트 디렉토리 내용:"
                    ls -lah "$REPORT_DIR" || true

                    echo "📂 docker run 이후 스크린샷 디렉토리 내용:"
                    ls -lah "$SCREENSHOT_DIR" || true
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
                    // WORKSPACE 기준: reports/test-results.xml
                    junit 'reports/test-results.xml'
                } catch (err) {
                    echo "JUnit 리포트를 찾지 못했습니다: ${err}"
                }

                echo "📊 HTML 리포트 게시 시도"
                try {
                    publishHTML(target: [
                        allowMissing:           true,
                        alwaysLinkToLastBuild:  true,
                        keepAll:                true,
                        reportDir:              'reports',
                        reportFiles:            'report.html',
                        reportName:             'Pytest HTML Report'
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

            // 선택: Docker 자원 정리 (원치 않으면 주석 처리)
            sh 'docker system prune -f || true'
        }
    }
}
