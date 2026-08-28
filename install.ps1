<#
.SYNOPSIS
    Install oneshot into your user-level Claude directory on Windows.

.DESCRIPTION
    A thin wrapper around install.py so Windows users can run one command.
    Requires Python 3.8+ on PATH (python, python3, or the py launcher).

.EXAMPLE
    .\install.ps1
    .\install.ps1 -Project
    .\install.ps1 -Check
    .\install.ps1 -Uninstall
#>
[CmdletBinding()]
param(
    [switch]$Project,
    [switch]$Check,
    [switch]$Uninstall,
    [switch]$Force,
    [string]$Dest
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$installer = Join-Path $repo 'install.py'

if (-not (Test-Path $installer)) {
    Write-Error @"
install.py not found next to this script.

You are probably running this from the wrong directory, or the repository
contents are nested one level deep. The project root must directly contain
skills\, agents\, commands\ and .claude-plugin\.
"@
    exit 1
}

# Find a Python interpreter.
$python = $null
foreach ($candidate in @('python3', 'python', 'py')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) {
        $version = & $candidate -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and [version]$version -ge [version]'3.8') {
            $python = $candidate
            break
        }
    }
}

if (-not $python) {
    Write-Error "Python 3.8 or newer is required and was not found on PATH. Install it from https://www.python.org/downloads/ and re-run."
    exit 1
}

$pyArgs = @($installer)
if ($Project)   { $pyArgs += '--project' }
if ($Check)     { $pyArgs += '--check' }
if ($Uninstall) { $pyArgs += '--uninstall' }
if ($Force)     { $pyArgs += '--force' }
if ($Dest)      { $pyArgs += @('--dest', $Dest) }

Write-Host "Using $python" -ForegroundColor DarkGray
& $python @pyArgs
exit $LASTEXITCODE
