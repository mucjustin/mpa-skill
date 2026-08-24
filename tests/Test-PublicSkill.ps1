[CmdletBinding()]
param(
    [string] $RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string] $InstalledSkillRoot
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()
$skillRoot = Join-Path $RepoRoot 'skills\mpa-skill'

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
    'references\local-office-editing.md',
    'references\real-data-workflow.md',
    'references\mpa-case-competition.md',
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
$caseCompetition = Read-File (Join-Path $skillRoot 'references\mpa-case-competition.md')
$researchContract = Read-File (Join-Path $skillRoot 'references\mpa-research-contract.md')
$routing = Read-File (Join-Path $skillRoot 'references\routing.md')
$dependencies = Read-File (Join-Path $skillRoot 'references\dependencies.md')
$workspace = Read-File (Join-Path $skillRoot 'references\workspace-configuration.md')
$localOffice = Read-File (Join-Path $skillRoot 'references\local-office-editing.md')
$realData = Read-File (Join-Path $skillRoot 'references\real-data-workflow.md')
$readmeZh = Read-File (Join-Path $RepoRoot 'README.md')
$readmeEn = Read-File (Join-Path $RepoRoot 'README.en.md')
$license = Read-File (Join-Path $RepoRoot 'LICENSE')
$security = Read-File (Join-Path $RepoRoot 'SECURITY.md')

Require-Text $skill '(?s)^---\s*\r?\nname:\s*mpa-skill\s*\r?\ndescription:' 'skill frontmatter'
Require-Text $skill '(?i)MPA graduate' 'MPA graduate trigger'
Require-Text $skill '(?i)generic.*(?:academic|teaching|blogging|data|Zotero|Obsidian).*not' 'generic request exclusion'
Require-Text $skill '(?i)public problem.*stakeholders.*public value.*institutional.*theory.*evidence.*method.*analysis.*recommendation' 'MPA Research Spine'
Require-Text $skill '(?i)course-to-capstone' 'course-to-capstone provenance'
Require-Text $skill '\u662F\u5426\u6267\u884C\uFF1F' 'single confirmation prompt'
Require-Text $skill '(?i)without repeated.*permission' 'no repeated confirmation'
Require-Text $skill '(?i)never.*zotero\.sqlite' 'direct Zotero database prohibition'
Require-Text $skill '(?i)login.*CAPTCHA.*paywall' 'access safety stop'
Require-Text $skill 'references/mpa-deliverables\.md' 'deliverable reference routing'
Require-Text $skill 'references/mpa-case-competition\.md' 'case competition reference routing'
Require-Text $skill 'references/workspace-configuration\.md' 'workspace reference routing'

foreach ($term in @('course notes', 'case analysis', 'policy memo', 'literature map', 'proposal', 'fieldwork', 'data analysis', 'thesis', 'defence')) {
    Require-Text $deliverables ([regex]::Escape($term)) "MPA deliverable: $term"
}
Require-Text $deliverables '(?i)evidence.*inference.*recommendation' 'evidence/inference/recommendation boundary'
Require-Text $researchContract '(?i)current.*programme.*university.*supervisor.*ethics.*override' 'current programme precedence'
Require-Text $researchContract '(?i)causal|causality' 'causal boundary'
Require-Text $researchContract '(?i)Treat course notes and earlier assignments as leads' 'course notes as leads'
Require-Text $researchContract '(?i)Disclose AI assistance' 'AIGC disclosure rule'
Require-Text $researchContract '(?i)never present AI-generated text, data, or citations as the student''s own' 'AIGC originality boundary'
Require-Text $routing '(?i)minimum sufficient' 'minimum sufficient route'
Require-Text $routing '(?i)course.*case.*policy memo.*literature.*research design.*fieldwork.*data.*thesis.*defence' 'MPA route coverage'
Require-Text $routing '(?i)case competition entry' 'case competition route row'
Require-Text $routing 'mpa-case-competition\.md' 'case competition reference load'
foreach ($term in @('\u6848\u4F8B\u6B63\u6587', '\u6848\u4F8B\u5206\u6790\u62A5\u544A', '\u8C03\u7814\u62A5\u544A', 'fieldwork evidence', 'theory applicability')) {
    Require-Text $routing $term "routing case competition rule: $term"
}
Require-Text $caseCompetition '(?s)\u6848\u4F8B\u6B63\u6587.*\u6848\u4F8B\u5206\u6790\u62A5\u544A.*\u8C03\u7814\u62A5\u544A' 'case competition three-document structure'
Require-Text $caseCompetition '15000' 'case competition word limit'
Require-Text $caseCompetition '4000' 'case competition survey word limit'
Require-Text $caseCompetition '\u8D77\u627F\u8F6C\u5408' 'case competition narrative arc'
Require-Text $caseCompetition '(?i)overrides this file' 'case competition notice precedence'
Require-Text $caseCompetition '(?i)multi-stakeholder interview outlines' 'case competition fieldwork evidence'
Require-Text $caseCompetition '(?i)applicability' 'case competition theory applicability'
Require-Text $caseCompetition '(?i)must not be AI-generated' 'case competition AIGC boundary'
Require-Text $caseCompetition '(?i)never substitutes' 'case competition drafting boundary'
Require-Text $researchContract 'mpa-case-competition\.md' 'research contract case competition pointer'
Require-Text $dependencies '(?i)optional' 'optional dependency boundary'
Require-Text $dependencies '(?i)unavailable.*closest|missing.*report' 'dependency degradation'
Require-Text $workspace 'MPA_WORKSPACE_CONFIG' 'environment configuration'
Require-Text $workspace '%APPDATA%\\mpa-skill\\config\.json' 'user configuration path'
Require-Text $workspace '(?i)start.*Zotero.*automatically' 'automatic Zotero startup'
Require-Text $workspace '(?i)launch fails' 'manual Zotero fallback'

Require-Text $localOffice '(?i)descending' 'office-editing descending-order rule'
Require-Text $localOffice '--json' 'office-editing json-argument rule'
Require-Text $localOffice 'file://' 'office-editing file-prefix rule'
Require-Text $localOffice '(?i)doc_insert_table_by_csv' 'office-editing table-creation rule'
Require-Text $localOffice '(?i)is_dirty' 'office-editing crash-recovery rule'
Require-Text $realData '(?i)AUTHOR_INPUT_NEEDED' 'real-data no-fabrication rule'
Require-Text $realData '(?i)relative position' 'real-data standardization-frame rule'
Require-Text $realData '(?i)majority-class baseline' 'real-data baseline-reporting rule'
Require-Text $dependencies '(?i)Verified integration pitfalls' 'dependencies verified-pitfalls table'
Require-Text $dependencies '(?i)connector API' 'dependencies Zotero write-route rule'
Require-Text $skill '(?i)new values present' 'skill two-way numeric verification'
Require-Text $routing '(?is)non-MPA to MPA conversion.*audit source-data consistency' 'conversion data-audit-first rule'
Require-Text $routing 'real-data-workflow\.md' 'routing loads real-data reference'
Require-Text $routing 'local-office-editing\.md' 'routing loads office-editing reference'

Require-Text $skill '(?i)A request to convert non-MPA material into MPA work is MPA work' 'non-MPA conversion scope rule'
Require-Text $skill '(?i)include one workspace-integration question in the same confirmation' 'workspace offer in single confirmation'
Require-Text $routing '(?is)non-MPA to MPA conversion.*Research Spine before rewriting' 'non-MPA conversion route sequence'
Require-Text $routing '(?i)Offer Zotero or Obsidian integration once in the route confirmation' 'workspace integration offer'
Require-Text $routing '(?i)write nothing to either before the user confirms' 'no unconfirmed integration writes'
Require-Text $metadata 'display_name:' 'UI display name'
Require-Text $metadata 'short_description:' 'UI short description'
Require-Text $metadata 'default_prompt:' 'UI default prompt'
Require-Text $metadata '(?i)allow_implicit_invocation:\s*true' 'implicit invocation policy'

foreach ($text in @($readmeZh, $readmeEn)) {
    Require-Text $text 'mucjustin/mpa-skill' 'public repository installation'
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

$trackedText = @($skill, $metadata, $deliverables, $caseCompetition, $researchContract, $routing, $dependencies, $workspace, $localOffice, $realData, $readmeZh, $readmeEn, $security) -join "`n"
Reject-Text $trackedText '(?i)(?<![A-Z0-9])[A-Z]:\\' 'fixed drive-letter path'
Reject-Text $trackedText '(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}' 'embedded email address'
Reject-Text $trackedText '(?i)gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' 'credential-like token'

if ($InstalledSkillRoot) {
    foreach ($relative in $requiredSkillFiles) {
        $sourceFile = Join-Path $skillRoot $relative
        $installedFile = Join-Path $InstalledSkillRoot $relative
        if ((Test-Path -LiteralPath $sourceFile -PathType Leaf) -and (Test-Path -LiteralPath $installedFile -PathType Leaf)) {
            $sourceText = [IO.File]::ReadAllText($sourceFile).Replace("`r`n", "`n").Replace("`r", "`n")
            $installedText = [IO.File]::ReadAllText($installedFile).Replace("`r`n", "`n").Replace("`r", "`n")
            if ($sourceText -cne $installedText) {
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
