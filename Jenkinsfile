pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Repository checked out successfully"
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    echo "🔧 Setting up Python environment..."
                    python3 --version
                    pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "📦 Installing dependencies..."
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    else
                        pip install pytest selenium
                    fi
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "🧪 Running acceptance tests..."
                    pytest tests/TEST_AC.py -v --tb=short --junit-xml=test-results.xml
                '''
            }
        }
    }

    post {
        always {
            echo "📊 Publishing test results..."
            junit(testResults: 'test-results.xml', allowEmptyResults: true)
        }
        success {
            echo "✅ Build successful!"
        }
        failure {
            echo "❌ Build failed!"
        }
    }
}
