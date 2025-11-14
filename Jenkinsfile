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
      stage('Checkout') { steps { checkout scm } }

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
                  mkdir -p reports screenshots
                  docker run --rm \
                    -e MAIN_EMAIL="${MAIN_EMAIL}" \
                    -e MAIN_PASSWORD="${MAIN_PASSWORD}" \
                    -e SUB_EMAIL="${SUB_EMAIL}" \
                    -e SUB_PASSWORD="${SUB_PASSWORD}" \
                    -e HEADLESS=true \
                    -v "${PWD}/reports:/app/reports" \
                    -v "${PWD}/screenshots:/app/screenshots" \
                    elice-bugshunters:latest \
                    tests -v \
                      --junitxml=reports/test-results.xml \
                      --html=reports/report.html \
                      --self-contained-html \
                      --tb=short
                '''
              } else {
                bat '''
                  if not exist reports mkdir reports
                  if not exist screenshots mkdir screenshots
                  docker run --rm ^
                    -e MAIN_EMAIL="%MAIN_EMAIL%" ^
                    -e MAIN_PASSWORD="%MAIN_PASSWORD%" ^
                    -e SUB_EMAIL="%SUB_EMAIL%" ^
                    -e SUB_PASSWORD="%SUB_PASSWORD%" ^
                    -e HEADLESS=true ^
                    -v "%CD%\\reports:/app/reports" ^
                    -v "%CD%\\screenshots:/app/screenshots" ^
                    elice-bugshunters:latest ^
                    tests -v ^
                      --junitxml=reports/test-results.xml ^
                      --html=reports/report.html ^
                      --self-contained-html ^
                      --tb=short
                '''
              }
            }
          }
        }
        post {
          always {
            junit allowEmptyResults: true, testResults: 'reports/test-results.xml'
            publishHTML([
              allowMissing: true,
              alwaysLinkToLastBuild: true,
              keepAll: true,
              reportDir: 'reports',
              reportFiles: 'report.html',
              reportName: 'Pytest Report'
            ])
            archiveArtifacts artifacts: 'reports/**/*,screenshots/**/*.png', allowEmptyArchive: true, fingerprint: true
          }
        }
      }
    }
}

