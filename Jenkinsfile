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
            steps { 
                checkout scm 
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            docker build -t elice-bugshunters:${BUILD_NUMBER} -f Dockerfile .
                            docker tag elice-bugshunters:${BUILD_NUMBER} elice-bugshunters:latest
                        '''
                    } else {
                        bat '''
                            docker build -t elice-bugshunters:%BUILD_NUMBER% -f Dockerfile .
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
                    script {
                        if (isUnix()) {
                            sh '''
                                mkdir -p "${REPORT_DIR}" "${SCREENSHOT_DIR}" ".wdm"
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
                                  -v "${PWD}/${SCREENSHOT_DIR}:/app/${SCREENSHOT_DIR}" \
                                  elice-bugshunters:latest \
                                  tests -v -n auto \
                                    --junitxml=${REPORT_DIR}/test-results.xml \
                                    --html=${REPORT_DIR}/report.html \
                                    --self-contained-html \
                                    --tb=short \
                                    --maxfail=5
                            '''
                        } else {
                            bat '''
                                if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"
                                if not exist "%SCREENSHOT_DIR%" mkdir "%SCREENSHOT_DIR%"
                                if not exist ".wdm" mkdir ".wdm"
                                docker run --rm ^
                                  --shm-size=2g ^
                                  -e HEADLESS=true ^
                                  -e WDM_SKIP=1 ^
                                  -e CHROME_BIN=/usr/bin/chromium ^
                                  -e CHROMEDRIVER=/usr/bin/chromedriver ^
                                  -e WDM_CACHE=/app/.wdm ^
                                  -e MAIN_EMAIL=%MAIN_EMAIL% ^
                                  -e MAIN_PASSWORD=%MAIN_PASSWORD% ^
                                  -e SUB_EMAIL=%SUB_EMAIL% ^
                                  -e SUB_PASSWORD=%SUB_PASSWORD% ^
                                  -v "%CD%\\.wdm:/app/.wdm" ^
                                  -v "%CD%\\%REPORT_DIR%:/app/%REPORT_DIR%" ^
                                  -v "%CD%\\%SCREENSHOT_DIR%:/app/%SCREENSHOT_DIR%" ^
                                  elice-bugshunters:latest ^
                                  tests -v -n auto ^
                                    --junitxml=%REPORT_DIR%/test-results.xml ^
                                    --html=%REPORT_DIR%/report.html ^
                                    --self-contained-html ^
                                    --tb=short ^
                                    --maxfail=5
                            '''
                        }
                    }
                }
            }
            post {
                always {
                    // 1️⃣ JUnit XML 리포트 퍼블리시
                    junit(
                        allowEmptyResults: true,
                        testResults: 'reports/test-results.xml',
                        skipPublishingChecks: false
                    )
                    
                    // 2️⃣ HTML 리포트 퍼블리시
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'report.html',
                        reportName: 'Pytest HTML Report',
                        reportTitles: 'Test Execution Report'
                    ])
                    
                    // 3️⃣ 스크린샷 및 리포트 아카이브
                    archiveArtifacts(
                        artifacts: 'reports/**/*,screenshots/**/*.png',
                        allowEmptyArchive: true,
                        fingerprint: true,
                        onlyIfSuccessful: false
                    )
                }
                success {
                    echo '✅ 모든 테스트 통과!'
                    script {
                        // 테스트 통계 출력
                        def testResults = junit 'reports/test-results.xml'
                        echo """
╔════════════════════════════════════════╗
║        테스트 실행 결과 요약           ║
╠════════════════════════════════════════╣
║ 총 테스트: ${testResults.totalCount}
║ 성공: ${testResults.passCount}
║ 실패: ${testResults.failCount}
║ 건너뜀: ${testResults.skipCount}
║ 성공률: ${testResults.totalCount > 0 ? String.format('%.2f', (testResults.passCount / testResults.totalCount * 100)) : 0}%
╚════════════════════════════════════════╝
                        """
                    }
                }
                failure {
                    echo '❌ 테스트 실패 - 리포트를 확인하세요'
                    script {
                        def testResults = junit 'reports/test-results.xml'
                        echo """
╔════════════════════════════════════════╗
║        테스트 실패 상세 정보           ║
╠════════════════════════════════════════╣
║ 총 테스트: ${testResults.totalCount}
║ 성공: ${testResults.passCount}
║ 실패: ${testResults.failCount}
║ 건너뜀: ${testResults.skipCount}
║ 
║ 📊 HTML 리포트: ${BUILD_URL}Pytest_20HTML_20Report/
║ 📸 스크린샷: ${BUILD_URL}artifact/screenshots/
╚════════════════════════════════════════╝
                        """
                    }
                }
                unstable {
                    echo '⚠️  일부 테스트 실패'
                }
            }
        }
    }

    post {
        always {
            script {
                // 빌드 완료 시간 기록
                def duration = currentBuild.duration / 1000
                def minutes = (duration / 60).intValue()
                def seconds = (duration % 60).intValue()
                
                echo """
╔════════════════════════════════════════╗
║           빌드 완료 정보               ║
╠════════════════════════════════════════╣
║ 빌드 번호: #${BUILD_NUMBER}
║ 소요 시간: ${minutes}분 ${seconds}초
║ 상태: ${currentBuild.currentResult}
║ 
║ 📋 리포트 링크:
║ • JUnit: ${BUILD_URL}testReport/
║ • HTML: ${BUILD_URL}Pytest_20HTML_20Report/
║ • Artifacts: ${BUILD_URL}artifact/
╚════════════════════════════════════════╝
                """
            }
            
            // Docker 정리
            script {
                if (isUnix()) {
                    sh 'docker system prune -f || true'
                } else {
                    bat 'docker system prune -f || exit 0'
                }
            }
        }
        success {
            // 성공 시 추가 작업 (선택)
            script {
                echo '🎉 CI/CD 파이프라인 성공!'
            }
        }
        failure {
            // 실패 시 추가 작업 (선택)
            script {
                echo '🚨 CI/CD 파이프라인 실패 - 관리자에게 알림'
                // 여기에 Slack/이메일 알림 추가 가능
            }
        }
    }
}

