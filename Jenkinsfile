pipeline {
    agent any

    environment {
        // Python and Docker
        //PYTHON_IMAGE = 'python:3.9-slim' // only relevant if using docker later 
        // Python path - LocalSystem may not access user directories
        // Option 1: Use 'py' launcher (if available to LocalSystem)
        // Option 2: Use full path (if LocalSystem can access it)
        // Option 3: Install Python system-wide (C:\Program Files\Python311\)
        PYTHON_CMD = 'py'
        PYTHON_FULL_PATH = 'C:\\Users\\ADIB\\AppData\\Local\\Programs\\Python\\Python311\\python.exe'
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

        stage('Find Python') {
            steps {
                script {
                    // Try to find Python using PowerShell (most reliable for LocalSystem)
                    def pythonExe = null
                    
                    // Use PowerShell to find Python - works better for LocalSystem
                    def psScript = '''
                        $found = $null
                        # Try 'py' launcher first (best for service accounts)
                        $py = Get-Command py -ErrorAction SilentlyContinue
                        if ($py) { 
                            # Test if py launcher actually works
                            $test = & py --version 2>&1
                            if ($LASTEXITCODE -eq 0) {
                                $found = "py"
                            }
                        }
                        
                        if (-not $found) {
                            # Try 'python' command
                            $python = Get-Command python -ErrorAction SilentlyContinue
                            if ($python) { 
                                $test = & python --version 2>&1
                                if ($LASTEXITCODE -eq 0) {
                                    $found = $python.Path
                                }
                            }
                        }
                        
                        if (-not $found) {
                            # Try common system locations (accessible to service accounts)
                            $paths = @(
                                "C:\\Program Files\\Python311\\python.exe",
                                "C:\\Program Files\\Python312\\python.exe",
                                "C:\\Program Files\\Python313\\python.exe",
                                "C:\\Program Files (x86)\\Python311\\python.exe",
                                "C:\\Python311\\python.exe",
                                "C:\\Python312\\python.exe"
                            )
                            foreach ($path in $paths) {
                                if (Test-Path $path) {
                                    # Verify it's actually executable
                                    $test = & $path --version 2>&1
                                    if ($LASTEXITCODE -eq 0) {
                                        $found = $path
                                        break
                                    }
                                }
                            }
                        }
                        
                        if ($found) { 
                            Write-Output $found 
                        } else { 
                            Write-Output "NOT_FOUND" 
                        }
                    '''
                    
                    try {
                        def psOutput = powershell(script: psScript, returnStdout: true).trim()
                        if (psOutput && psOutput != "NOT_FOUND") {
                            pythonExe = psOutput
                            echo "Found Python: ${pythonExe}"
                            
                            // Verify the Python executable works before proceeding
                            if (pythonExe == "py") {
                                // Test py launcher
                                def testResult = bat(script: "py --version", returnStdout: true, returnStatus: true)
                                if (testResult != 0) {
                                    error("Python launcher 'py' found but not working. Please install Python system-wide.")
                                }
                            } else {
                                // Test full path
                                def testResult = bat(script: "\"${pythonExe}\" --version", returnStdout: true, returnStatus: true)
                                if (testResult != 0) {
                                    error("Python found at ${pythonExe} but not executable. Please check permissions.")
                                }
                            }
                        } else {
                            error("Python not found! Please install Python system-wide (e.g., C:\\Program Files\\Python311\\) or ensure 'py' launcher is available.")
                        }
                    } catch (Exception e) {
                        error("Failed to find Python: ${e.getMessage()}. Please install Python system-wide or ensure 'py' launcher is available.")
                    }
                    
                    // Store in environment variable for later stages
                    env.PYTHON_EXE = pythonExe
                    echo "Will use Python: ${env.PYTHON_EXE}"
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Create Python virtual environment
                    // Using Python found in previous stage
                    def pythonCmd = (env.PYTHON_EXE == "py") ? "py" : "\"${env.PYTHON_EXE}\""
                    bat "${pythonCmd} -m venv ${VENV_PATH}"
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