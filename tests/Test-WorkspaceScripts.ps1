[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$skillRoot = Join-Path $repoRoot 'skills\mpa-skill'
$initializeScript = Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1'
$inspectScript = Join-Path $skillRoot 'scripts\Test-MpaEnvironment.ps1'

if (-not (Test-Path -LiteralPath $initializeScript -PathType Leaf)) {
    throw "RED: missing $initializeScript"
}
if (-not (Test-Path -LiteralPath $inspectScript -PathType Leaf)) {
    throw "RED: missing $inspectScript"
}

function Assert-True {
    param([bool] $Condition, [string] $Message)
    if (-not $Condition) { throw $Message }
}

$tempBase = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\')
$testRoot = Join-Path $tempBase ('mpa-workspace-test-' + [guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($testRoot) | Out-Null

try {
    $isolatedAppData = Join-Path $testRoot 'AppData'
    $workspaceRoot = Join-Path $testRoot 'Workspace'
    $configPath = Join-Path $isolatedAppData 'mpa-skill\config.json'
    $zoteroPath = Join-Path $testRoot 'Apps\Zotero\zotero.exe'

    $result = & $initializeScript -WorkspaceRoot $workspaceRoot -ConfigPath $configPath -ZoteroExecutable $zoteroPath

    Assert-True (Test-Path -LiteralPath $configPath -PathType Leaf) 'config was not created'
    foreach ($path in @(
        $workspaceRoot,
        (Join-Path $workspaceRoot 'Obsidian'),
        (Join-Path $workspaceRoot 'ZoteroAttachments'),
        (Join-Path $workspaceRoot 'ResearchData'),
        (Join-Path $workspaceRoot 'ResearchProjects')
    )) {
        Assert-True (Test-Path -LiteralPath $path -PathType Container) "missing initialized directory: $path"
        Assert-True ([IO.Path]::GetFullPath($path).StartsWith($testRoot, [StringComparison]::OrdinalIgnoreCase)) "path escaped test root: $path"
    }

    $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $expectedProperties = @('obsidian_vault', 'research_data', 'research_projects', 'workspace_root', 'zotero_attachments', 'zotero_executable') | Sort-Object
    $actualProperties = @($config.PSObject.Properties.Name | Sort-Object)
    Assert-True (($actualProperties -join "`n") -ceq ($expectedProperties -join "`n")) 'config property set differs'
    Assert-True ($config.zotero_executable -ceq $zoteroPath) 'explicit Zotero executable was not preserved'
    Assert-True ($result.ConfigPath -ceq [IO.Path]::GetFullPath($configPath)) 'initializer summary config path differs'

    $whatIfRoot = Join-Path $testRoot 'WhatIfWorkspace'
    $whatIfConfig = Join-Path $isolatedAppData 'what-if.json'
    $null = & $initializeScript -WorkspaceRoot $whatIfRoot -ConfigPath $whatIfConfig -WhatIf
    Assert-True (-not (Test-Path -LiteralPath $whatIfRoot)) 'WhatIf created workspace'
    Assert-True (-not (Test-Path -LiteralPath $whatIfConfig)) 'WhatIf created config'

    $before = @(Get-ChildItem -LiteralPath $testRoot -File -Recurse | ForEach-Object { $_.FullName + '|' + $_.Length })
    $inspection = & $inspectScript -ConfigPath $configPath
    $after = @(Get-ChildItem -LiteralPath $testRoot -File -Recurse | ForEach-Object { $_.FullName + '|' + $_.Length })
    Assert-True (($before -join "`n") -ceq ($after -join "`n")) 'environment inspection changed files'
    Assert-True $inspection.ConfigFound 'environment inspection did not find config'
    Assert-True ($inspection.WorkspaceRootExists -and $inspection.ObsidianVaultExists) 'environment inspection missed initialized paths'

    $rootRejected = $false
    try {
        $null = & $initializeScript -WorkspaceRoot ([IO.Path]::GetPathRoot($testRoot)) -ConfigPath (Join-Path $isolatedAppData 'unsafe-root.json') -WhatIf
    } catch {
        $rootRejected = $true
    }
    Assert-True $rootRejected 'filesystem root was not rejected'

    $fileTarget = Join-Path $testRoot 'existing-file'
    [IO.File]::WriteAllText($fileTarget, 'not a directory')
    $fileRejected = $false
    try {
        $null = & $initializeScript -WorkspaceRoot $fileTarget -ConfigPath (Join-Path $isolatedAppData 'unsafe-file.json') -WhatIf
    } catch {
        $fileRejected = $true
    }
    Assert-True $fileRejected 'existing file target was not rejected'

    Write-Output 'WORKSPACE SCRIPT TESTS PASS'
} finally {
    $resolvedTestRoot = [IO.Path]::GetFullPath($testRoot)
    if (-not $resolvedTestRoot.StartsWith($tempBase + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Refusing cleanup outside temporary directory'
    }
    if (Test-Path -LiteralPath $resolvedTestRoot) {
        [IO.Directory]::Delete($resolvedTestRoot, $true)
    }
}
