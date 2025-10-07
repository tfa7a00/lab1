$path = "D:\Downloads\lab1"
$repo = $path
$lastCommit = ""

while ($true) {
    cd $repo
    git fetch origin
    $currentCommit = git rev-parse origin/main
    if ($currentCommit -ne $lastCommit) {
        Write-Host "New commit detected. Pulling and rebuilding..."
        git pull origin main
        docker build -t arithmetic-api $repo
        docker stop arithmetic-api -ErrorAction SilentlyContinue
        docker rm arithmetic-api -ErrorAction SilentlyContinue
        docker run -d -p 5000:5000 --name arithmetic-api arithmetic-api
        $lastCommit = $currentCommit
    }
    Start-Sleep -Seconds 10
}
