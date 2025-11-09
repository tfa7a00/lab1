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

        stage('Setup CI Logs Directory') {
            steps {
                powershell """
                    Write-Host "Creating CI logs directory..."
                    New-Item -ItemType Directory -Force -Path "${env.CI_LOGS}" | Out-Null
                """
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                powershell """
                    \$ErrorActionPreference = 'Stop'
                    
                    Write-Host "Removing old virtual environment if it exists..."
                    if (Test-Path "${env.VENV_DIR}") {
                        Remove-Item -Recurse -Force "${env.VENV_DIR}"
                    }
                    
                    Write-Host "Creating fresh virtual environment..."
                    & "${env.PYTHON_EXE}" -m venv "${env.VENV_DIR}"
                    if (\$LASTEXITCODE -ne 0) { exit \$LASTEXITCODE }

                    Write-Host "Activating virtual environment and installing pip..."
                    \$venvPython = "${env.VENV_DIR}\\Scripts\\python.exe"
                    
                    # Use the venv python directly to upgrade pip
                    Write-Host "Upgrading pip..."
                    & \$venvPython -m pip install --upgrade pip
                    if (\$LASTEXITCODE -ne 0) { exit \$LASTEXITCODE }

                    Write-Host "Installing setuptools and wheel..."
                    & \$venvPython -m pip install --upgrade setuptools wheel
                    if (\$LASTEXITCODE -ne 0) { exit \$LASTEXITCODE }

                    Write-Host "Installing dependencies from requirements.txt..."
                    & \$venvPython -m pip install -r requirements.txt
                    if (\$LASTEXITCODE -ne 0) { exit \$LASTEXITCODE }
                """
            }
        }

        stage('Run Tests') {
            steps {
                powershell """
                    \$ErrorActionPreference = 'Stop'
                    
                    Write-Host "Running pytest..."
                    & "${env.VENV_DIR}\\Scripts\\python.exe" -m pytest -v test_app.py `
                        2>&1 | Tee-Object -FilePath "${env.CI_LOGS}\\pytest.log"
                    
                    if (\$LASTEXITCODE -ne 0) {
                        Write-Host "Tests failed with exit code \$LASTEXITCODE"
                        exit \$LASTEXITCODE
                    }
                """
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                powershell """
                    Write-Host "Running Bandit..."
                    
                    & "${env.VENV_DIR}\\Scripts\\python.exe" -m bandit -r app -f json `
                        -o "${env.CI_LOGS}\\bandit-report.json"
                    
                    \$banditExitCode = \$LASTEXITCODE
                    Write-Host "Bandit completed with exit code: \$banditExitCode"
                    
                    # Bandit exit codes: 0 = no issues, 1 = issues found
                    # We'll continue but warn if issues found
                    if (\$banditExitCode -eq 1) {
                        Write-Host "WARNING: Bandit found security issues. Check the report."
                    }
                """
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                powershell """
                    Write-Host "Running Safety check..."
                    
                    # Safety may require authentication in newer versions
                    # Capture both stdout and stderr
                    & "${env.VENV_DIR}\\Scripts\\python.exe" -m safety check --json `
                        2>&1 | Tee-Object -FilePath "${env.CI_LOGS}\\safety-report.json"
                    
                    \$safetyExitCode = \$LASTEXITCODE
                    Write-Host "Safety completed with exit code: \$safetyExitCode"
                    
                    # Exit codes: 0 = clean, 64 = vulnerabilities, 1 = error (auth/other)
                    if (\$safetyExitCode -eq 64) {
                        Write-Host "WARNING: Safety found vulnerabilities. Check the report."
                    } elseif (\$safetyExitCode -eq 1) {
                        Write-Host "WARNING: Safety check failed (possibly due to authentication requirement)."
                        Write-Host "Consider using 'safety check --continue-on-error' or configuring Safety API key."
                        Write-Host "Continuing pipeline..."
                    }
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                powershell """
                    \$ErrorActionPreference = 'Stop'
                    
                    Write-Host "Building Docker image..."
                    docker compose build
                    if (\$LASTEXITCODE -ne 0) {
                        Write-Host "Docker build failed with exit code \$LASTEXITCODE"
                        exit \$LASTEXITCODE
                    }
                    
                    Write-Host "Docker image built successfully."
                """
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                powershell """
                    Write-Host "Running Trivy image scan..."
                    
                    # Get the actual image name from docker compose
                    \$imageName = docker compose config --images 2>&1 | Out-Null
                    \$imageName = docker compose config --images
                    if ([string]::IsNullOrWhiteSpace(\$imageName)) {
                        Write-Host "WARNING: Could not determine image name from docker compose."
                        Write-Host "Attempting to scan ${env.IMAGE_NAME}:latest"
                        \$imageName = "${env.IMAGE_NAME}:latest"
                    }
                    
                    Write-Host "Scanning image: \$imageName"
                    
                    trivy image `
                        --severity CRITICAL,HIGH `
                        --format json `
                        -o "${env.CI_LOGS}\\trivy-report.json" `
                        \$imageName
                    
                    \$trivyExitCode = \$LASTEXITCODE
                    Write-Host "Trivy completed with exit code: \$trivyExitCode"
                    
                    # Trivy exit codes: 0 = no vulnerabilities, non-zero = vulnerabilities found
                    if (\$trivyExitCode -ne 0) {
                        Write-Host "WARNING: Trivy found vulnerabilities. Check the report."
                        Write-Host "You may want to fix these before deploying to production."
                        # Uncomment the line below to fail the build on vulnerabilities
                        # exit \$trivyExitCode
                    }
                """
            }
        }

        stage('Deploy Application') {
            steps {
                powershell """
                    \$ErrorActionPreference = 'Stop'
                    
                    Write-Host "Deploying Docker container..."
                    docker compose up -d
                    if (\$LASTEXITCODE -ne 0) {
                        Write-Host "Docker deployment failed with exit code \$LASTEXITCODE"
                        exit \$LASTEXITCODE
                    }
                    
                    Write-Host "Application deployed successfully."
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
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed. Check logs for errors."
        }
    }
}