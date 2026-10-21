param([switch]$Render)
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
for ($taskIndex = 0; $taskIndex -lt 4; $taskIndex++) { $taskRoot = Split-Path -Parent $taskRoot }
$taskBlender = Join-Path $taskRoot '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$taskScripts = Join-Path $taskRoot '_tools/keentools'
if (!(Test-Path -LiteralPath $taskBlender)) { throw 'Expected bundled Blender not found.' }
$taskStage = Join-Path $PSScriptRoot ('reproduction-fb133-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (Test-Path -LiteralPath $taskStage) { throw 'Refusing to overwrite an existing reconstruction.' }
New-Item -ItemType Directory -Path $taskStage | Out-Null
New-Item -ItemType Directory -Path (Join-Path $taskStage 'renders') | Out-Null
foreach ($taskInput in @('Carrillo_FaceBuilder_FB98.blend','eye-mask.json')) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $taskInput) -Destination $taskStage }
$taskLog = Join-Path $taskStage 'rebuild-pipeline.log'
& $taskBlender -b (Join-Path $taskStage 'Carrillo_FaceBuilder_FB98.blend') --python (Join-Path $taskScripts 'rebuild_fb133_pipeline.py') *> $taskLog
if (Select-String -LiteralPath $taskLog -Pattern 'Traceback|FAILED numerical' -Quiet) { throw ('Rebuild failed; inspect ' + $taskLog) }
$taskExpected = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'FB133-editable-manifest.json') | ConvertFrom-Json
$taskActual = Get-Content -Raw -LiteralPath (Join-Path $taskStage 'FB133-editable-manifest.json') | ConvertFrom-Json
$taskGeometryMatches = $taskExpected.visible_geometry_hash -eq $taskActual.visible_geometry_hash
$taskTopologyMatches = $taskExpected.topology_and_vertex_color_hash -eq $taskActual.topology_and_vertex_color_hash
if (!$taskGeometryMatches -or !$taskTopologyMatches) { throw 'Reconstruction geometry/topology/vertex-color hashes differ.' }
$taskAudit = Get-Content -Raw -LiteralPath (Join-Path $taskStage 'FB133-ocular-attachment-audit.json') | ConvertFrom-Json
if (@($taskAudit.objects | Where-Object { $_.nonfinite -gt 0 -or $_.near_zero_area_triangles -gt 0 -or $_.nonadjacent_BVH_overlap_pairs -gt 0 }).Count -gt 0) { throw 'Rebuilt ocular attachments failed recorded checks.' }
if ($Render) { & $taskBlender -b (Join-Path $taskStage 'Carrillo_FaceBuilder_FB133.blend') --python (Join-Path $taskScripts 'review_integrated_fb133.py') *> (Join-Path $taskStage 'render.log') }
$taskReport = @{ at=(Get-Date -Format o); base='FB98'; reconstruction=$taskStage; visible_geometry_hash_matches=$taskGeometryMatches; topology_and_vertex_color_hash_matches=$taskTopologyMatches; geometry_hash=$taskActual.visible_geometry_hash; topology_and_vertex_color_hash=$taskActual.topology_and_vertex_color_hash; rendering_requested=[bool]$Render; scope='Recorded geometry, face topology and vertex colors reproduced. Not pixel identity or whole-character likeness.' }
$taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'FB133-reproduction-check.json') -Encoding utf8
$taskReport | ConvertTo-Json -Depth 5
