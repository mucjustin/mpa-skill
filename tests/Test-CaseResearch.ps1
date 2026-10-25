[CmdletBinding()]
param([string] $ScenarioPath)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$refs = Join-Path $repoRoot 'skills\mpa-skill\references'

function Read-Required([string] $path) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing case research file: $path" }
    return (Get-Content -LiteralPath $path -Raw -Encoding UTF8)
}
function Require-Pattern([string] $text, [string] $pattern, [string] $name) {
    if ($text -notmatch $pattern) { throw "Case research contract missing: $name" }
}

$controller = Read-Required (Join-Path $repoRoot 'skills\mpa-skill\SKILL.md')
$routing = Read-Required (Join-Path $refs 'routing.md')
$case = Read-Required (Join-Path $refs 'case-research.md')
$evidence = Read-Required (Join-Path $refs 'evidence-protocol.md')
$template = Read-Required (Join-Path $refs 'templates.md')
$methods = Read-Required (Join-Path $refs 'mpa-knowledge.md')
$competition = Read-Required (Join-Path $refs 'mpa-case-competition.md')
$evaluation = Read-Required (Join-Path $repoRoot 'docs\validation\case-research-evaluation.md')

Require-Pattern $controller 'references/case-research\.md' 'controller case link'
Require-Pattern $controller 'references/evidence-protocol\.md' 'controller evidence link'
Require-Pattern $routing 'case-research\.md' 'routing case link'
Require-Pattern $routing 'evidence-protocol\.md' 'routing evidence link'
Require-Pattern $case 'Stakeholder bargaining' 'multiple lenses'
Require-Pattern $case 'Policy implementation' 'implementation lens'
Require-Pattern $case 'Resource activation' 'resource lens'
Require-Pattern $case 'Development and safeguards' 'safeguards lens'
Require-Pattern $case '(?i)rival' 'competing explanation'
Require-Pattern $case '(?i)do not (invent|fabricate)' 'no synthetic evidence'
Require-Pattern $case '(?i)short classroom answer' 'compact classroom path'
Require-Pattern $evidence 'verified' 'verified evidence state'
Require-Pattern $evidence 'disputed' 'disputed evidence state'
Require-Pattern $evidence 'inaccessible' 'access boundary'
Require-Pattern $evidence '(?i)do not commit' 'privacy redline'
Require-Pattern $template 'case-research\.md' 'optional case research template'
Require-Pattern $competition 'case-research\.md' 'case competition reuse'
Require-Pattern $methods '(?i)parallel trends' 'DID identification caveat'
Require-Pattern $methods '(?i)unobserved confounding' 'matching limitation'
Require-Pattern $evaluation '(?i)not benchmark results' 'evaluation honestly labeled'

if ([string]::IsNullOrWhiteSpace($ScenarioPath)) {
    $ScenarioPath = Join-Path $PSScriptRoot 'fixtures\case-research-scenarios.json'
}
$scenarios = @(Read-Required $ScenarioPath | ConvertFrom-Json)
if ($scenarios.Count -lt 6) { throw 'At least six case scenarios required' }
$ids = @($scenarios | ForEach-Object { $_.id })
if (@($ids | Sort-Object -Unique).Count -ne $ids.Count) { throw 'Duplicate case scenario id' }
foreach ($s in $scenarios) {
    foreach ($field in @('id','kind','request','fixture','expected_decisions','forbidden_decisions')) {
        if (-not $s.PSObject.Properties.Name.Contains($field)) { throw "Missing $field in case fixture: $($s.id)" }
    }
    if (@($s.expected_decisions).Count -lt 2 -or @($s.forbidden_decisions).Count -lt 1) {
        throw "Incomplete decisions: $($s.id)"
    }
}
Write-Output 'CASE RESEARCH CONTRACT PASS (structural checks, not semantic model evaluation)'
