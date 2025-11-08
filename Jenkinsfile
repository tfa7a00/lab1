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
                    echo "========================================="
                    echo "Searching for Python installation..."
                    echo "========================================="
                    
                    def pythonExe = null
                    def pythonVersion = null
                    
                    // Use PowerShell to find Python and get full path
                    def psScript = '''
                        $found = $null
                        $version = $null
                        $ErrorActionPreference = "SilentlyContinue"
                        
                        # Try 'py' launcher first
                        try {
                            $result = & py --version 2>&1
                            if ($?) {
                                $version = $result
                                # Get full path of py launcher
                                $pyPath = (Get-Command py -ErrorAction SilentlyContinue).Source
                                if ($pyPath) {
                                    $found = $pyPath
                                } else {
                                    $found = "py"
                                }
                            }
                        } catch {}
                        
                        # If py launcher didn't work, try 'python' command
                        if (-not $found) {
                            try {
                                $cmd = Get-Command python -ErrorAction SilentlyContinue
                                if ($cmd) {
                                    $result = & python --version 2>&1
                                    if ($?) {
                                        $version = $result
                                        $found = $cmd.Path
                                    }
                                }
                            } catch {}
                        }
                        
                        # Try system-wide installation paths
                        if (-not $found) {
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
                                    try {
                                        $result = & $path --version 2>&1
                                        if ($?) {
                                            $version = $result
                                            $found = $path
                                            break
                                        }
                                    } catch {}
                                }
                            }
                        }
                        
                        if ($found) {
                            Write-Output "PATH:$found"
                            Write-Output "VERSION:$version"
                        } else {
                            Write-Output "NOT_FOUND"
                        }
                    '''
                    
                    try {
                        def psOutput = powershell(script: psScript, returnStdout: true).trim()
                        def lines = psOutput.split('\n')
                        
                        for (def line : lines) {
                            if (line.startsWith("PATH:")) {
                                pythonExe = line.substring(5).trim()
                            } else if (line.startsWith("VERSION:")) {
                                pythonVersion = line.substring(8).trim()
                            }
                        }
                        
                        if (pythonExe && pythonExe != "NOT_FOUND") {
                            echo ""
                            echo "✓ Python Found Successfully!"
                            echo "  Path: ${pythonExe}"
                            if (pythonVersion) {
                                echo "  Version: ${pythonVersion}"
                            }
                            echo ""
                            
                            // Store in environment variable for all subsequent stages
                            env.PYTHON_EXE = pythonExe
                            echo "Python path stored in env.PYTHON_EXE: ${env.PYTHON_EXE}"
                        } else {
                            error("Python not found! Please install Python system-wide (e.g., C:\\Program Files\\Python311\\) or ensure 'py' launcher is available.")
                        }
                    } catch (Exception e) {
                        error("Failed to find Python: ${e.getMessage()}")
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    echo "Using Python from previous stage: ${env.PYTHON_EXE}"
                    
                    // Create Python virtual environment using the stored Python path
                    // Handle both "py" launcher and full paths
                    def pythonCmd = (env.PYTHON_EXE == "py" || env.PYTHON_EXE.endsWith("\\py.exe")) 
                        ? "py" 
                        : "\"${env.PYTHON_EXE}\""
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
