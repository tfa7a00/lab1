pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        CI_LOGS = 'ci_logs'
        IMAGE_NAME = 'lab-2-app'
        PYTHON_EXE = 'C:\\Program Files\\Python312\\python.exe'
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
                    \$python = '${env.PYTHON_EXE}'
                    \$venv = '${env.VENV_DIR}'

                    Write-Host "Creating virtual environment..."
                    & \$python -m venv \$venv --upgrade-deps

                    Write-Host "Bootstrapping pip..."
                    & "\$venv\\Scripts\\python.exe" -m ensurepip --upgrade

                    Write-Host "Upgrading pip and installing dependencies..."
                    & "\$venv\\Scripts\\python.exe" -m pip install --upgrade pip
                    & "\$venv\\Scripts\\python.exe" -m pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                powershell """
                    \$venv = '${env.VENV_DIR}'
                    \$logs = '${env.CI_LOGS}'

                    Write-Host "Running pytest..."
                    New-Item -ItemType Directory -Force -Path \$logs | Out-Null
                    & "\$venv\\Scripts\\pytest.exe" -v test_app.py `
                        2>&1 | Tee-Object -FilePath "\$logs\\pytest.log"
                """
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                powershell """
                    \$venv = '${env.VENV_DIR}'
                    \$logs = '${env.CI_LOGS}'

                    Write-Host "Running Bandit..."
                    New-Item -ItemType Directory -Force -Path \$logs | Out-Null

                    try {
                        & "\$venv\\Scripts\\bandit.exe" -r app -f json `
                            -o "\$logs\\bandit-report.json"
                    } catch {
                        Write-Host "Bandit exited with error code. Continuing..."
                    }
                """
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                powershell """
                    \$venv = '${env.VENV_DIR}'
                    \$logs = '${env.CI_LOGS}'

                    Write-Host "Running Safety..."
                    New-Item -ItemType Directory -Force -Path \$logs | Out-Null

                    try {
                        & "\$venv\\Scripts\\safety.exe" check --json `
                            > "\$logs\\safety-report.json"
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
                    \$logs = '${env.CI_LOGS}'
                    \$image = '${env.IMAGE_NAME}'

                    Write-Host "Running Trivy image scan..."
                    New-Item -ItemType Directory -Force -Path \$logs | Out-Null

                    try {
                        trivy image `
                            --severity CRITICAL,HIGH `
                            --format json `
                            -o "\$logs\\trivy-report.json" `
                            "\$image:latest"
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
            archiveArtifacts artifacts: "\${CI_LOGS}/*.json, \${CI_LOGS}/*.log", allowEmptyArchive: true
            echo "Pipeline finished. Check archived logs for details."
        }
    }
}
