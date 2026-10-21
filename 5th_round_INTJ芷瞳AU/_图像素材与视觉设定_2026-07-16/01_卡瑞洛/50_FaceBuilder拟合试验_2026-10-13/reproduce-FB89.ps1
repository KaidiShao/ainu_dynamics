param([switch]$Render)
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$taskBlender = Join-Path $taskRoot '_tools/blender/blender-4.5.14-windows-x64/blender.exe'
$taskScripts = Join-Path $taskRoot '_tools/keentools'
$rebuildDir = Join-Path $PSScriptRoot ('reproduction-fb89-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $rebuildDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $rebuildDir 'renders') | Out-Null
foreach ($name in @('Carrillo_FaceBuilder_FB86.blend','eye-mask.json')) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $rebuildDir $name) }
function Invoke-RebuildStep([string]$Source, [string]$Script, [string]$Expected, [string[]]$Extra = @()) {
 & $taskBlender --background (Join-Path $rebuildDir $Source) -t 8 --python (Join-Path $taskScripts $Script) @Extra *> (Join-Path $rebuildDir ($Script + '.log'))
 $taskLog = Get-Content -LiteralPath (Join-Path $rebuildDir ($Script + '.log')) -Raw
 if ($taskLog.Contains('Traceback') -or -not (Test-Path -LiteralPath (Join-Path $rebuildDir $Expected))) { throw ('Rebuild failed: ' + $Script) }
}
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'candidate_search_fb88.py' 'Carrillo_FaceBuilder_FB88_A.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'refine_lip_candidates_fb88.py' 'Carrillo_FaceBuilder_FB88_D.blend'
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'promote_selected_fb89.py' 'Carrillo_FaceBuilder_FB89.blend' @('--','FB88_D')
Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'prepare_editable_fb89.py' 'Carrillo_FB89_editable_working.blend'
if ($Render) {
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'render_candidates_fb88.py' 'renders/fb88_c-neutral-threequarter.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB86.blend' 'render_lip_candidates_fb88.py' 'renders/fb88_d-neutral-threequarter.png'
 Invoke-RebuildStep 'Carrillo_FaceBuilder_FB89.blend' 'final_review_fb89.py' 'FB89-geometry-audit.json'
}
Write-Output ('Rebuilt to ' + $rebuildDir)
Write-Output 'Candidate D was selected visually for limited upper-lip improvement. Whole likeness remains unapproved. Full helper has not been independently rerun end-to-end.'
