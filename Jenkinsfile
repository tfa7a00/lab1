pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
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
                powershell '''
                    Write-Host "Creating virtual environment..."
                    python -m venv $env:VENV_DIR

                    Write-Host "Upgrading pip and installing dependencies..."
                    & "$env:VENV_DIR\\Scripts\\pip.exe" install --upgrade pip
                    & "$env:VENV_DIR\\Scripts\\pip.exe" install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                powershell '''
                    Write-Host "Running pytest..."

                    New-Item -ItemType Directory -Force -Path $env:CI_LOGS | Out-Null

                    & "$env:VENV_DIR\\Scripts\\pytest.exe" -v test_app.py `
                        2>&1 | Tee-Object -FilePath "$env:CI_LOGS\\pytest.log"
                '''
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                powershell '''
                    Write-Host "Running Bandit..."

                    New-Item -ItemType Directory -Force -Path $env:CI_LOGS | Out-Null

                    # Run Bandit and ignore non-zero exit code
                    try {
                        & "$env:VENV_DIR\\Scripts\\bandit.exe" -r app -f json `
                            -o "$env:CI_LOGS\\bandit-report.json"
                    } catch {
                        Write-Host "Bandit returned a non-zero exit code, continuing..."
                    }
                '''
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                powershell '''
                    Write-Host "Running Safety..."

                    New-Item -ItemType Directory -Force -Path $env:CI_LOGS | Out-Null

                    try {
                        & "$env:VENV_DIR\\Scripts\\safety.exe" check --json `
                            > "$env:CI_LOGS\\safety-report.json"
                    } catch {
                        Write-Host "Safety returned a non-zero exit code, continuing..."
                    }
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                powershell '''
                    Write-Host "Building Docker image..."
                    try {
                        docker compose build
                    } catch {
                        Write-Host "Docker build returned a non-zero exit code, continuing..."
                    }
                '''
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                powershell '''
                    Write-Host "Running Trivy image scan..."

                    New-Item -ItemType Directory -Force -Path $env:CI_LOGS | Out-Null

                    try {
                        trivy image `
                            --severity CRITICAL,HIGH `
                            --format json `
                            -o "$env:CI_LOGS\\trivy-report.json" `
                            "$env:IMAGE_NAME:latest"
                    } catch {
                        Write-Host "Trivy returned a non-zero exit code, continuing..."
                    }
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                powershell '''
                    Write-Host "Deploying Docker container..."
                    try {
                        docker compose up -d
                    } catch {
                        Write-Host "docker compose up failed, continuing..."
                    }
                '''
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
//ignore