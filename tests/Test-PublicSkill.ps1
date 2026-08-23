[CmdletBinding()]
param(
    [string] $RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string] $InstalledSkillRoot
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()
$skillRoot = Join-Path $RepoRoot 'skills\mpa-research-workflow'

function Require-File {
    param([string] $Path, [string] $Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        $script:failures.Add("missing $Label")
    }
}

function Read-File {
    param([string] $Path)
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    }
    return ''
}

function Require-Text {
    param([string] $Text, [string] $Pattern, [string] $Label)
    if ($Text -notmatch $Pattern) {
        $script:failures.Add($Label)
    }
}

function Reject-Text {
    param([string] $Text, [string] $Pattern, [string] $Label)
    if ($Text -match $Pattern) {
        $script:failures.Add($Label)
    }
}

$requiredRepoFiles = @(
    'README.md',
    'README.en.md',
    'LICENSE',
    'SECURITY.md',
    '.gitignore',
    'tests\Test-PublicSkill.ps1',
    'tests\Test-WorkspaceScripts.ps1',
    'tests\fixtures\portable-config.json'
)
foreach ($relative in $requiredRepoFiles) {
    Require-File (Join-Path $RepoRoot $relative) $relative
}

$requiredSkillFiles = @(
    'SKILL.md',
    'agents\openai.yaml',
    'references\dependencies.md',
    'references\mpa-deliverables.md',
    'references\mpa-research-contract.md',
    'references\routing.md',
    'references\workspace-configuration.md',
    'scripts\Initialize-MpaWorkspace.ps1',
    'scripts\Test-MpaEnvironment.ps1'
)
foreach ($relative in $requiredSkillFiles) {
    Require-File (Join-Path $skillRoot $relative) "skill/$relative"
}

$skillFiles = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'skills') -Filter SKILL.md -File -Recurse -ErrorAction SilentlyContinue)
if ($skillFiles.Count -ne 1) {
    $failures.Add("discoverable skill count: $($skillFiles.Count)")
}

$skill = Read-File (Join-Path $skillRoot 'SKILL.md')
$metadata = Read-File (Join-Path $skillRoot 'agents\openai.yaml')
$deliverables = Read-File (Join-Path $skillRoot 'references\mpa-deliverables.md')
$researchContract = Read-File (Join-Path $skillRoot 'references\mpa-research-contract.md')
$routing = Read-File (Join-Path $skillRoot 'references\routing.md')
$dependencies = Read-File (Join-Path $skillRoot 'references\dependencies.md')
$workspace = Read-File (Join-Path $skillRoot 'references\workspace-configuration.md')
$readmeZh = Read-File (Join-Path $RepoRoot 'README.md')
$readmeEn = Read-File (Join-Path $RepoRoot 'README.en.md')
$license = Read-File (Join-Path $RepoRoot 'LICENSE')
$security = Read-File (Join-Path $RepoRoot 'SECURITY.md')

Require-Text $skill '(?s)^---\s*\r?\nname:\s*mpa-research-workflow\s*\r?\ndescription:' 'skill frontmatter'
Require-Text $skill '(?i)MPA graduate' 'MPA graduate trigger'
Require-Text $skill '(?i)generic.*(?:academic|teaching|blogging|data|Zotero|Obsidian).*not' 'generic request exclusion'
Require-Text $skill '(?i)public problem.*stakeholders.*public value.*institutional.*theory.*evidence.*method.*analysis.*recommendation' 'MPA Research Spine'
Require-Text $skill '(?i)course-to-capstone' 'course-to-capstone provenance'
Require-Text $skill '\u662F\u5426\u6267\u884C\uFF1F' 'single confirmation prompt'
Require-Text $skill '(?i)without repeated.*permission' 'no repeated confirmation'
Require-Text $skill '(?i)never.*zotero\.sqlite' 'direct Zotero database prohibition'
Require-Text $skill '(?i)login.*CAPTCHA.*paywall' 'access safety stop'
Require-Text $skill 'references/mpa-deliverables\.md' 'deliverable reference routing'
Require-Text $skill 'references/workspace-configuration\.md' 'workspace reference routing'

foreach ($term in @('course notes', 'case analysis', 'policy memo', 'literature map', 'proposal', 'fieldwork', 'data analysis', 'thesis', 'defence')) {
    Require-Text $deliverables ([regex]::Escape($term)) "MPA deliverable: $term"
}
Require-Text $deliverables '(?i)evidence.*inference.*recommendation' 'evidence/inference/recommendation boundary'
Require-Text $researchContract '(?i)current.*programme.*university.*supervisor.*ethics.*override' 'current programme precedence'
Require-Text $researchContract '(?i)causal|causality' 'causal boundary'
Require-Text $routing '(?i)minimum sufficient' 'minimum sufficient route'
Require-Text $routing '(?i)course.*case.*policy memo.*literature.*research design.*fieldwork.*data.*thesis.*defence' 'MPA route coverage'
Require-Text $dependencies '(?i)optional' 'optional dependency boundary'
Require-Text $dependencies '(?i)unavailable.*closest|missing.*report' 'dependency degradation'
Require-Text $workspace 'MPA_WORKSPACE_CONFIG' 'environment configuration'
Require-Text $workspace '%APPDATA%\\mpa-research-workflow\\config\.json' 'user configuration path'
Require-Text $workspace '(?i)start.*Zotero.*automatically' 'automatic Zotero startup'
Require-Text $workspace '(?i)launch fails' 'manual Zotero fallback'

Require-Text $metadata 'display_name:' 'UI display name'
Require-Text $metadata 'short_description:' 'UI short description'
Require-Text $metadata 'default_prompt:' 'UI default prompt'
Require-Text $metadata '(?i)allow_implicit_invocation:\s*true' 'implicit invocation policy'

foreach ($text in @($readmeZh, $readmeEn)) {
    Require-Text $text 'mucjustin/mpa-research-workflow-skill' 'public repository installation'
    Require-Text $text '(?i)npx skills add' 'npx installation command'
    Require-Text $text '(?i)Initialize-MpaWorkspace\.ps1' 'first-run setup command'
    Require-Text $text '(?i)update' 'update instructions'
    Require-Text $text '(?i)uninstall' 'uninstall instructions'
    Require-Text $text '(?i)Windows-first' 'Windows-first support'
}
Require-Text $readmeZh 'MPA Research Spine' 'Chinese MPA Research Spine explanation'
Require-Text $readmeEn 'MPA Research Spine' 'English MPA Research Spine explanation'
Require-Text $license 'MIT License' 'MIT license title'
Require-Text $license 'Copyright \(c\) 2026 mucjustin' 'MIT copyright'
Require-Text $security '(?i)private vulnerability reporting' 'private vulnerability reporting'
Require-Text $security '(?i)credentials' 'credential reporting boundary'

$trackedText = @($skill, $metadata, $deliverables, $researchContract, $routing, $dependencies, $workspace, $readmeZh, $readmeEn, $security) -join "`n"
Reject-Text $trackedText '(?i)(?<![A-Z0-9])[A-Z]:\\' 'fixed drive-letter path'
Reject-Text $trackedText '(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}' 'embedded email address'
Reject-Text $trackedText '(?i)gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' 'credential-like token'

if ($InstalledSkillRoot) {
    foreach ($relative in $requiredSkillFiles) {
        $sourceFile = Join-Path $skillRoot $relative
        $installedFile = Join-Path $InstalledSkillRoot $relative
        if ((Test-Path -LiteralPath $sourceFile -PathType Leaf) -and (Test-Path -LiteralPath $installedFile -PathType Leaf)) {
            $sourceHash = (Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash
            $installedHash = (Get-FileHash -LiteralPath $installedFile -Algorithm SHA256).Hash
            if ($sourceHash -ne $installedHash) {
                $failures.Add("installed parity: $relative")
            }
        }
    }
}

if ($failures.Count -gt 0) {
    Write-Error ('PUBLIC SKILL CONTRACT FAIL: ' + ($failures -join '; '))
    exit 1
}

Write-Output 'PUBLIC SKILL CONTRACT PASS'
exit 0
