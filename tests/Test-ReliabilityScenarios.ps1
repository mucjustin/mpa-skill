[CmdletBinding()]
param([string] $ScenarioPath)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($ScenarioPath)) {
    $ScenarioPath = Join-Path $PSScriptRoot 'fixtures\reliability-scenarios.json'
}

if (-not (Test-Path -LiteralPath $ScenarioPath -PathType Leaf)) { throw 'missing reliability scenario fixture' }

$items = @(Get-Content -LiteralPath $ScenarioPath -Raw -Encoding UTF8 | ConvertFrom-Json | ForEach-Object { $_ })
if ($items.Count -lt 8) { throw 'at least 8 reliability scenarios are required' }

$ids = @($items | ForEach-Object id)
if (@($ids | Sort-Object -Unique).Count -ne $ids.Count) { throw 'scenario ids must be unique' }

$requiredKinds = @('data-consistency','method-boundary','capability-preflight','document-recovery','bidirectional-acceptance')
foreach ($kind in $requiredKinds) {
    if (-not @($items | Where-Object kind -eq $kind)) { throw "missing scenario kind: $kind" }
}

foreach ($item in $items) {
    foreach ($field in @('id','kind','request','fixture','expected_decisions','forbidden_decisions')) {
        if (-not $item.PSObject.Properties.Name.Contains($field)) { throw "scenario $($item.id) missing $field" }
    }

    if (@($item.expected_decisions).Count -eq 0) { throw "scenario $($item.id) has no expected decisions" }
}

Write-Output 'RELIABILITY SCENARIOS PASS'
