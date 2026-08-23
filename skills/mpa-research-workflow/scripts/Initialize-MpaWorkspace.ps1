[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $WorkspaceRoot,
    [string] $ConfigPath,
    [string] $ZoteroExecutable,
    [switch] $WhatIf
)

$ErrorActionPreference = 'Stop'

function Resolve-FullPath {
    param([Parameter(Mandatory)] [string] $Path)
    $expanded = [Environment]::ExpandEnvironmentVariables($Path)
    return [IO.Path]::GetFullPath($expanded)
}

$resolvedRoot = Resolve-FullPath $WorkspaceRoot
$filesystemRoot = [IO.Path]::GetPathRoot($resolvedRoot)
if ($resolvedRoot.TrimEnd('\', '/') -ceq $filesystemRoot.TrimEnd('\', '/')) {
    throw 'WorkspaceRoot must not be a filesystem root.'
}
if (Test-Path -LiteralPath $resolvedRoot -PathType Leaf) {
    throw 'WorkspaceRoot points to an existing file.'
}

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    if ([string]::IsNullOrWhiteSpace($env:APPDATA)) {
        throw 'ConfigPath is required when APPDATA is unavailable.'
    }
    $ConfigPath = Join-Path $env:APPDATA 'mpa-research-workflow\config.json'
}
$resolvedConfig = Resolve-FullPath $ConfigPath

if ([string]::IsNullOrWhiteSpace($ZoteroExecutable)) {
    $candidates = [System.Collections.Generic.List[string]]::new()
    if ($env:ProgramFiles) {
        $candidates.Add((Join-Path $env:ProgramFiles 'Zotero\zotero.exe'))
    }
    if (${env:ProgramFiles(x86)}) {
        $candidates.Add((Join-Path ${env:ProgramFiles(x86)} 'Zotero\zotero.exe'))
    }
    if ($env:LOCALAPPDATA) {
        $candidates.Add((Join-Path $env:LOCALAPPDATA 'Programs\Zotero\zotero.exe'))
    }
    $detected = $candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
    $resolvedZotero = if ($detected) { Resolve-FullPath $detected } else { '' }
} else {
    $resolvedZotero = Resolve-FullPath $ZoteroExecutable
}

$paths = [ordered]@{
    workspace_root = $resolvedRoot
    obsidian_vault = Join-Path $resolvedRoot 'Obsidian'
    zotero_executable = $resolvedZotero
    zotero_attachments = Join-Path $resolvedRoot 'ZoteroAttachments'
    research_data = Join-Path $resolvedRoot 'ResearchData'
    research_projects = Join-Path $resolvedRoot 'ResearchProjects'
}

if (-not $WhatIf) {
    foreach ($directory in @(
        $paths.workspace_root,
        $paths.obsidian_vault,
        $paths.zotero_attachments,
        $paths.research_data,
        $paths.research_projects
    )) {
        [IO.Directory]::CreateDirectory($directory) | Out-Null
    }

    $configDirectory = Split-Path -Parent $resolvedConfig
    if ([string]::IsNullOrWhiteSpace($configDirectory)) {
        throw 'ConfigPath must include a parent directory.'
    }
    [IO.Directory]::CreateDirectory($configDirectory) | Out-Null
    $json = [pscustomobject]$paths | ConvertTo-Json
    $utf8 = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($resolvedConfig, $json + [Environment]::NewLine, $utf8)
}

[pscustomobject]@{
    ConfigPath = $resolvedConfig
    WorkspaceRoot = $resolvedRoot
    ZoteroExecutable = $resolvedZotero
    Created = -not $WhatIf
    Directories = @(
        $paths.workspace_root,
        $paths.obsidian_vault,
        $paths.zotero_attachments,
        $paths.research_data,
        $paths.research_projects
    )
}
