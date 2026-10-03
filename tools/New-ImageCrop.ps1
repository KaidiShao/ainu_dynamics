param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [Parameter(Mandatory = $true)]
    [int]$X,

    [Parameter(Mandatory = $true)]
    [int]$Y,

    [Parameter(Mandatory = $true)]
    [int]$Width,

    [Parameter(Mandatory = $true)]
    [int]$Height,

    [int]$OutputWidth = 768,
    [int]$OutputHeight = 1024
)

Add-Type -AssemblyName System.Drawing

$source = [System.Drawing.Image]::FromFile($SourcePath)
try {
    $x1 = [Math]::Max(0, $X)
    $y1 = [Math]::Max(0, $Y)
    $w1 = [Math]::Min($Width, $source.Width - $x1)
    $h1 = [Math]::Min($Height, $source.Height - $y1)

    $targetRatio = $OutputWidth / $OutputHeight
    $sourceRatio = $w1 / $h1

    if ($sourceRatio -gt $targetRatio) {
        $adjustedWidth = [int]($h1 * $targetRatio)
        $x1 += [int](($w1 - $adjustedWidth) / 2)
        $w1 = $adjustedWidth
    }
    elseif ($sourceRatio -lt $targetRatio) {
        $adjustedHeight = [int]($w1 / $targetRatio)
        $y1 += [int](($h1 - $adjustedHeight) / 2)
        $h1 = $adjustedHeight
    }

    $bitmap = New-Object System.Drawing.Bitmap($OutputWidth, $OutputHeight)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.Clear([System.Drawing.Color]::FromArgb(235, 233, 229))
        $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
        $destination = New-Object System.Drawing.Rectangle(0, 0, $OutputWidth, $OutputHeight)
        $sourceRect = New-Object System.Drawing.Rectangle($x1, $y1, $w1, $h1)
        $graphics.DrawImage($source, $destination, $sourceRect, [System.Drawing.GraphicsUnit]::Pixel)

        $outputDirectory = [System.IO.Path]::GetDirectoryName($OutputPath)
        if ($outputDirectory -and -not (Test-Path -LiteralPath $outputDirectory)) {
            New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
        }
        $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}
finally {
    $source.Dispose()
}

Write-Output $OutputPath
