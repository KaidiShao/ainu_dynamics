param([switch]$Render)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskBlender = Join-Path $taskRoot '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$taskScripts = Join-Path $taskRoot '_tools/keentools'
$rebuildDir = Join-Path $PSScriptRoot ('reproduction-fb84-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $rebuildDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $rebuildDir 'renders') | Out-Null
foreach ($name in @('Carrillo_FaceBuilder_FB01.blend','Carrillo_FaceBuilder_FB82.blend','eye-mask.json')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $rebuildDir $name)
}
function Invoke-RebuildStep([string]$Source, [string]$Script, [string]$Expected) {
    & $taskBlender --background (Join-Path $rebuildDir $Source) --python (Join-Path $taskScripts $Script) *> (Join-Path $rebuildDir ($Script + '.log'))
    # KeenTools can return exit1 during shutdown after saving. Validate output
    # and traceback rather than treating exit0 as sufficient proof.
    $taskLog = Get-Content -LiteralPath (Join-Path $rebuildDir ($Script + '.log')) -Raw
    if ($taskLog.Contains('Traceback') -or -not (Test-Path -LiteralPath (Join-Path $rebuildDir $Expected))) { throw ('Rebuild failed: ' + $Script) }
}
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB01.blend' 'refit_t22_only_fb83.py' 'FB83_T22_only_raw_fit.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB82.blend' 'integrate_t22_only_fb83.py' 'Carrillo_FaceBuilder_FB83.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB83.blend' 'orbital_roof_t22_fb84.py' 'Carrillo_FaceBuilder_FB84.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB84.blend' 'finalize_orbital_strength_fb84.py' 'FB84-orbit.json'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB84.blend' 'prepare_editable_t22_fb84.py' 'Carrillo_FB84_editable_working.blend'
if ($Render) { Invoke-RebuildStep 'Carrillo_FaceBuilder_FB84.blend' 'final_review_t22_fb84.py' 'FB84-geometry-audit.json' }
Write-Output ('Saved real rebuilt project to ' + $rebuildDir)
Write-Output 'This is a reproducibility aid, not likeness approval. Requires the installed official FaceBuilder plugin and valid licence for refitting.'
