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
                    // First, let's try a simpler approach using where.exe
                    echo "Searching for Python..."
                    
                    // Try 'py' launcher using where.exe (more reliable)
                    def wherePy = bat(script: "where.exe py 2>nul", returnStdout: true, returnStatus: true)
                    if (wherePy == 0) {
                        def pyPath = bat(script: "where.exe py", returnStdout: true).trim()
                        echo "Found 'py' launcher at: ${pyPath}"
                        // Test if it works
                        def testPy = bat(script: "py --version", returnStdout: true, returnStatus: true)
                        if (testPy == 0) {
                            pythonExe = "py"
                            echo "Python launcher 'py' is working!"
                        } else {
                            echo "Python launcher 'py' found but not working (exit code: ${testPy})"
                        }
                    }
                    
                    // If py launcher didn't work, try 'python' command
                    if (!pythonExe) {
                        def wherePython = bat(script: "where.exe python 2>nul", returnStdout: true, returnStatus: true)
                        if (wherePython == 0) {
                            def pythonPath = bat(script: "where.exe python", returnStdout: true).trim()
                            echo "Found 'python' command at: ${pythonPath}"
                            // Test if it works
                            def testPython = bat(script: "python --version", returnStdout: true, returnStatus: true)
                            if (testPython == 0) {
                                pythonExe = pythonPath
                                echo "Python command is working!"
                            } else {
                                echo "Python command found but not working (exit code: ${testPython})"
                            }
                        }
                    }
                    
                    // If still not found, try common system locations
                    if (!pythonExe) {
                        echo "Searching system-wide Python installations..."
                        def systemPaths = [
                            "C:\\Program Files\\Python311\\python.exe",
                            "C:\\Program Files\\Python312\\python.exe",
                            "C:\\Program Files\\Python313\\python.exe",
                            "C:\\Program Files (x86)\\Python311\\python.exe",
                            "C:\\Python311\\python.exe",
                            "C:\\Python312\\python.exe"
                        ]
                        
                        for (def path : systemPaths) {
                            def testPath = bat(script: "if exist \"${path}\" (\"${path}\" --version) else (exit /b 1)", returnStdout: true, returnStatus: true)
                            if (testPath == 0) {
                                pythonExe = path
                                echo "Found Python at: ${pythonExe}"
                                break
                            }
                        }
                    }
                    
                    // Final check - if still not found, try PowerShell search as fallback
                    if (!pythonExe) {
                        echo "Trying PowerShell-based search as fallback..."
                        def psScript = '''
                            $found = $null
                            $ErrorActionPreference = "SilentlyContinue"
                            
                            # Try 'py' launcher
                            try {
                                $result = & py --version 2>&1
                                if ($?) {
                                    $found = "py"
                                }
                            } catch {}
                            
                            # Try 'python' command
                            if (-not $found) {
                                try {
                                    $cmd = Get-Command python -ErrorAction SilentlyContinue
                                    if ($cmd) {
                                        $result = & python --version 2>&1
                                        if ($?) {
                                            $found = $cmd.Path
                                        }
                                    }
                                } catch {}
                            }
                            
                            # Try system paths
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
                                                $found = $path
                                                break
                                            }
                                        } catch {}
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
                                echo "Found Python via PowerShell: ${pythonExe}"
                            }
                        } catch (Exception e) {
                            echo "PowerShell search also failed: ${e.getMessage()}"
                        }
                    }
                    
                    // Final validation
                    if (!pythonExe) {
                        error("Python not found! Please install Python system-wide (e.g., C:\\Program Files\\Python311\\) or ensure 'py' launcher is available. The Jenkins service account needs access to Python.")
                    }
                    
                    // Verify the Python executable works
                    echo "Verifying Python executable..."
                    def verifyCmd = (pythonExe == "py") ? "py --version" : "\"${pythonExe}\" --version"
                    def verifyResult = bat(script: verifyCmd, returnStdout: true, returnStatus: true)
                    if (verifyResult != 0) {
                        error("Python found at '${pythonExe}' but verification failed. Please check permissions.")
                    }
                    
                    // Store in environment variable for later stages
                    env.PYTHON_EXE = pythonExe
                    echo "Successfully found and verified Python: ${env.PYTHON_EXE}"
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
