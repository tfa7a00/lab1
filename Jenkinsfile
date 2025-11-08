pipeline {
    agent any

    environment {
        // Python and Docker
        //PYTHON_IMAGE = 'python:3.9-slim' // only relevant if using docker later
        IMAGE_NAME = 'devsecops-flask'
        VENV_PATH = '.\\venv'
    }

    stages {
        stage('Checkout') {
            steps {
                // Pull the code from GitHub
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Create Python virtual environment
                    bat "python -m venv ${VENV_PATH}"
                    // Upgrade pip and install requirements
                    bat "${VENV_PATH}\\Scripts\\pip.exe install --upgrade pip"
                    bat "${VENV_PATH}\\Scripts\\pip.exe install -r requirements.txt"
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run tests with pytest
                    bat "${VENV_PATH}\\Scripts\\pytest.exe"
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    // Run Bandit for static code analysis (mark as UNSTABLE if issues)
                    catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                        bat "${VENV_PATH}\\Scripts\\bandit.exe -r ."
                    }
                }
            }
        }

        stage('Check Dependency Vulnerabilities (Safety)') {
            steps {
                script {
                    bat "${VENV_PATH}\\Scripts\\safety.exe check -r requirements.txt"
                }
            }
        }

        stage('Build & Scan Docker Image') {
            steps {
                script {
                    // Build Docker image
                    bat "docker-compose build"
                    // Scan the Docker image with Trivy
                    // Make sure Trivy is installed on your Windows agent
                    bat "trivy image ${IMAGE_NAME}:latest || echo 'Trivy scan failed'"
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    bat "docker-compose up -d"
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace after build
            cleanWs()
        }
        failure {
            // Optional: send notification if build fails
            echo "Build failed! Check logs."
        }
    }
}
