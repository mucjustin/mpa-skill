[CmdletBinding()]
param(
    [string] $ConfigPath
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    if (-not [string]::IsNullOrWhiteSpace($env:MPA_WORKSPACE_CONFIG)) {
        $ConfigPath = $env:MPA_WORKSPACE_CONFIG
    } elseif (-not [string]::IsNullOrWhiteSpace($env:APPDATA)) {
        $ConfigPath = Join-Path $env:APPDATA 'mpa-research-workflow\config.json'
    }
}

$resolvedConfig = if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    ''
} else {
    [IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($ConfigPath))
}
$configFound = (-not [string]::IsNullOrWhiteSpace($resolvedConfig)) -and (Test-Path -LiteralPath $resolvedConfig -PathType Leaf)
$config = if ($configFound) {
    Get-Content -LiteralPath $resolvedConfig -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
    $null
}

function Test-ConfiguredDirectory {
    param([object] $Config, [string] $Property)
    if ($null -eq $Config -or $Config.PSObject.Properties.Name -notcontains $Property) { return $false }
    $value = [string]$Config.$Property
    return (-not [string]::IsNullOrWhiteSpace($value)) -and (Test-Path -LiteralPath $value -PathType Container)
}

$zoteroExecutable = if ($config -and $config.PSObject.Properties.Name -contains 'zotero_executable') {
    [string]$config.zotero_executable
} else {
    ''
}
$zoteroRunning = @(Get-Process -Name zotero -ErrorAction SilentlyContinue).Count -gt 0
$connectorReachable = $false
try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:23119/connector/ping' -TimeoutSec 1
    $connectorReachable = $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
} catch {
    $connectorReachable = $false
}

[pscustomobject]@{
    Platform = [Environment]::OSVersion.Platform.ToString()
    PowerShellVersion = $PSVersionTable.PSVersion.ToString()
    ConfigPath = $resolvedConfig
    ConfigFound = $configFound
    WorkspaceRootExists = Test-ConfiguredDirectory $config 'workspace_root'
    ObsidianVaultExists = Test-ConfiguredDirectory $config 'obsidian_vault'
    ZoteroAttachmentsExists = Test-ConfiguredDirectory $config 'zotero_attachments'
    ResearchDataExists = Test-ConfiguredDirectory $config 'research_data'
    ResearchProjectsExists = Test-ConfiguredDirectory $config 'research_projects'
    ZoteroExecutableConfigured = -not [string]::IsNullOrWhiteSpace($zoteroExecutable)
    ZoteroExecutableExists = (-not [string]::IsNullOrWhiteSpace($zoteroExecutable)) -and (Test-Path -LiteralPath $zoteroExecutable -PathType Leaf)
    ZoteroRunning = $zoteroRunning
    ZoteroConnectorReachable = $connectorReachable
}
