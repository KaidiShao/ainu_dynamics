param([switch]$Render)
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
for ($taskIndex = 0; $taskIndex -lt 4; $taskIndex++) { $taskRoot = Split-Path -Parent $taskRoot }
$taskBlender = Join-Path $taskRoot '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$taskScripts = Join-Path $taskRoot '_tools/keentools'
if (!(Test-Path -LiteralPath $taskBlender)) { throw 'Expected bundled Blender not found.' }
$taskStage = Join-Path $PSScriptRoot ('reproduction-fb189-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (Test-Path -LiteralPath $taskStage) { throw 'Refusing to overwrite an existing reconstruction.' }
New-Item -ItemType Directory -Path $taskStage | Out-Null
New-Item -ItemType Directory -Path (Join-Path $taskStage 'renders') | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Carrillo_FB188_editable_working.blend') -Destination (Join-Path $taskStage 'Carrillo_FaceBuilder_FB188.blend')

$taskLog = Join-Path $taskStage 'rebuild-pipeline.log'
& $taskBlender -b (Join-Path $taskStage 'Carrillo_FaceBuilder_FB188.blend') -t 12 --python (Join-Path $taskScripts 'rebuild_fb189_pipeline.py') *> $taskLog
if (Select-String -LiteralPath $taskLog -Pattern 'Traceback|FAILED numerical' -Quiet) { throw ('Rebuild failed; inspect ' + $taskLog) }
$taskExpected = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'FB189-editable-manifest.json') | ConvertFrom-Json
$taskActual = Get-Content -Raw -LiteralPath (Join-Path $taskStage 'FB189-editable-manifest.json') | ConvertFrom-Json
$taskGeometryMatches = $taskExpected.visible_geometry_hash -eq $taskActual.visible_geometry_hash
$taskTopologyMatches = $taskExpected.topology_and_vertex_color_hash -eq $taskActual.topology_and_vertex_color_hash
$taskGroomMatches = $taskExpected.groom_profile_hash -eq $taskActual.groom_profile_hash
$taskUvMatches = $taskExpected.uv_and_binding_hash -eq $taskActual.uv_and_binding_hash
if (!$taskGeometryMatches -or !$taskTopologyMatches -or !$taskGroomMatches -or !$taskUvMatches) { throw 'Reconstruction geometry/topology/vertex-color/groom/UV hashes differ.' }
$taskAudit = Get-Content -Raw -LiteralPath (Join-Path $taskStage 'FB189-ocular-attachment-audit.json') | ConvertFrom-Json
if (@($taskAudit.objects | Where-Object { $_.nonfinite -gt 0 -or $_.near_zero_area_triangles -gt 0 -or $_.nonadjacent_BVH_overlap_pairs -gt 0 }).Count -gt 0) { throw 'Rebuilt ocular attachments failed recorded checks.' }
if ($Render) { & $taskBlender -b (Join-Path $taskStage 'Carrillo_FaceBuilder_FB189.blend') -t 12 --python (Join-Path $taskScripts 'review_integrated_fb189.py') *> (Join-Path $taskStage 'render.log') }
$taskReport = @{ at=(Get-Date -Format o); base='FB188'; reconstruction=$taskStage; visible_geometry_hash_matches=$taskGeometryMatches; topology_and_vertex_color_hash_matches=$taskTopologyMatches; groom_profile_hash_matches=$taskGroomMatches; groom_profile_hash=$taskActual.groom_profile_hash; uv_and_binding_hash_matches=$taskUvMatches; uv_and_binding_hash=$taskActual.uv_and_binding_hash; geometry_hash=$taskActual.visible_geometry_hash; topology_and_vertex_color_hash=$taskActual.topology_and_vertex_color_hash; rendering_requested=[bool]$Render; scope='Recorded geometry, face topology, vertex colors and groom radius/settings and visible UV/bindings reproduced. Not pixel identity or whole-character likeness.' }
$taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'FB189-reproduction-check.json') -Encoding utf8
$taskReport | ConvertTo-Json -Depth 5
