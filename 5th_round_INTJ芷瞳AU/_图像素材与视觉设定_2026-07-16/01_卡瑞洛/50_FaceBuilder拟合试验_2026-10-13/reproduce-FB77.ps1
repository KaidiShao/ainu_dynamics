param([switch]$Render)
$ErrorActionPreference = 'Stop'
$modelDir = $PSScriptRoot
$projectDir = (Get-Item -LiteralPath $modelDir).Parent.Parent.Parent.Parent.FullName
$blenderPath = Join-Path $projectDir '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$scriptDir = Join-Path $projectDir '_tools/keentools'
$runName = 'reproduction-run-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
$runDir = Join-Path $modelDir $runName
if (Test-Path -LiteralPath $runDir) { throw 'Reproduction directory already exists; preserving it.' }
if (-not (Test-Path -LiteralPath $blenderPath)) { throw 'Bundled Blender not found in the project.' }
New-Item -ItemType Directory -Path $runDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $runDir 'renders') | Out-Null
Copy-Item -LiteralPath (Join-Path $modelDir 'Carrillo_FaceBuilder_FB75.blend') -Destination (Join-Path $runDir 'Carrillo_FaceBuilder_FB75.blend')
& $blenderPath -b (Join-Path $runDir 'Carrillo_FaceBuilder_FB75.blend') --python (Join-Path $scriptDir 'lower_lip_underside_fb77.py') *> (Join-Path $runDir 'rebuild.log')
$rebuiltPath = Join-Path $runDir 'Carrillo_FaceBuilder_FB77.blend'
if (-not (Test-Path -LiteralPath $rebuiltPath)) { throw 'FB77 build failed; inspect rebuild.log.' }
& $blenderPath -b $rebuiltPath --python (Join-Path $scriptDir 'audit_export_geometry.py') -- FB77 *> (Join-Path $runDir 'audit.log')
$auditPath = Join-Path $runDir 'FB77-geometry-audit.json'
if (-not (Test-Path -LiteralPath $auditPath)) { throw 'Audit failed; inspect audit.log.' }
$audit = Get-Content -LiteralPath $auditPath -Raw | ConvertFrom-Json
if ($audit.nonfinite_coordinates -or $audit.degenerate_triangles -or $audit.collapsed_edges -or $audit.inverted_triangles_vs_base) { throw 'Mesh audit reported a geometry defect.' }
if ($Render) {
    & $blenderPath -b $rebuiltPath --python (Join-Path $scriptDir 'render_review_fb77.py') *> (Join-Path $runDir 'render.log')
    if (-not (Test-Path -LiteralPath (Join-Path $runDir 'renders/fb77-directional-side.png'))) { throw 'Rendering did not complete; inspect render.log.' }
}
Write-Output "Rebuilt independently in: $runDir"
Write-Output 'Geometry audit is not a likeness approval.'
