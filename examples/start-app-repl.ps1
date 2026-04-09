param(
    [Parameter(Mandatory = $true)]
    [string]$DeviceIp,

    [Parameter(Mandatory = $false)]
    [string]$ApkPath
)

$adbTarget = "$DeviceIp`:5555"
$appPackage = "aivane.apprepl"
$mainActivity = "$appPackage/.ui.ReplMainActivity"
$serviceName = "$appPackage/.api.ApiService"
$accessibilityService = "$appPackage/aivane.android.accessibility.AIVaneAccessibilityService"

Write-Host "Connecting to $adbTarget..."
try {
    & adb connect $adbTarget | Out-Null
} catch {
}

if ($ApkPath) {
    Write-Host "Installing APK from $ApkPath..."
    & adb -s $adbTarget install -r $ApkPath
}

Write-Host "Enabling accessibility service..."
& adb -s $adbTarget shell settings put secure enabled_accessibility_services $accessibilityService 2>$null | Out-Null
& adb -s $adbTarget shell settings put secure accessibility_enabled 1 2>$null | Out-Null
Write-Host "Note: On non-privileged Android builds, automatic accessibility enable may be denied (WRITE_SECURE_SETTINGS). Use /health permissions to decide next steps."

Write-Host "Starting AIVane REPL activity..."
& adb -s $adbTarget shell am start -n $mainActivity | Out-Null

Write-Host "Starting API service..."
try {
    & adb -s $adbTarget shell am start-foreground-service -n $serviceName | Out-Null
} catch {
}

Write-Host "Checking health..."
Start-Sleep -Seconds 2
try {
    $health = Invoke-RestMethod -Uri "http://$DeviceIp`:8080/health"
    $health | ConvertTo-Json -Depth 6
    if ($health.permissions -and $health.permissions.accessibilityEnabled -eq $false) {
        Write-Warning "Accessibility is still disabled. Open Android Settings and enable the AIVane accessibility service before using --launch/--list/--tap/--input."
    }
} catch {
    Write-Warning "Health check failed. Confirm the phone is on the same LAN and the AIVane app/service is running."
}

Write-Host "AIVane REPL should now be available at http://$DeviceIp`:8080"
