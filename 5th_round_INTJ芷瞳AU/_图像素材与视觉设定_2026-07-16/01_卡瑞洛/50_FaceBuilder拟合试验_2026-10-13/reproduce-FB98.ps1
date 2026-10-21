param([switch]$Render)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskBlender = Join-Path $taskRoot '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$taskScripts = Join-Path $taskRoot '_tools/keentools'
$rebuildDir = Join-Path $PSScriptRoot ('reproduction-fb98-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $rebuildDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $rebuildDir 'renders') | Out-Null
foreach ($name in @('Carrillo_FaceBuilder_FB93.blend','eye-mask.json')) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $rebuildDir $name) }
function Invoke-RebuildStep([string]$Source, [string]$Script, [string]$Expected) {
 & $taskBlender --background (Join-Path $rebuildDir $Source) -t 8 --python (Join-Path $taskScripts $Script) *> (Join-Path $rebuildDir ($Script + '.log'))
 $taskLog = Get-Content -LiteralPath (Join-Path $rebuildDir ($Script + '.log')) -Raw
 if ($taskLog.Contains('Traceback') -or -not (Test-Path -LiteralPath (Join-Path $rebuildDir $Expected))) { throw ('Rebuild failed: ' + $Script) }
}
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB93.blend' 'canthus_arc_fb95.py' 'Carrillo_FaceBuilder_FB95_B.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB93.blend' 'lowerface_fb96.py' 'Carrillo_FaceBuilder_FB96_B.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB93.blend' 'integrate_oct15_fb98.py' 'Carrillo_FaceBuilder_FB98.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB98.blend' 'prepare_editable_fb98.py' 'Carrillo_FB98_editable_working.blend'
if ($Render) {
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB98.blend' 'review_oct15_fb98.py' 'FB98-geometry-audit.json'
}
Write-Output ('Rebuilt to ' + $rebuildDir)
Write-Output 'FB98 remains a provisional local working revision, not a likeness approval.'
