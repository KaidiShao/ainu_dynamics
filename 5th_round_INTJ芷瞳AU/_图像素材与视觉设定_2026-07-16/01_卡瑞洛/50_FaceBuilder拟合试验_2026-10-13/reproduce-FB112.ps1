param([switch]$Render)
$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\新建文件夹\ainu_dynamics'
$taskBlender = Join-Path $taskRoot '_tools\blender\blender-4.5.14-windows-x64\blender.exe'
$taskScripts = Join-Path $taskRoot '_tools\keentools'
$taskStage = Join-Path $PSScriptRoot ('reproduction-fb112-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (Test-Path -LiteralPath $taskStage) { throw 'Refusing to overwrite an existing reproduction directory.' }
New-Item -ItemType Directory -Path $taskStage | Out-Null
New-Item -ItemType Directory -Path (Join-Path $taskStage 'renders') | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Carrillo_FaceBuilder_FB98.blend') -Destination $taskStage
$taskBase = Join-Path $taskStage 'Carrillo_FaceBuilder_FB98.blend'
foreach ($taskScript in @('nasal_base_fb107.py','lip_registration_fb108.py','cheek_mandible_planes_fb109.py')) {
    & $taskBlender -b $taskBase --python (Join-Path $taskScripts $taskScript) *> (Join-Path $taskStage ($taskScript + '.log'))
    if (Select-String -LiteralPath (Join-Path $taskStage ($taskScript + '.log')) -Pattern 'Traceback' -Quiet) { throw ('Script failed: ' + $taskScript) }
}
& $taskBlender -b $taskBase --python (Join-Path $taskScripts 'integrate_night_candidates_fb112_115.py') -- FB112 *> (Join-Path $taskStage 'integrate.log')
$taskModel = Join-Path $taskStage 'Carrillo_FaceBuilder_FB112.blend'
if (!(Test-Path -LiteralPath $taskModel)) { throw 'Rebuilt model missing.' }
& $taskBlender -b $taskModel --python (Join-Path $taskScripts 'audit_candidates_oct15.py') -- FB112 *> (Join-Path $taskStage 'audit.log')
& $taskBlender -b $taskModel --python (Join-Path $taskScripts 'prepare_editable_fb112.py') *> (Join-Path $taskStage 'pack.log')
$taskExpected = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'FB112-editable-manifest.json') | ConvertFrom-Json
$taskActual = Get-Content -Raw -LiteralPath (Join-Path $taskStage 'FB112-editable-manifest.json') | ConvertFrom-Json
$taskAudit = Get-Content -Raw -LiteralPath (Join-Path $taskStage 'FB112-geometry-audit.json') | ConvertFrom-Json
$taskMatches = $taskExpected.visible_geometry_hash -eq $taskActual.visible_geometry_hash
if (!$taskMatches -or $taskAudit.nonfinite_coordinates -ne 0 -or $taskAudit.inverted_triangles_vs_base -ne 0) { throw 'Reproduction geometry validation failed.' }
if ($Render) {
    & $taskBlender -b $taskModel --python (Join-Path $taskScripts 'render_t22_round83.py') -- FB112 *> (Join-Path $taskStage 'render.log')
}
$taskReport = @{ at=(Get-Date -Format o); base='FB98'; reconstruction=$taskStage; visible_geometry_hash_matches=$taskMatches; hash=$taskActual.visible_geometry_hash; rendering_requested=[bool]$Render; scope='Geometry and packed mesh reproduction verified; color-domain script rerun. Render pixels not compared.' }
$taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'FB112-reproduction-check.json') -Encoding utf8
$taskReport | ConvertTo-Json -Depth 5
