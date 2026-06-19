# Step 1 backup: full repo ZIP, timestamped, before any change.
# Run from the OfflineFeed repo root.
$stamp = Get-Date -Format yyyyMMdd-HHmmss
$out = "..\OfflineFeed-backup-$stamp.zip"
Compress-Archive -Path * -DestinationPath $out -Force
Write-Host "Backup written to: $out"
