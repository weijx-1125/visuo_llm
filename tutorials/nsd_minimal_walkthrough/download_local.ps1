param([Parameter(ValueFromRemainingArguments=$true)][string[]]$DownloadArgs)
# Restore PATH when finished. Does not edit system environment or execution policy.
$pythonExe = (Get-Command python -ErrorAction Stop).Source
$libraryBin = Join-Path (Split-Path $pythonExe) 'Library\bin'
$previousPath = $env:PATH
try {
    if (Test-Path -LiteralPath $libraryBin) {
        $env:PATH = "$libraryBin;$previousPath"
    }
    & $pythonExe -c 'import ssl; print(ssl.OPENSSL_VERSION)'
    if ($LASTEXITCODE -ne 0) { throw 'Python SSL unavailable; use an activated Anaconda Prompt.' }
    & $pythonExe (Join-Path $PSScriptRoot 'download_data.py') @DownloadArgs
    if ($LASTEXITCODE -ne 0) { throw 'Downloader failed; see the error above.' }
} finally {
    $env:PATH = $previousPath
}
