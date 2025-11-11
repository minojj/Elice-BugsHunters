pipeline {
    agent {
        docker {
            image 'python:3.11-slim'  // 또는 필요한 버전
            args '-u 0:0'             // (선택) 퍼미션 이슈 있으면
        }
    }
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Install Dependencies') {
      steps {
        sh '''
          python3 -V
          python3 -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }
    stage('Run Tests') {
      steps {
        sh '''
          . venv/bin/activate
          pytest -q
        '''
      }
    }
  }



    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    if [ ! -d venv ]; then
                        python3 -m venv venv
                    fi
                    . venv/bin/activate
                    pip install --upgrade pip
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                    pip install pytest selenium
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest tests/test_ac.py -v
                '''
            }
        }
    }

    post {
        always {
            echo "Build finished"
        }
    }

    