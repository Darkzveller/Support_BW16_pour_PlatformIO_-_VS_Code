$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PlatformIOCore = if ($env:PLATFORMIO_CORE_DIR) {
    $env:PLATFORMIO_CORE_DIR
} else {
    Join-Path $env:USERPROFILE ".platformio"
}

$WorkDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ("bw16-platformio-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $WorkDirectory -Force | Out-Null

function Install-LocalPackage {
    param(
        [string]$Name,
        [string]$Archive,
        [string]$Sha256,
        [string]$ExtractDirectory
    )

    $ArchivePath = Join-Path $ProjectRoot $Archive
    $ExtractPath = Join-Path $WorkDirectory $ExtractDirectory
    $Destination = Join-Path (Join-Path $PlatformIOCore "packages") $Name

    if (-not (Test-Path $ArchivePath)) {
        throw "Archive missing: $ArchivePath. Extract the complete BW16 project before running the installer."
    }

    Write-Host "Installing $Name from the bundled archive..."
    $ActualHash = (Get-FileHash -Path $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($ActualHash -ne $Sha256.ToLowerInvariant()) {
        throw "SHA-256 mismatch for $Archive. The project archive may be incomplete."
    }

    New-Item -ItemType Directory -Path $ExtractPath -Force | Out-Null
    & tar.exe -xzf $ArchivePath -C $ExtractPath
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to extract $Archive."
    }
    if (-not (Test-Path (Join-Path $ExtractPath "package.json"))) {
        throw "Invalid PlatformIO package: $Archive."
    }

    if (Test-Path $Destination) {
        Remove-Item -Path $Destination -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    Copy-Item -Path (Join-Path $ExtractPath "*") -Destination $Destination -Recurse -Force
}

try {
    New-Item -ItemType Directory -Path (Join-Path $PlatformIOCore "packages") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $PlatformIOCore "platforms") -Force | Out-Null

    Install-LocalPackage `
        -Name "framework-arduinorealtek-amebad" `
        -Archive "vendor\framework-arduinorealtek-amebad-3.1.9-bundle.tar.gz" `
        -Sha256 "544bceb8b177ed66a5952ed616bd4ae057df30db1e4251b24994477aa632a6ee" `
        -ExtractDirectory "framework"

    Install-LocalPackage `
        -Name "toolchain-realtek-amebad" `
        -Archive "vendor\toolchain-realtek-amebad-windows-1.0.1-bundle.tar.gz" `
        -Sha256 "fd19606534ac887359506c0d3aad0945f76d82257ecd87b49b74acf43c59d210" `
        -ExtractDirectory "toolchain"

    Install-LocalPackage `
        -Name "tool-realtek-amebad" `
        -Archive "vendor\tool-realtek-amebad-windows-1.1.3-bundle.tar.gz" `
        -Sha256 "f76f7d413a620528af125806bd344513655042fa2770aa729367ad3a707889f4" `
        -ExtractDirectory "uploader"

    Install-LocalPackage `
        -Name "tool-scons" `
        -Archive "vendor\tool-scons-4.40801.0-bundle.tar.gz" `
        -Sha256 "6aff14ac126a0b019b4650e55543f2969b4bceacf60bbdd886a28bb5711b9824" `
        -ExtractDirectory "scons"

    $PlatformDestination = Join-Path (Join-Path $PlatformIOCore "platforms") "realtek-amebad"
    if (Test-Path $PlatformDestination) {
        Remove-Item -Path $PlatformDestination -Recurse -Force
    }
    Copy-Item -Path (Join-Path $ProjectRoot "platform") -Destination $PlatformDestination -Recurse -Force

    Write-Host ""
    Write-Host "BW16 support installed successfully without bzip2." -ForegroundColor Green
    Write-Host "Open this project folder in VS Code, then click PlatformIO Build."
} finally {
    if (Test-Path $WorkDirectory) {
        Remove-Item -Path $WorkDirectory -Recurse -Force
    }
}
