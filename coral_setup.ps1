# Register the StudySync CSVs as a Coral file-backend source and run the join.
# Reference: https://withcoral.com/docs/reference/source-spec-reference
$ErrorActionPreference = 'Stop'

# Make sure coral.exe is on PATH for this session
$binDir = Join-Path $env:USERPROFILE '.local\bin'
if (Test-Path (Join-Path $binDir 'coral.exe')) {
    $env:Path = "$binDir;$env:Path"
}

$spec = Join-Path $PSScriptRoot 'studysync.coral.yaml'

Write-Host "==> Linting source spec"
coral source lint $spec

Write-Host "`n==> Adding 'studysync' source from spec"
coral source add --file $spec

Write-Host "`n==> Listing tables in the Coral catalog"
coral sql "SELECT schema_name, table_name FROM coral.tables WHERE schema_name = 'studysync' ORDER BY table_name"

Write-Host "`n==> StudySync joined query"
$query = "SELECT a.subject, a.assignment, a.deadline, n.note_topic FROM studysync.assignments a JOIN studysync.notes n ON a.subject = n.subject ORDER BY a.deadline"
coral sql $query
