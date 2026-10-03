param(
    [Parameter(Mandatory = $true)]
    [string[]]$InputPaths,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [int]$Columns = 4,
    [int]$CellWidth = 320,
    [int]$CellHeight = 230
)

Add-Type -AssemblyName System.Drawing

$margin = 20
$labelHeight = 54
$rows = [Math]::Ceiling($InputPaths.Count / $Columns)
$canvasWidth = ($Columns * $CellWidth) + (($Columns + 1) * $margin)
$canvasHeight = ($rows * $CellHeight) + (($rows + 1) * $margin)

$canvas = New-Object System.Drawing.Bitmap($canvasWidth, $canvasHeight)
$graphics = [System.Drawing.Graphics]::FromImage($canvas)
$graphics.Clear([System.Drawing.Color]::FromArgb(245, 243, 239))
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

$font = New-Object System.Drawing.Font('Microsoft YaHei UI', 10)
$textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(36, 36, 36))
$borderPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(205, 201, 194), 1)

try {
    for ($i = 0; $i -lt $InputPaths.Count; $i++) {
        $path = $InputPaths[$i]
        $row = [Math]::Floor($i / $Columns)
        $column = $i % $Columns
        $x = $margin + ($column * ($CellWidth + $margin))
        $y = $margin + ($row * ($CellHeight + $margin))
        $imageAreaHeight = $CellHeight - $labelHeight

        $image = [System.Drawing.Image]::FromFile($path)
        try {
            $scale = [Math]::Min($CellWidth / $image.Width, $imageAreaHeight / $image.Height)
            $drawWidth = [int]($image.Width * $scale)
            $drawHeight = [int]($image.Height * $scale)
            $drawX = $x + [int](($CellWidth - $drawWidth) / 2)
            $drawY = $y + [int](($imageAreaHeight - $drawHeight) / 2)
            $graphics.DrawImage($image, $drawX, $drawY, $drawWidth, $drawHeight)
            $graphics.DrawRectangle($borderPen, $x, $y, $CellWidth, $imageAreaHeight)
        }
        finally {
            $image.Dispose()
        }

        $label = [System.IO.Path]::GetFileNameWithoutExtension($path)
        $labelRect = New-Object System.Drawing.RectangleF($x, ($y + $imageAreaHeight + 4), $CellWidth, ($labelHeight - 4))
        $graphics.DrawString($label, $font, $textBrush, $labelRect)
    }

    $outputDirectory = [System.IO.Path]::GetDirectoryName($OutputPath)
    if ($outputDirectory -and -not (Test-Path -LiteralPath $outputDirectory)) {
        New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
    }
    $canvas.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $font.Dispose()
    $textBrush.Dispose()
    $borderPen.Dispose()
    $graphics.Dispose()
    $canvas.Dispose()
}

Write-Output $OutputPath
