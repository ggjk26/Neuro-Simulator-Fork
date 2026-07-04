param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $LauncherArgs
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$ServerPath = Join-Path $RepoRoot 'server'
if (Test-Path $ServerPath) {
    if ($env:PYTHONPATH) {
        $env:PYTHONPATH = "$ServerPath$([IO.Path]::PathSeparator)$env:PYTHONPATH"
    } else {
        $env:PYTHONPATH = $ServerPath
    }
}
python -m neuro_simulator.launcher @LauncherArgs
