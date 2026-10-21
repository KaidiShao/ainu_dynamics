param([switch]$Render)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskBlender = Join-Path $taskRoot '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$taskScripts = Join-Path $taskRoot '_tools/keentools'
$rebuildDir = Join-Path $PSScriptRoot ('reproduction-fb86-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $rebuildDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $rebuildDir 'renders') | Out-Null
foreach ($name in @('Carrillo_FaceBuilder_FB84.blend','eye-mask.json')) {
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $rebuildDir $name)
}
function Invoke-RebuildStep([string]$Source, [string]$Script, [string]$Expected) {
 & $taskBlender --background (Join-Path $rebuildDir $Source) -t 8 --python (Join-Path $taskScripts $Script) *> (Join-Path $rebuildDir ($Script + '.log'))
 $taskLog = Get-Content -LiteralPath (Join-Path $rebuildDir ($Script + '.log')) -Raw
 if ($taskLog.Contains('Traceback') -or -not (Test-Path -LiteralPath (Join-Path $rebuildDir $Expected))) { throw ('Rebuild failed: ' + $Script) }
}
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB84.blend' 'lower_lid_t22_fb85.py' 'Carrillo_FaceBuilder_FB85_L2.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB85_L2.blend' 'nasal_planes_t22_fb86.py' 'Carrillo_FaceBuilder_FB86.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'prepare_editable_t22_fb86.py' 'Carrillo_FB86_editable_working.blend'
if ($Render) {
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'final_review_t22_fb86.py' 'FB86-geometry-audit.json'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'render_strict_profile_fb86.py' 'renders/fb86-strict-profile.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'render_lower_lid_fb85.py' 'renders/fb85-lid-front-two-pixels.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'render_nasal_planes_fb86.py' 'renders/fb86-nose-material-quarter-full.png'
}
Write-Output ('Saved rebuilt geometry to ' + $rebuildDir)
Write-Output 'FB87 was rejected and is not merged. This script rebuilds from the preserved FB84 checkpoint. It does not establish likeness.'
