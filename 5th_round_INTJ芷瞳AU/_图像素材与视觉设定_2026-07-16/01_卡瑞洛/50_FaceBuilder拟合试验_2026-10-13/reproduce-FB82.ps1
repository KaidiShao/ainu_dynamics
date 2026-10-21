param([switch]$Render)
$ErrorActionPreference = 'Stop'
$modelDir = $PSScriptRoot
$projectDir = (Get-Item -LiteralPath $modelDir).Parent.Parent.Parent.Parent.FullName
$blenderPath = Join-Path $projectDir '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$scriptDir = Join-Path $projectDir '_tools/keentools'
$runDir = Join-Path $modelDir ('reproduction-fb82-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (Test-Path -LiteralPath $runDir) { throw 'Preserving existing reproduction directory.' }
New-Item -ItemType Directory -Path $runDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $runDir 'renders') | Out-Null
Copy-Item -LiteralPath (Join-Path $modelDir 'Carrillo_FaceBuilder_FB77.blend') -Destination (Join-Path $runDir 'Carrillo_FaceBuilder_FB77.blend')
& $blenderPath -b (Join-Path $runDir 'Carrillo_FaceBuilder_FB77.blend') --python (Join-Path $scriptDir 'scalp_coverage_fb82.py') *> (Join-Path $runDir 'rebuild.log')
$rebuiltPath = Join-Path $runDir 'Carrillo_FaceBuilder_FB82.blend'
if (-not (Test-Path -LiteralPath $rebuiltPath)) { throw 'Build failed; inspect rebuild.log.' }
& $blenderPath -b $rebuiltPath --python (Join-Path $scriptDir 'audit_export_geometry.py') -- FB82 *> (Join-Path $runDir 'audit.log')
$auditPath = Join-Path $runDir 'FB82-geometry-audit.json'
if (-not (Test-Path -LiteralPath $auditPath)) { throw 'Audit failed.' }
$audit = Get-Content -LiteralPath $auditPath -Raw | ConvertFrom-Json
if ($audit.nonfinite_coordinates -or $audit.degenerate_triangles -or $audit.collapsed_edges -or $audit.inverted_triangles_vs_base) { throw 'Geometry audit defect.' }
if ($Render) {
    & $blenderPath -b $rebuiltPath --python (Join-Path $scriptDir 'render_coverage_fb82.py') *> (Join-Path $runDir 'render-coverage.log')
    & $blenderPath -b $rebuiltPath --python (Join-Path $scriptDir 'render_final_review_fb82.py') *> (Join-Path $runDir 'render-review.log')
    if (-not (Test-Path -LiteralPath (Join-Path $runDir 'renders/fb82-directional-side.png'))) { throw 'Render incomplete; inspect logs.' }
}
Write-Output "Independent FB82 build: $runDir"
Write-Output 'This validates reproducibility only, not likeness.'
