[CmdletBinding()]
param(
    [string] $RepoRoot,
    [string] $InstalledSkillRoot
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}
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

function ConvertTo-PageSetPattern {
    param([object[]] $Pages, [string] $Separator)

    $orderedPages = @($Pages | ForEach-Object { [int] $_ } | Sort-Object -Unique)
    if ($orderedPages.Count -eq 0) { return '' }

    $segments = [System.Collections.Generic.List[string]]::new()
    $rangeStart = $orderedPages[0]
    $rangeEnd = $orderedPages[0]
    for ($index = 1; $index -lt $orderedPages.Count; $index++) {
        $page = $orderedPages[$index]
        if ($page -eq ($rangeEnd + 1)) {
            $rangeEnd = $page
            continue
        }
        $segments.Add($(if ($rangeStart -eq $rangeEnd) { "$rangeStart" } else { "$rangeStart\u2013$rangeEnd" }))
        $rangeStart = $page
        $rangeEnd = $page
    }
    $segments.Add($(if ($rangeStart -eq $rangeEnd) { "$rangeStart" } else { "$rangeStart\u2013$rangeEnd" }))
    return ($segments -join $Separator)
}

# ── Required repo files ──
$requiredRepoFiles = @(
    'README.md',
    'README.en.md',
    'CHANGELOG.md',
    'LICENSE',
    'SECURITY.md',
    '.gitignore',
    'tests\Test-PublicSkill.ps1',
    'tests\Test-ReliabilityScenarios.ps1',
    'tests\Test-BenchmarkManifest.ps1',
    'tests\Test-WorkspaceScripts.ps1',
    'tests\fixtures\portable-config.json',
    'tests\fixtures\reliability-scenarios.json',
    'docs\validation\mpa-thesis-corpus.json',
    'docs\validation\v1.0.0-benchmark.md',
    'docs\validation\v1.0.0-results.json',
    'docs\validation\a-b-regression.md'
)
foreach ($relative in $requiredRepoFiles) {
    Require-File (Join-Path $RepoRoot $relative) $relative
}

# ── Required skill files (consolidated structure) ──
$requiredSkillFiles = @(
    'SKILL.md',
    'agents\openai.yaml',
    'references\execution.md',
    'references\mpa-case-competition.md',
    'references\mpa-deliverables.md',
    'references\aigc-disclosure.md',
    'references\mpa-research-contract.md',
    'references\routing.md',
    'references\mpa-knowledge.md',
    'references\templates.md',
    'scripts\Initialize-MpaWorkspace.ps1',
    'scripts\Test-MpaEnvironment.ps1'
)
foreach ($relative in $requiredSkillFiles) {
    Require-File (Join-Path $skillRoot $relative) "skill/$relative"
}

# ── Discoverable skill count ──
$skillFiles = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'skills') -Filter SKILL.md -File -Recurse -ErrorAction SilentlyContinue)
if ($skillFiles.Count -ne 1) {
    $failures.Add("discoverable skill count: $($skillFiles.Count)")
}

# ── Read all files ──
$skill = Read-File (Join-Path $skillRoot 'SKILL.md')
$metadata = Read-File (Join-Path $skillRoot 'agents\openai.yaml')
$deliverables = Read-File (Join-Path $skillRoot 'references\mpa-deliverables.md')
$aigcDisclosure = Read-File (Join-Path $skillRoot 'references\aigc-disclosure.md')
$caseCompetition = Read-File (Join-Path $skillRoot 'references\mpa-case-competition.md')
$researchContract = Read-File (Join-Path $skillRoot 'references\mpa-research-contract.md')
$routing = Read-File (Join-Path $skillRoot 'references\routing.md')
$execution = Read-File (Join-Path $skillRoot 'references\execution.md')
$mpaKnowledge = Read-File (Join-Path $skillRoot 'references\mpa-knowledge.md')
$templates = Read-File (Join-Path $skillRoot 'references\templates.md')
$abRegression = Read-File (Join-Path $RepoRoot 'docs\validation\a-b-regression.md')
$readmeZh = Read-File (Join-Path $RepoRoot 'README.md')
$readmeEn = Read-File (Join-Path $RepoRoot 'README.en.md')
$changelog = Read-File (Join-Path $RepoRoot 'CHANGELOG.md')
$corpusText = Read-File (Join-Path $RepoRoot 'docs\validation\mpa-thesis-corpus.json')
$benchmarkResultsText = Read-File (Join-Path $RepoRoot 'docs\validation\v1.0.0-results.json')
$license = Read-File (Join-Path $RepoRoot 'LICENSE')
$security = Read-File (Join-Path $RepoRoot 'SECURITY.md')

# ── SKILL.md assertions ──
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
Require-Text $skill 'references/execution\.md' 'execution handbook reference'
Require-Text $skill 'references/mpa-knowledge\.md' 'mpa knowledge base pointer'
Require-Text $skill 'references/templates\.md' 'templates pointer'
Require-Text $skill 'references/routing\.md' 'routing reference'
Require-Text $skill 'mpa-knowledge\.md' 'skill knowledge-base pointer'
Require-Text $skill 'execution\.md' 'skill execution-handbook pointer'
Require-Text $skill '(?is)new.*present.*old.*absent|old.*absent.*new.*present' 'bidirectional replacement acceptance'
Require-Text $skill '(?i)A request to convert non-MPA material into MPA work is MPA work' 'non-MPA conversion scope rule'
Require-Text $skill '(?i)include one workspace-integration question in the same confirmation' 'workspace offer in single confirmation'

# ── Deliverables assertions ──
foreach ($term in @('course notes', 'case analysis', 'policy memo', 'literature map', 'proposal', 'fieldwork', 'data analysis', 'thesis', 'defence')) {
    Require-Text $deliverables ([regex]::Escape($term)) "MPA deliverable: $term"
}
Require-Text $deliverables '(?i)evidence.*inference.*recommendation' 'evidence/inference/recommendation boundary'

# ── AI-use disclosure assertions ──
Require-Text $aigcDisclosure '(?is)tool name.*version.*official URL.*purpose.*phases.*parameter settings.*verification process' 'aigc-disclosure field set'
Require-Text $aigcDisclosure '(?i)AUTHOR_INPUT_NEEDED' 'aigc-disclosure no-fabrication rule'
Require-Text $aigcDisclosure '(?i)verification that did not run' 'aigc-disclosure verification-trace rule'
Require-Text $aigcDisclosure '\u8C01\u4F7F\u7528\u3001\u8C01\u8D1F\u8D23' 'aigc-disclosure responsibility rule'
Require-Text $aigcDisclosure '(?i)Do not sign, submit, or upload' 'aigc-disclosure submission boundary'
Require-Text $skill 'aigc-disclosure\.md' 'skill aigc-disclosure pointer'
Require-Text $routing 'aigc-disclosure\.md' 'routing aigc-disclosure loading'
Require-Text $deliverables 'AI-use disclosure statement' 'deliverables aigc-disclosure row'

# ── Research contract assertions ──
Require-Text $researchContract '(?i)current.*programme.*university.*supervisor.*ethics.*override' 'current programme precedence'
Require-Text $researchContract '(?i)causal|causality' 'causal boundary'
Require-Text $researchContract '(?i)Treat course notes and earlier assignments as leads' 'course notes as leads'
Require-Text $researchContract '(?i)Disclose AI assistance' 'AIGC disclosure rule'
Require-Text $researchContract '(?i)never present AI-generated text, data, or citations as the student''s own' 'AIGC originality boundary'
Require-Text $researchContract 'mpa-case-competition\.md' 'research contract case competition pointer'

# ── Routing assertions ──
Require-Text $routing '(?i)minimum sufficient' 'minimum sufficient route'
Require-Text $routing '(?i)course.*case.*policy memo.*literature.*research design.*fieldwork.*data.*thesis.*defence' 'MPA route coverage'
Require-Text $routing 'mpa-case-competition\.md' 'case competition reference load'
Require-Text $routing 'mpa-knowledge\.md' 'routing knowledge-base loading'
Require-Text $routing 'execution\.md' 'routing execution-handbook loading'
Require-Text $routing 'templates\.md' 'routing templates loading'
Require-Text $routing '(?i)capabilit.*audit.*data.*content.*deliver|data.*audit.*content.*acceptance' 'data-before-writing route order'
foreach ($term in @('\u6848\u4F8B\u6B63\u6587', '\u6848\u4F8B\u5206\u6790\u62A5\u544A', '\u8C03\u7814\u62A5\u544A', 'fieldwork evidence', 'theory applicability')) {
    Require-Text $routing $term "routing case competition rule: $term"
}
Require-Text $routing '(?is)non-MPA to MPA conversion.*Research Spine before rewriting' 'non-MPA conversion route sequence'
Require-Text $routing '(?i)Offer Zotero or Obsidian integration once in the route confirmation' 'workspace integration offer'
Require-Text $routing '(?i)write nothing to either before the user confirms' 'no unconfirmed integration writes'

# ── Case competition assertions ──
Require-Text $caseCompetition '(?s)\u6848\u4F8B\u6B63\u6587.*\u6848\u4F8B\u5206\u6790\u62A5\u544A.*\u8C03\u7814\u62A5\u544A' 'case competition three-document structure'
Require-Text $caseCompetition '15000' 'case competition word limit'
Require-Text $caseCompetition '4000' 'case competition survey word limit'
Require-Text $caseCompetition '\u8D77\u627F\u8F6C\u5408' 'case competition narrative arc'
Require-Text $caseCompetition '(?i)overrides this file' 'case competition notice precedence'
Require-Text $caseCompetition '(?i)multi-stakeholder interview outlines' 'case competition fieldwork evidence'
Require-Text $caseCompetition '(?i)applicability' 'case competition theory applicability'
Require-Text $caseCompetition '(?i)must not be AI-generated' 'case competition AIGC boundary'
Require-Text $caseCompetition '(?i)never substitutes' 'case competition drafting boundary'

# ── Execution handbook assertions (merged: dependencies + workspace + office + data) ──
Require-Text $execution '(?i)optional' 'optional dependency boundary'
Require-Text $execution '(?i)unavailable.*closest|missing.*report' 'dependency degradation'
Require-Text $execution '(?i)Verified integration pitfalls' 'dependencies verified-pitfalls table'
Require-Text $execution '(?i)connector API' 'dependencies Zotero write-route rule'
Require-Text $execution 'MPA_WORKSPACE_CONFIG' 'environment configuration'
Require-Text $execution '%APPDATA%\\mpa-skill\\config\.json' 'user configuration path'
Require-Text $execution '(?i)start.*Zotero.*automatically' 'automatic Zotero startup'
Require-Text $execution '(?i)launch fails' 'manual Zotero fallback'
Require-Text $execution '(?i)not applied.*applied.*partially applied.*STATE_UNKNOWN' 'mutation-state classification'
Require-Text $execution '(?i)STATE_UNKNOWN.*(?:stop|pause)' 'unknown-state safety stop'
Require-Text $execution '(?i)descending' 'descending positional edits'
Require-Text $execution '(?i)unique' 'unique live anchor'
Require-Text $execution '--json' 'office-editing json-argument rule'
Require-Text $execution 'file://' 'office-editing file-prefix rule'
Require-Text $execution '(?i)doc_insert_table_by_csv' 'office-editing table-creation rule'
Require-Text $execution '(?i)is_dirty' 'office-editing crash-recovery rule'
Require-Text $execution '(?i)raw data' 'raw-data preservation'
Require-Text $execution '(?i)standardized|Z.standard' 'standardization interpretation boundary'
Require-Text $execution '(?i)majority.*baseline|baseline.*majority' 'classification baseline'
Require-Text $execution '(?i)new value.*old value|old value.*new value' 'numeric bidirectional verification'
Require-Text $execution '(?i)AUTHOR_INPUT_NEEDED' 'real-data no-fabrication rule'
Require-Text $execution '(?i)relative position' 'real-data standardization-frame rule'
Require-Text $execution '(?i)majority-class baseline' 'real-data baseline-reporting rule'

# ── MPA knowledge base assertions (merged: theory + china + thinking + course) ──
Require-Text $mpaKnowledge '\u4F55\u65F6\u67E5\u9605' 'knowledge-base usage note'
Require-Text $mpaKnowledge '\u4E13\u9898\u7814\u7A76|\u6848\u4F8B\u5206\u6790|\u8C03\u7814\u62A5\u544A|\u516C\u5171\u653F\u7B56\u5206\u6790' 'knowledge-base type taxonomy'
Require-Text $mpaKnowledge '\u538B\u529B\u578B\u4F53\u5236|\u8BD5\u70B9|\u6570\u5B57\u653F\u5E9C' 'knowledge-base china-contexts coverage'
Require-Text $mpaKnowledge '\u95EE\u9898\u5BFC\u5411|\u60C5\u5883\u654F\u611F|\u8BC1\u636E\u94FE|\u5BF9\u7B56\u53EF\u884C' 'knowledge-base thinking principles'
Require-Text $mpaKnowledge '\u516C\u5171\u653F\u7B56\u5206\u6790|\u793E\u4F1A\u7814\u7A76\u65B9\u6CD5|\u516C\u5171\u7BA1\u7406\u5B66' 'knowledge-base course-map coverage'
if ((@([regex]::Matches($mpaKnowledge, '(?m)^\|')).Count) -lt 40) { $failures.Add('knowledge-base table rows (min 40)') }

# ── Templates assertions ──
Require-Text $templates '(?i)case analysis' 'templates case-analysis section'
Require-Text $templates '(?i)policy memo' 'templates policy-memo section'
Require-Text $templates '(?i)literature' 'templates literature section'
Require-Text $templates '(?i)research design' 'templates research-design section'
Require-Text $templates '(?i)fieldwork' 'templates fieldwork section'
Require-Text $templates '(?i)data analysis' 'templates data-analysis section'
Require-Text $templates '\u9AA8\u67B6\u964D\u7EA7\u4E3A\u68C0\u67E5\u6E05\u5355' 'templates flexibility clause'
Require-Text $templates '\u7ED3\u6784\u4ECE\u7528\u6237' 'templates structure-from-user rule'
Require-Text $templates '\u4F9B\u7ED9\u4FA7\u5DE5\u5177' 'templates supply-side coverage'
Require-Text $templates '\u9700\u6C42\u4FA7\u8BC4\u4F30' 'templates demand-side coverage'
Require-Text $templates '\u4FE1\u606F\u4E0E\u95EE\u8D23\u673A\u5236' 'templates information-accountability coverage'
Require-Text $templates '\u8BC1\u636E\+\u63A8\u65AD|\u63A8\u65AD\+\u5EFA\u8BAE' 'templates layer tags'

# ── A/B regression method doc assertions ──
Require-Text $abRegression '(?i)A/B regression' 'ab-regression method doc'
Require-Text $abRegression '(?i)single sampled response' 'ab-regression single-run limit'
Require-Text $abRegression '(?i)not quality ranking' 'ab-regression no-ranking boundary'

# ── Metadata assertions ──
Require-Text $metadata 'display_name:' 'UI display name'
Require-Text $metadata 'short_description:' 'UI short description'
Require-Text $metadata 'default_prompt:' 'UI default prompt'
Require-Text $metadata '(?i)allow_implicit_invocation:\s*true' 'implicit invocation policy'

# ── README assertions ──
foreach ($text in @($readmeZh, $readmeEn)) {
    Require-Text $text 'mucjustin/mpa-skill' 'public repository installation'
    Require-Text $text '(?i)npx skills add' 'npx installation command'
    Require-Text $text '(?i)Initialize-MpaWorkspace\.ps1' 'first-run setup command'
    Require-Text $text '(?i)update' 'update instructions'
    Require-Text $text '(?i)uninstall' 'uninstall instructions'
    Require-Text $text '(?i)Windows-first' 'Windows-first support'
    Require-Text $text 'skills/mpa-skill/references/execution\.md' 'README execution handbook link'
    Require-Text $text 'skills/mpa-skill/references/aigc-disclosure\.md' 'README AI-use disclosure link'
    Require-Text $text 'docs/validation/v1\.0\.0-benchmark\.md' 'README benchmark report link'
    Require-Text $text 'pwsh -NoProfile -File tests/Test-ReliabilityScenarios\.ps1' 'README reliability scenario command'
    Require-Text $text '(?i)STATE_UNKNOWN' 'README unknown-state boundary'
}
Require-Text $readmeZh 'MPA Research Spine' 'Chinese MPA Research Spine explanation'
Require-Text $readmeEn 'MPA Research Spine' 'English MPA Research Spine explanation'
Require-Text $readmeZh '(?s)\u6570\u636E.*\u5199\u4F5C|\u5199\u4F5C.*\u6570\u636E' 'Chinese data-before-writing explanation'
Require-Text $readmeEn '(?is)data.*before.*writ|audit.*data.*before.*prose' 'English data-before-writing explanation'
Require-Text $readmeZh '(?s)\u8BD5\u70B9.*(?:\u4E0D\u80FD|\u4E0D).*\u6CDB\u5316|\u4E0D\u80FD.*\u6CDB\u5316.*\u8BD5\u70B9' 'Chinese evidence boundary'
Require-Text $readmeEn '(?is)pilot.*does not.*(?:establish|prove|generalize)' 'English evidence boundary'
$evidenceZh = [regex]::Match($readmeZh, '(?s)### 1\.0\.0 \u7684\u8BC1\u636E\u8FB9\u754C.*?(?=\r?\n## )').Value
$evidenceEn = [regex]::Match($readmeEn, '(?s)### 1\.0\.0 evidence boundary.*?(?=\r?\n## )').Value
Require-Text $readmeZh '### 1\. \u539F\u59CB\u6570\u636E\u8F6C\u5316' 'Chinese raw-data starter prompt'
Require-Text $readmeZh '### 2\. \u65E0\u6570\u636E\u7684\u6848\u4F8B/\u653F\u7B56\u5206\u6790' 'Chinese no-data starter prompt'
Require-Text $readmeZh '### 3\. \u5DF2\u9A8C\u6536\u5185\u5BB9\u7684 Word \u4EA4\u4ED8' 'Chinese Word-delivery starter prompt'
Require-Text $readmeEn '### 1\. Raw-data conversion' 'English raw-data starter prompt'
Require-Text $readmeEn '### 2\. Case/policy analysis without data' 'English no-data starter prompt'
Require-Text $readmeEn '### 3\. Accepted-content Word delivery' 'English Word-delivery starter prompt'
$zhPrompt1 = [regex]::Match($readmeZh, '(?s)### 1\. \u539F\u59CB\u6570\u636E\u8F6C\u5316.*?(?=\r?\n### 2\.)').Value
$zhPrompt2 = [regex]::Match($readmeZh, '(?s)### 2\. \u65E0\u6570\u636E\u7684\u6848\u4F8B/\u653F\u7B56\u5206\u6790.*?(?=\r?\n### 3\.)').Value
$zhPrompt3 = [regex]::Match($readmeZh, '(?s)### 3\. \u5DF2\u9A8C\u6536\u5185\u5BB9\u7684 Word \u4EA4\u4ED8.*?(?=\r?\n## )').Value
$enPrompt1 = [regex]::Match($readmeEn, '(?s)### 1\. Raw-data conversion.*?(?=\r?\n### 2\.)').Value
$enPrompt2 = [regex]::Match($readmeEn, '(?s)### 2\. Case/policy analysis without data.*?(?=\r?\n### 3\.)').Value
$enPrompt3 = [regex]::Match($readmeEn, '(?s)### 3\. Accepted-content Word delivery.*?(?=\r?\n## )').Value
Require-Text $zhPrompt1 '(?s)\u539F\u59CB\u6570\u636E.*\u5206\u6790\u672A\u88AB\u63A5\u53D7\u524D\u4E0D\u8981\u6539\u5199\u7ED3\u8BBA' 'Chinese prompt 1 raw-data content'
Require-Text $zhPrompt2 '(?s)\u6CA1\u6709\u539F\u59CB\u6570\u636E.*\u4E0D\u8981\u865A\u6784\u6570\u636E\u6216\u6548\u679C' 'Chinese prompt 2 no-data content'
Require-Text $zhPrompt3 '(?s)Word/Office.*STATE_UNKNOWN' 'Chinese prompt 3 recoverable-delivery content'
Require-Text $zhPrompt3 '(?s)(?:STATE_UNKNOWN.{0,12}\u65F6(?:\u505C\u6B62|\u6682\u505C)|(?:\u505C\u6B62|\u6682\u505C).{0,12}STATE_UNKNOWN)' 'Chinese Word prompt stops at STATE_UNKNOWN'
Reject-Text $zhPrompt3 '(?s)(?:STATE_UNKNOWN.{0,12}\u65F6\u7EE7\u7EED|\u7EE7\u7EED.{0,12}STATE_UNKNOWN)' 'Chinese Word prompt continues at STATE_UNKNOWN'
Require-Text $enPrompt1 '(?is)raw data.*do not rewrite conclusions' 'English prompt 1 raw-data content'
Require-Text $enPrompt2 '(?is)no raw data.*do not invent data or effects' 'English prompt 2 no-data content'
Require-Text $enPrompt3 '(?is)Word/Office.*STATE_UNKNOWN' 'English prompt 3 recoverable-delivery content'
Require-Text $enPrompt3 '(?is)(?:(?:stop|pause)(?:s|d|ing)?\s+at\s+STATE_UNKNOWN|STATE_UNKNOWN.{0,20}(?:stop|pause))' 'English Word prompt stops at STATE_UNKNOWN'
Reject-Text $enPrompt3 '(?is)(?:continue.{0,20}STATE_UNKNOWN|STATE_UNKNOWN.{0,20}continue)' 'English Word prompt continues at STATE_UNKNOWN'
Require-Text $readmeZh 'https://(?:dspace\.library\.uvic\.ca/items|digital\.library\.txst\.edu/items|calhoun\.nps\.edu/handle)/' 'Chinese open-thesis example link'
Require-Text $readmeEn 'https://(?:dspace\.library\.uvic\.ca/items|digital\.library\.txst\.edu/items|calhoun\.nps\.edu/handle)/' 'English open-thesis example link'

# ── CHANGELOG assertions ──
$releaseSection = [regex]::Match($changelog, '(?s)## \[1\.0\.0\] - 2026-08-24.*?(?=\r?\n## \[|\z)').Value

# ── Benchmark-backed assertions ──
if ((-not [string]::IsNullOrWhiteSpace($benchmarkResultsText)) -and (-not [string]::IsNullOrWhiteSpace($corpusText))) {
    $benchmarkResults = $benchmarkResultsText | ConvertFrom-Json
    $corpus = @($corpusText | ConvertFrom-Json | ForEach-Object { $_ })
    $paperCases = @($benchmarkResults.paper_cases)
    $noneSynthetic = $benchmarkResults.metrics.synthetic.none
    $v23Synthetic = $benchmarkResults.metrics.synthetic.'previous'
    $v24Synthetic = $benchmarkResults.metrics.synthetic.'current'
    $v23Papers = $benchmarkResults.metrics.papers.'previous'
    $v24Papers = $benchmarkResults.metrics.papers.'current'
    $developmentCount = @($paperCases | Where-Object split -eq 'development').Count
    $holdoutCount = @($paperCases | Where-Object split -eq 'holdout').Count
    $v23Unsupported = @($paperCases | Where-Object { $_.conditions.'previous'.unsupported_claim_generated }).Count
    $v24Unsupported = @($paperCases | Where-Object { $_.conditions.'current'.unsupported_claim_generated }).Count
    $chinaContextCount = @($corpus | Where-Object jurisdiction -eq 'China').Count
    $unavailablePreflight = $benchmarkResults.corpus_access.pdf_structural_preflight.unavailable
    $replicatesPerCondition = [int] $benchmarkResults.execution.replicates_per_condition
    $syntheticDeltaVsV23 = $v24Synthetic.passed - $v23Synthetic.passed
    $syntheticDeltaVsNone = $v24Synthetic.passed - $noneSynthetic.passed
    $deltaVsV23Fraction = "+$syntheticDeltaVsV23/$($v24Synthetic.total)"
    $deltaVsNoneFraction = "+$syntheticDeltaVsNone/$($v24Synthetic.total)"
    $deltaVsV23Points = "+$($benchmarkResults.metrics.synthetic.'current_minus_previous_percentage_points')"
    $deltaVsNonePoints = "+$($benchmarkResults.metrics.synthetic.'current_minus_none_percentage_points')"

    $noneMetric = "$($noneSynthetic.passed)/$($noneSynthetic.total)"
    $v23SyntheticMetric = "$($v23Synthetic.passed)/$($v23Synthetic.total)"
    $v24SyntheticMetric = "$($v24Synthetic.passed)/$($v24Synthetic.total)"
    $v23RouteMetric = "$($v23Papers.route_correct)/$($v23Papers.route_total)"
    $v24RouteMetric = "$($v24Papers.route_correct)/$($v24Papers.route_total)"
    $v23RiskMetric = "$($v23Papers.confirmed_risks_found)/$($v23Papers.confirmed_risks_total)"
    $v24RiskMetric = "$($v24Papers.confirmed_risks_found)/$($v24Papers.confirmed_risks_total)"

    Require-Text $readmeZh ('\u65E0 Skill\s*\u4E3A\s*' + [regex]::Escape($noneMetric)) 'Chinese no-skill synthetic metric'
    Require-Text $readmeZh ('\u65E9\u671F\u5185\u90E8\u8FED\u4EE3\u4E3A\s*' + [regex]::Escape($v23SyntheticMetric)) 'Chinese previous-iteration synthetic metric'
    Require-Text $readmeZh ('\u5F53\u524D\u7248\u672C\u4E3A\s*' + [regex]::Escape($v24SyntheticMetric)) 'Chinese current-version synthetic metric'
    Require-Text $readmeEn ([regex]::Escape($noneMetric) + '\s+for no skill') 'English no-skill synthetic metric'
    Require-Text $readmeEn ([regex]::Escape($v23SyntheticMetric) + '\s+for the previous iteration') 'English previous-iteration synthetic metric'
    Require-Text $readmeEn ([regex]::Escape($v24SyntheticMetric) + '\s+for the current version') 'English current-version synthetic metric'

    if (($deltaVsV23Fraction -eq $deltaVsNoneFraction) -and ($deltaVsV23Points -eq $deltaVsNonePoints)) {
        Require-Text $readmeZh ('\u76F8\u5BF9\u4E24\u4E2A\u57FA\u7EBF\u5747\u63D0\u5347\s*' + [regex]::Escape($deltaVsV23Fraction) + '.{0,30}' + [regex]::Escape($deltaVsV23Points)) 'Chinese delta against each baseline'
        Require-Text $readmeEn ('gain against each baseline was\s*' + [regex]::Escape($deltaVsV23Fraction) + '.{0,30}' + [regex]::Escape($deltaVsV23Points)) 'English delta against each baseline'
        Require-Text $releaseSection ('\u5DEE\u503C\u5747\u4E3A\s*' + [regex]::Escape($deltaVsV23Fraction) + '.{0,30}' + [regex]::Escape($deltaVsV23Points)) '1.0.0 changelog delta against each baseline'
    } else {
        Require-Text $readmeZh ('\u65E9\u671F\u5185\u90E8\u8FED\u4EE3.{0,40}' + [regex]::Escape($deltaVsV23Fraction) + '.{0,30}' + [regex]::Escape($deltaVsV23Points)) 'Chinese delta against previous iteration'
        Require-Text $readmeZh ('\u65E0 Skill.{0,40}' + [regex]::Escape($deltaVsNoneFraction) + '.{0,30}' + [regex]::Escape($deltaVsNonePoints)) 'Chinese delta against no skill'
        Require-Text $readmeEn ('previous iteration.{0,40}' + [regex]::Escape($deltaVsV23Fraction) + '.{0,30}' + [regex]::Escape($deltaVsV23Points)) 'English delta against previous iteration'
        Require-Text $readmeEn ('no skill.{0,40}' + [regex]::Escape($deltaVsNoneFraction) + '.{0,30}' + [regex]::Escape($deltaVsNonePoints)) 'English delta against no skill'
    }
    foreach ($text in @($evidenceZh, $evidenceEn)) {
        Require-Text $text ([regex]::Escape("$unavailablePreflight/$($benchmarkResults.corpus_access.papers)") + '.{0,80}UNAVAILABLE') 'README unavailable PDF preflights'
    }
    Require-Text $readmeZh ("$($paperCases.Count)\s*\u7BC7\u8BBA\u6587\u8BD5\u70B9.{0,80}$developmentCount\s*\u7BC7\u5F00\u53D1\u96C6.{0,40}$holdoutCount\s*\u7BC7.*\u7559\u51FA\u96C6") 'Chinese development/holdout split'
    Require-Text $readmeEn ("$($paperCases.Count)-paper pilot.{0,80}$developmentCount development papers.{0,40}$holdoutCount.*holdouts") 'English development/holdout split'
    if (($v23RouteMetric -eq $v24RouteMetric) -and ($v23RiskMetric -eq $v24RiskMetric) -and ($v23Unsupported -eq $v24Unsupported)) {
        $englishUnsupported = if ($v23Unsupported -eq 0) { 'zero' } else { [string] $v23Unsupported }
        Require-Text $readmeZh ("\u4E24\u4E2A\u7248\u672C\u90FD\u5B8C\u6210.{0,100}" + [regex]::Escape($v23RouteMetric) + '.{0,80}' + [regex]::Escape($v23RiskMetric) + ".{0,80}\u4E3A $v23Unsupported") 'Chinese condition-bound paper metrics'
        Require-Text $readmeEn ("both iterations.{0,100}" + [regex]::Escape($v23RouteMetric) + '.{0,80}' + [regex]::Escape($v23RiskMetric) + ".{0,80}$englishUnsupported unsupported claims") 'English condition-bound paper metrics'
        Require-Text $releaseSection ("\u4E24\u4E2A\u7248\u672C\u5747\u5B8C\u6210.{0,80}" + [regex]::Escape($v23RouteMetric) + '.{0,60}' + [regex]::Escape($v23RiskMetric) + ".{0,80}\u4E3A $v23Unsupported") '1.0.0 changelog condition-bound paper metrics'
    } else {
        foreach ($claim in @(
            @{ Text = $readmeZh; Version = '\u4E24\u4E2A\u7248\u672C\u4E2D\u7684\u65E9\u671F\u8FED\u4EE3'; Route = $v23RouteMetric; Risk = $v23RiskMetric; Unsupported = $v23Unsupported; Label = 'Chinese previous-iteration paper metrics' },
            @{ Text = $readmeZh; Version = '\u5F53\u524D\u7248\u672C'; Route = $v24RouteMetric; Risk = $v24RiskMetric; Unsupported = $v24Unsupported; Label = 'Chinese current-version paper metrics' },
            @{ Text = $readmeEn; Version = 'previous iteration'; Route = $v23RouteMetric; Risk = $v23RiskMetric; Unsupported = $v23Unsupported; Label = 'English previous-iteration paper metrics' },
            @{ Text = $readmeEn; Version = 'current version'; Route = $v24RouteMetric; Risk = $v24RiskMetric; Unsupported = $v24Unsupported; Label = 'English current-version paper metrics' },
            @{ Text = $releaseSection; Version = '\u65E9\u671F\u5185\u90E8\u8FED\u4EE3'; Route = $v23RouteMetric; Risk = $v23RiskMetric; Unsupported = $v23Unsupported; Label = '1.0.0 changelog previous-iteration paper metrics' },
            @{ Text = $releaseSection; Version = '\u5F53\u524D\u7248\u672C'; Route = $v24RouteMetric; Risk = $v24RiskMetric; Unsupported = $v24Unsupported; Label = '1.0.0 changelog current-version paper metrics' }
        )) {
            Require-Text $claim.Text ($claim.Version + '.{0,100}' + [regex]::Escape($claim.Route) + '.{0,80}' + [regex]::Escape($claim.Risk) + ".{0,80}$($claim.Unsupported)") $claim.Label
        }
    }
    Require-Text $evidenceZh ("$chinaContextCount\s*\u6761\u4E2D\u56FD\u60C5\u5883\u8BB0\u5F55") 'Chinese China-context limit'
    $englishChinaCount = if ($chinaContextCount -eq 1) { 'one' } else { [string] $chinaContextCount }
    Require-Text $evidenceEn ([regex]::Escape($englishChinaCount) + ' China-context record') 'English China-context limit'
    Require-Text $evidenceZh '(?s)\u4E0D\u80FD.{0,40}\u5F53\u524D\u7248\u672C.{0,40}\u8BBA\u6587\u8BCA\u65AD\u4F18\u4E8E\s*\u65E9\u671F\u8FED\u4EE3' 'Chinese not-superior-diagnosis boundary'
    Require-Text $evidenceEn '(?is)does not establish superior thesis diagnosis for the current version' 'English not-superior-diagnosis boundary'

    $chineseReplicateCount = if ($replicatesPerCondition -eq 1) { '\u4E00' } else { [regex]::Escape([string] $replicatesPerCondition) }
    $englishReplicateCount = if ($replicatesPerCondition -eq 1) { 'one' } else { [regex]::Escape([string] $replicatesPerCondition) }
    Require-Text $evidenceZh ('\u6BCF\u4E2A\u6761\u4EF6(?:\u53EA\u6709|\u4EC5)' + $chineseReplicateCount + '\u6B21\u54CD\u5E94') 'Chinese one-response-per-condition limit'
    Require-Text $evidenceEn ([regex]::Escape($englishReplicateCount) + '\s+response(?:s)? per condition') 'English one-response-per-condition limit'
    Require-Text $releaseSection ('\u6BCF\u4E2A\u6761\u4EF6(?:\u53EA\u6709|\u4EC5)' + $chineseReplicateCount + '\u6B21\u54CD\u5E94') '1.0.0 changelog one-response-per-condition limit'
    Require-Text $evidenceZh ("$($paperCases.Count)\s*\u7BC7(?:\u6837\u672C|\u8BD5\u70B9)\u4E0D\u662F\u603B\u4F53\u4F30\u8BA1") 'Chinese not-a-population-estimate limit'
    Require-Text $evidenceEn ("$($paperCases.Count)-paper (?:pilot|sample).{0,30}(?:rather than|not) a population estimate") 'English not-a-population-estimate limit'
    Require-Text $releaseSection ("$($paperCases.Count)\s*\u7BC7(?:\u6837\u672C|\u8BD5\u70B9)\u4E0D\u662F\u603B\u4F53\u4F30\u8BA1") '1.0.0 changelog not-a-population-estimate limit'
    foreach ($claim in @(
        @{ Text = $evidenceZh; Pattern = '\u6765\u6E90\u94FE\u63A5\u53EF\u80FD.{0,12}\u6F02\u79FB'; Reject = '\u6765\u6E90\u94FE\u63A5.{0,12}(?:\u4E0D\u4F1A|\u4E0D\u53EF\u80FD)\u6F02\u79FB'; Label = 'Chinese README source links may drift' },
        @{ Text = $evidenceEn; Pattern = 'source links(?: that)? may drift'; Reject = 'source links.{0,20}(?:cannot|can''t|will not|won''t) drift'; Label = 'English README source links may drift' },
        @{ Text = $releaseSection; Pattern = '\u6765\u6E90\u94FE\u63A5\u53EF\u80FD.{0,12}\u6F02\u79FB'; Reject = '\u6765\u6E90\u94FE\u63A5.{0,12}(?:\u4E0D\u4F1A|\u4E0D\u53EF\u80FD)\u6F02\u79FB'; Label = '1.0.0 changelog source links may drift' }
    )) {
        Require-Text $claim.Text $claim.Pattern $claim.Label
        Reject-Text $claim.Text $claim.Reject ($claim.Label + ' rejects cannot-drift wording')
    }

    $exampleSourceId = 'txst-50bce8d1-3a34-49bb-8c38-8e52b8038265'
    $exampleRiskId = 'd3-identification'
    $exampleCorpusRecord = @($corpus | Where-Object id -eq $exampleSourceId)[0]
    $examplePaper = @($paperCases | Where-Object source_id -eq $exampleSourceId)[0]
    $exampleRisk = @($examplePaper.confirmed_risks | Where-Object id -eq $exampleRiskId)[0]
    if (($null -eq $exampleCorpusRecord) -or ($null -eq $exampleRisk)) {
        $failures.Add('benchmark-backed README example source')
    } else {
        $exampleZh = [regex]::Match($readmeZh, '(?s)## \u53EF\u590D\u73B0\u5BA1\u8BA1\u793A\u4F8B.*?(?=\r?\n## )').Value
        $exampleEn = [regex]::Match($readmeEn, '(?s)## Reproducible audit example.*?(?=\r?\n## )').Value
        foreach ($exampleText in @($exampleZh, $exampleEn)) {
            Require-Text $exampleText ([regex]::Escape($exampleSourceId)) 'README example source id from corpus'
            Require-Text $exampleText ([regex]::Escape($exampleCorpusRecord.title)) 'README example title from corpus'
            Require-Text $exampleText ([regex]::Escape($exampleCorpusRecord.landing_url)) 'README example landing URL from corpus'
            Require-Text $exampleText ([regex]::Escape($exampleRisk.id)) 'README example risk id from results'
        }
        foreach ($pageClaim in @(
            @{ Id = 'd3-missingness'; ZhPrefix = 'PDF\s+\u7B2C\s*'; ZhSuffix = '\s*\u9875\u6D89\u53CA'; EnPrefix = 'PDF pages\s*'; EnSuffix = '\s+cover' },
            @{ Id = 'd3-identification'; ZhPrefix = '\u7B2C\s*'; ZhSuffix = '\s*\u9875\u663E\u793A'; EnPrefix = 'pages\s*'; EnSuffix = '\s+show' },
            @{ Id = 'd3-null-overreach'; ZhPrefix = '\u7B2C\s*'; ZhSuffix = '\s*\u9875\u7684\u65E0\u663E\u8457\u7ED3\u679C'; EnPrefix = 'pages\s*'; EnSuffix = '\s+do not' }
        )) {
            $risk = @($examplePaper.confirmed_risks | Where-Object id -eq $pageClaim.Id)[0]
            if ($null -eq $risk) {
                $failures.Add("README example page risk missing from results: $($pageClaim.Id)")
                continue
            }
            $zhPageSet = ConvertTo-PageSetPattern -Pages @($risk.pdf_pages) -Separator '\u3001'
            $enPageSet = ConvertTo-PageSetPattern -Pages @($risk.pdf_pages) -Separator ' and '
            Require-Text $exampleZh ($pageClaim.ZhPrefix + $zhPageSet + $pageClaim.ZhSuffix) "Chinese example page set from results: $($pageClaim.Id)"
            Require-Text $exampleEn ($pageClaim.EnPrefix + $enPageSet + $pageClaim.EnSuffix) "English example page set from results: $($pageClaim.Id)"
        }
    }

    Require-Text $releaseSection ('\u51BB\u7ED3\u5019\u9009\u5728\u5408\u6210\u573A\u666F\u4E2D\u4E3A\s*' + [regex]::Escape($v24SyntheticMetric)) '1.0.0 changelog current-version synthetic metric'
    if ($noneMetric -eq $v23SyntheticMetric) {
        Require-Text $releaseSection ('\u65E0 Skill \u4E0E\s*(?:\u65E9\u671F\u5185\u90E8\u8FED\u4EE3|v2\.3\.0)\s*\u5747\u4E3A\s*' + [regex]::Escape($noneMetric)) '1.0.0 changelog baseline synthetic metrics'
    } else {
        Require-Text $releaseSection ('\u65E0 Skill.{0,40}' + [regex]::Escape($noneMetric)) '1.0.0 changelog no-skill synthetic metric'
        Require-Text $releaseSection ('\u65E9\u671F\u5185\u90E8\u8FED\u4EE3.{0,40}' + [regex]::Escape($v23SyntheticMetric)) '1.0.0 changelog previous-iteration synthetic metric'
    }
    Require-Text $releaseSection ("$developmentCount\s*\u7BC7\u5F00\u53D1\u96C6\u52A0\s*$holdoutCount\s*\u7BC7\u7559\u51FA\u96C6") '1.0.0 changelog development/holdout split'
    Require-Text $releaseSection ([regex]::Escape("$unavailablePreflight/$($benchmarkResults.corpus_access.papers)") + '.{0,60}PDF.{0,30}UNAVAILABLE') '1.0.0 changelog unavailable PDF preflights'
    Require-Text $releaseSection ("$chinaContextCount\s*\u6761\u4E2D\u56FD\u60C5\u5883\u8BB0\u5F55") '1.0.0 changelog China-context limit'
    Require-Text $releaseSection '\u4E0D\u4EE3\u8868\u8BBA\u6587\u8BCA\u65AD\u66F4\u4F18' '1.0.0 changelog not-superior-diagnosis boundary'
}

Require-Text $releaseSection '### Added' '1.0.0 Added changelog section'
Require-Text $releaseSection '### Changed' '1.0.0 Changed changelog section'
Require-Text $releaseSection '### Validation' '1.0.0 Validation changelog section'
Require-Text $releaseSection '(?s)\u6570\u636E.*\u5199\u4F5C|\u5199\u4F5C.*\u6570\u636E' '1.0.0 data-first routing changelog claim'
Require-Text $releaseSection '(?is)Office.*(?:\u6062\u590D|\u53EF\u6062\u590D)|(?:\u6062\u590D|\u53EF\u6062\u590D).*Office' '1.0.0 recoverable Office changelog claim'
Require-Text $releaseSection '(?s)\u771F\u5B9E.*\u8BBA\u6587.*(?:\u9A8C\u8BC1|\u8BD5\u70B9|\u57FA\u51C6)' '1.0.0 real-thesis validation changelog claim'

# ── License & security assertions ──
Require-Text $license 'MIT License' 'MIT license title'
Require-Text $license 'Copyright \(c\) 2026 mucjustin' 'MIT copyright'
Require-Text $security '(?i)private vulnerability reporting' 'private vulnerability reporting'
Require-Text $security '(?i)credentials' 'credential reporting boundary'

# ── Privacy scanning (includes four knowledge files) ──
$trackedText = @($skill, $metadata, $deliverables, $aigcDisclosure, $caseCompetition, $researchContract, $routing, $execution, $mpaKnowledge, $templates, $abRegression, $readmeZh, $readmeEn, $changelog, $security) -join "`n"
Reject-Text $trackedText '(?i)(?<![A-Z0-9])[A-Z]:\\' 'fixed drive-letter path'
Reject-Text $trackedText '(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}' 'embedded email address'
Reject-Text $trackedText '(?i)gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}' 'credential-like token'

# ── Installed parity check ──
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
