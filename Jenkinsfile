pipeline {
  agent {
    docker {
      image 'python:3.11-slim'
      args '-u 0:0'   // 퍼미션 이슈 피하고 싶으면 유지, 아니면 제거 가능
    }
  }
  options { timestamps() }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Install Dependencies') {
      steps {
        sh '''
          python3 -V
          [ ! -d venv ] && python3 -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        '''
      }
    }
    stage('Run Tests') {
      steps {
        sh '''
          . venv/bin/activate
          pytest -q || { echo "Tests failed"; exit 1; }
        '''
      }
    }
  }
  post {
    always { echo 'Build finished' }
  }
}
