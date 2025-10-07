$path = "D:\Downloads\lab1"
$lastWrite = Get-ChildItem -Recurse $path | Measure-Object LastWriteTime -Maximum | Select-Object -ExpandProperty Maximum

while ($true) {
    Start-Sleep -Seconds 5
    $currentWrite = Get-ChildItem -Recurse $path | Measure-Object LastWriteTime -Maximum | Select-Object -ExpandProperty Maximum
    if ($currentWrite -gt $lastWrite) {
        Write-Host "Changes detected. Rebuilding Docker image..."
        docker build -t arithmetic-api $path
        docker stop arithmetic-api -ErrorAction SilentlyContinue
        docker rm arithmetic-api -ErrorAction SilentlyContinue
        docker run -d -p 5000:5000 --name arithmetic-api arithmetic-api
        $lastWrite = $currentWrite
    }
}
