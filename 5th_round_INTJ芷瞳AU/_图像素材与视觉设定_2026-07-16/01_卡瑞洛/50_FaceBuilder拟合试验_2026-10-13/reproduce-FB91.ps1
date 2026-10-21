param([switch]$Render)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskBlender = Join-Path $taskRoot '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$taskScripts = Join-Path $taskRoot '_tools/keentools'
$rebuildDir = Join-Path $PSScriptRoot ('reproduction-fb91-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $rebuildDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $rebuildDir 'renders') | Out-Null
foreach ($name in @('Carrillo_FaceBuilder_FB89.blend','eye-mask.json')) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $rebuildDir $name) }
function Invoke-RebuildStep([string]$Source, [string]$Script, [string]$Expected) {
 & $taskBlender --background (Join-Path $rebuildDir $Source) -t 8 --python (Join-Path $taskScripts $Script) *> (Join-Path $rebuildDir ($Script + '.log'))
 $taskLog = Get-Content -LiteralPath (Join-Path $rebuildDir ($Script + '.log')) -Raw
 if ($taskLog.Contains('Traceback') -or -not (Test-Path -LiteralPath (Join-Path $rebuildDir $Expected))) { throw ('Rebuild failed: ' + $Script) }
}
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'pretarsal_roll_candidates_fb90.py' 'Carrillo_FaceBuilder_FB90_C.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'pretarsal_flat_candidates_fb90.py' 'Carrillo_FaceBuilder_FB90_E.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'promote_pretarsal_fb91.py' 'Carrillo_FaceBuilder_FB91.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB91.blend' 'prepare_editable_fb91.py' 'Carrillo_FB91_editable_working.blend'
if ($Render) {
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'render_pretarsal_screen_fb90.py' 'renders/fb90_c-pretarsal-front.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'render_pretarsal_flat_fb90.py' 'renders/fb90_e-pretarsal-front.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'review_pretarsal_finalists_fb90.py' 'renders/fb90_e-neutral-threequarter.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB91.blend' 'final_review_pretarsal_fb91.py' 'FB91-geometry-audit.json'
}
Write-Output ('Rebuilt to ' + $rebuildDir)
Write-Output 'D is a tentative shallow lower-lid study. Whole likeness remains unapproved. Individual steps ran; this combined helper has not been independently rerun end-to-end.'
