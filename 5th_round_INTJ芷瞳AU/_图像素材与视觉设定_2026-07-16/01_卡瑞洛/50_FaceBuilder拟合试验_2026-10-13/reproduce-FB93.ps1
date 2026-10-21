param([switch]$Render)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskBlender = Join-Path $taskRoot '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$taskScripts = Join-Path $taskRoot '_tools/keentools'
$rebuildDir = Join-Path $PSScriptRoot ('reproduction-fb93-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $rebuildDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $rebuildDir 'renders') | Out-Null
foreach ($name in @('Carrillo_FaceBuilder_FB89.blend','eye-mask.json')) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $rebuildDir $name) }
function Invoke-RebuildStep([string]$Source, [string]$Script, [string]$Expected) {
 & $taskBlender --background (Join-Path $rebuildDir $Source) -t 8 --python (Join-Path $taskScripts $Script) *> (Join-Path $rebuildDir ($Script + '.log'))
 $taskLog = Get-Content -LiteralPath (Join-Path $rebuildDir ($Script + '.log')) -Raw
 if ($taskLog.Contains('Traceback') -or -not (Test-Path -LiteralPath (Join-Path $rebuildDir $Expected))) { throw ('Rebuild failed: ' + $Script) }
}
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'wide_crescent_fb92.py' 'Carrillo_FaceBuilder_FB92_C.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'flat_wide_crescent_fb92.py' 'Carrillo_FaceBuilder_FB92_D.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'promote_wide_fb93.py' 'Carrillo_FaceBuilder_FB93.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB93.blend' 'prepare_editable_fb93.py' 'Carrillo_FB93_editable_working.blend'
if ($Render) {
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'render_wide_crescent_fb92.py' 'renders/fb92_c-pretarsal-front.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'render_flat_wide_fb92.py' 'renders/fb92_d-pretarsal-front.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'review_wide_finalists_fb92.py' 'renders/fb92_d-neutral-threequarter.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB93.blend' 'final_review_wide_fb93.py' 'FB93-geometry-audit.json'
}
Write-Output ('Rebuilt to ' + $rebuildDir)
Write-Output 'D is a tentative broader lower-lid study. Whole likeness remains unapproved. Individual steps ran; combined helper has not been independently rerun end-to-end.'
