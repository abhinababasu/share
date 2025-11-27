# -----------------------------------------
# CONFIG
# -----------------------------------------
$HugoProject     = "D:\MyGallerySite"
$LightroomExport = "D:\PublicPortfolio"
$ContentFolder   = "$HugoProject\content"
$PublicFolder    = "$HugoProject\public"

Write-Host "Parameters"  -ForegroundColor Green
Write-Host "  Lightroom export at $LightroomExport"  -ForegroundColor Yellow
Write-Host "  Using Hugo project at $HugoProject" -ForegroundColor Yellow
Write-Host "  Content folder at $ContentFolder"  -ForegroundColor Yellow
Write-Host ""

# -----------------------------------------
# Remove ALL old JPGs from Hugo content (except feature.jpg)
# -----------------------------------------
Write-Host "Cleaning old JPGs from Hugo content..." -ForegroundColor Green

Get-ChildItem -Path $ContentFolder -Recurse -Include *.jpg, *.jpeg, *.mp4 `
| Where-Object { $_.Name -ne 'feature.jpg' } `
| ForEach-Object {
    Write-Host "  Deleting $($_.FullName)"
    Remove-Item $_.FullName
}

# -----------------------------------------
# MIRROR Lightroom export → Hugo content
# -----------------------------------------
Write-Host ""
Write-Host "Copying Lightroom export into Hugo content..." -ForegroundColor Green

# /E = include subdirs, including empty ones
robocopy $LightroomExport $ContentFolder *.jpg *.jpeg *.mp4 /E /NFL /NDL /NJH /NJS /NC /NP /TEE

Write-Host ""
Write-Host "  Lightroom sync complete."

# -----------------------------------------
# Generate feature.jpg if no images in folder
# -----------------------------------------
Write-Host ""
Write-Host "Generating feature.jpg" -ForegroundColor Green
Get-ChildItem -Directory -Recurse $ContentFolder | ForEach-Object {
    $folder  = $_.FullName
    $feature = Join-Path $folder "feature.jpg"

    # 1. Does this folder already have images? If yes, do NOTHING.
    $localImages = Get-ChildItem -Path $folder -File |
                   Where-Object { $_.Extension -in '.jpg', '.jpeg', '.JPG', '.JPEG' }

    if ($localImages.Count -gt 0) {
        # Folder already has its own images; skip it entirely.
        return
    }

    # 2. Folder has NO images of its own → look in subfolders
    $recursiveImages = Get-ChildItem -Path $folder -Recurse -File |
                       Where-Object { $_.Extension -in '.jpg', '.jpeg', '.JPG', '.JPEG' }

    if ($recursiveImages.Count -eq 0) {
        # No images anywhere under this folder → nothing to do
        return
    }

    # 3. Folder is “empty” but children have images → create feature.jpg from a child
    if (-not (Test-Path $feature)) {
        $rand = Get-Random -Minimum 0 -Maximum $recursiveImages.Count
        $img  = $recursiveImages[$rand]
        Write-Host "Random feature.jpg for $folder → $($img.Name)"
        Copy-Item -LiteralPath $img.FullName -Destination $feature
    }
}


# -------------------------------------------------
# Generate index.md/_index.md in folder for Hugo
# -------------------------------------------------
Write-Host ""
Write-Host "Ensuring Hugo index markdown files (_index.md / index.md)..." -ForegroundColor Green

# Ensure root _index.md under content/
$rootIndex = Join-Path $ContentFolder "_index.md"
if (-not (Test-Path $rootIndex)) {
    Write-Host "  Creating root _index.md"
@"
---
title: "Photos"
---
"@ | Set-Content -LiteralPath $rootIndex -Encoding UTF8
}

# For every subfolder, create either _index.md (if it has sub-dir) or index.md (if it doesn’t)
Get-ChildItem -Path $ContentFolder -Directory -Recurse | ForEach-Object {
    $folder     = $_.FullName
    $folderName = $_.Name

    # Skip the content root itself (we already handled it)
    if ($folder -eq $ContentFolder) { return }

    $hasSubdirs = (Get-ChildItem -Path $folder -Directory).Count -gt 0

    # Folder display name from folder name
    $safeTitle = $folderName -replace '"', '\"'

    if ($hasSubdirs) {
        # Section / branch → _index.md
        $mdPath = Join-Path $folder "_index.md"
    }
    else {
        # Leaf album → index.md
        $mdPath = Join-Path $folder "index.md"
    }

    if (-not (Test-Path $mdPath)) {
        Write-Host "  Creating $(Split-Path -Leaf $mdPath) in $folder"
@"
---
title: "$safeTitle"
---
"@ | Set-Content -LiteralPath $mdPath -Encoding UTF8
    }
}


Write-Host "  Done"
# -----------------------------------------
# Run Hugo build
# -----------------------------------------
Write-Host "Building Hugo site..." -ForegroundColor Green

Set-Location $HugoProject
hugo --cleanDestinationDir

# -----------------------------------------
# MIRROR Hugo → Azure VM via rclone
# -----------------------------------------
Write-Host ""
Write-Host "Syncing to Azure VM (mirror mode)..." -ForegroundColor Green

# --delete-during ensures exact 1:1 mirror on remote
rclone sync `
    "$PublicFolder" `
    bgvm:/home/azureuser/site `
    --delete-during `
    --checksum `
    --progress

# -----------------------------------------
# 5. Reload Caddy
# -----------------------------------------
Write-Host ""
Write-Host "Reloading Caddy on the VM..."
ssh bgvm "docker exec caddy_server caddy reload"

Write-Host ""
Write-Host "Publishing completed successfully!"

