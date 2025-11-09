pipeline {
    agent any

    environment {
        CI_LOGS = 'ci_logs'
        IMAGE_NAME = 'lab-2-app'
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                checkout scm
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                powershell """
                    \$python = 'C:\\Program Files\\Python312\\python.exe'
                    \$venv = 'venv'

                    Write-Host "Creating virtual environment..."
                    & \$python -m venv \$venv --upgrade-deps

                    Write-Host "Bootstrapping pip..."
                    & "\$venv\\Scripts\\python.exe" -m ensurepip --upgrade

                    Write-Host "Upgrading pip, setuptools, wheel..."
                    & "\$venv\\Scripts\\python.exe" -m pip install --upgrade pip setuptools wheel

                    Write-Host "Installing dependencies from requirements.txt..."
                    & "\$venv\\Scripts\\python.exe" -m pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                powershell """
                    \$venv = 'venv'
                    Write-Host "Running pytest..."
                    New-Item -ItemType Directory -Force -Path '${CI_LOGS}' | Out-Null
                    & "\$venv\\Scripts\\pytest.exe" -v test_app.py 2>&1 | Tee-Object -FilePath "${CI_LOGS}\\pytest.log"
                """
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                powershell """
                    \$venv = 'venv'
                    Write-Host "Running Bandit..."
                    New-Item -ItemType Directory -Force -Path '${CI_LOGS}' | Out-Null
                    try {
                        & "\$venv\\Scripts\\bandit.exe" -r app -f json -o "${CI_LOGS}\\bandit-report.json"
                    } catch {
                        Write-Host "Bandit exited with error code. Continuing..."
                    }
                """
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                powershell """
                    \$venv = 'venv'
                    Write-Host "Running Safety..."
                    New-Item -ItemType Directory -Force -Path '${CI_LOGS}' | Out-Null
                    try {
                        & "\$venv\\Scripts\\safety.exe" check --json > "${CI_LOGS}\\safety-report.json"
                    } catch {
                        Write-Host "Safety exited with error code. Continuing..."
                    }
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                powershell """
                    Write-Host "Building Docker image..."
                    try {
                        docker compose build
                    } catch {
                        Write-Host "Docker build failed. Continuing..."
                    }
                """
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                powershell """
                    Write-Host "Running Trivy image scan..."
                    New-Item -ItemType Directory -Force -Path '${CI_LOGS}' | Out-Null
                    try {
                        trivy image --severity CRITICAL,HIGH --format json -o "${CI_LOGS}\\trivy-report.json" "${IMAGE_NAME}:latest"
                    } catch {
                        Write-Host "Trivy exited with error. Continuing..."
                    }
                """
            }
        }

        stage('Deploy Application') {
            steps {
                powershell """
                    Write-Host "Deploying Docker container..."
                    try {
                        docker compose up -d
                    } catch {
                        Write-Host "Docker run failed. Continuing..."
                    }
                """
            }
        }
    }

    post {
        always {
            echo "Archiving CI logs..."
            archiveArtifacts artifacts: "${CI_LOGS}/*.json, ${CI_LOGS}/*.log", allowEmptyArchive: true
            echo "Pipeline finished. Check archived logs for details."
        }
    }
}
