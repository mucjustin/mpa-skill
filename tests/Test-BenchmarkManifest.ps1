[CmdletBinding()]
param([string] $ManifestPath)
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
    $repositoryRoot = Split-Path -Parent $PSScriptRoot
    $ManifestPath = Join-Path $repositoryRoot 'docs\validation\mpa-thesis-corpus.json'
}
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) { throw 'missing MPA thesis corpus manifest' }
$parsedItems = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$items = @()
foreach ($parsedItem in $parsedItems) { $items += $parsedItem }
if ($items.Count -lt 10) { throw 'at least 10 thesis records are required' }
if (@($items | Where-Object split -eq 'development').Count -lt 7) { throw 'at least 7 development records are required' }
if (@($items | Where-Object split -eq 'holdout').Count -lt 3) { throw 'at least 3 holdout records are required' }
$ids = @($items | ForEach-Object id)
if (@($ids | Sort-Object -Unique).Count -ne $ids.Count) { throw 'corpus ids must be unique' }
foreach ($item in $items) {
    foreach ($field in @('id','title','year','institution','jurisdiction','language','method','topic','landing_url','full_text_url','access','split','verified_on')) {
        if (-not $item.PSObject.Properties.Name.Contains($field) -or [string]::IsNullOrWhiteSpace([string]$item.$field)) { throw "corpus record $($item.id) missing $field" }
    }
    if ($item.access -notin @('open','author-posted','repository-open')) { throw "corpus record $($item.id) is not lawfully open" }
    foreach ($url in @($item.landing_url,$item.full_text_url)) {
        if ($url -notmatch '^https://') { throw "corpus record $($item.id) has a non-HTTPS URL" }
    }
}
Write-Output 'BENCHMARK MANIFEST PASS'
