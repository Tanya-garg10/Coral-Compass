# StudySync AI — Coral CLI installer for Windows (x86_64)
# Source: https://withcoral.com/docs/getting-started/installation
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$zipUrl  = 'https://github.com/withcoral/coral/releases/latest/download/coral-x86_64-pc-windows-msvc.zip'
$zipPath = Join-Path $PSScriptRoot 'coral.zip'
$extract = Join-Path $PSScriptRoot 'coral_dist'
$binDir  = Join-Path $env:USERPROFILE '.local\bin'

Write-Host "==> Downloading Coral CLI..."
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing

Write-Host "==> Extracting..."
if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
Expand-Archive -Path $zipPath -DestinationPath $extract -Force

$exe = Get-ChildItem -Path $extract -Recurse -Filter coral.exe | Select-Object -First 1
if (-not $exe) { throw 'coral.exe not found in archive' }

New-Item -ItemType Directory -Force -Path $binDir | Out-Null
Copy-Item $exe.FullName (Join-Path $binDir 'coral.exe') -Force
Write-Host "==> Installed coral.exe to $binDir"

# Persist PATH for the user
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (-not (($userPath -split ';') -contains $binDir)) {
    [Environment]::SetEnvironmentVariable('Path', "$binDir;$userPath", 'User')
    Write-Host "==> Added $binDir to user PATH (restart terminal for new sessions)"
}
$env:Path = "$binDir;$env:Path"

Write-Host "==> Verifying install..."
& (Join-Path $binDir 'coral.exe') --version

Write-Host "`nDone. Next: run .\coral_setup.ps1 to register CSV file sources and run a sample query."
