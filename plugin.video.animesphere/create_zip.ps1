$zipFile = "plugin.video.animesphere.zip"
$sourceDir = "d:\plugin.video.animesphere"

# Create a new zip file
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($sourceDir, $zipFile)

# Remove excluded files from zip
$excludedFiles = @(
    "*.pyc",
    "__pycache__",
    ".git",
    ".pytest_cache",
    "*.log"
)

$shell = New-Object -ComObject Shell.Application
$zip = $shell.NameSpace($zipFile)

foreach ($file in $zip.Items()) {
    $filePath = Join-Path $sourceDir $file.Path
    foreach ($pattern in $excludedFiles) {
        if ($filePath -like $pattern) {
            $zip.DeleteItem($file)
            break
        }
    }
}
