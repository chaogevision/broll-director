$ErrorActionPreference = "Stop"
$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($env:CODEX_HOME) { $CodexHome = $env:CODEX_HOME } else { $CodexHome = Join-Path $HOME ".codex" }
$TargetDir = Join-Path (Join-Path $CodexHome "skills") "personal-talking-head-visual-director"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $TargetDir) | Out-Null
if (Test-Path $TargetDir) {
  $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $Backup = "$TargetDir.backup.$Stamp"
  Move-Item $TargetDir $Backup
  Write-Host "Existing skill moved to: $Backup"
}
Copy-Item -Recurse -Force $SourceDir $TargetDir
Write-Host "Installed to: $TargetDir"
Write-Host "Restart Codex before using the skill."
