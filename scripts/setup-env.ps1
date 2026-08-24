# SentinelOps Environment Setup Script
# This script loads .env variables and validates Phase 0 prerequisites

param(
    [switch]$Check = $false  # Just check status, don't apply
)

function Load-EnvFile {
    $envFile = Join-Path $PSScriptRoot ".." ".env"

    if (-not (Test-Path $envFile)) {
        Write-Host "❌ .env file not found at $envFile" -ForegroundColor Red
        Write-Host "   Create it from .env.example:" -ForegroundColor Yellow
        Write-Host "   cp .env.example .env"
        return $false
    }

    Get-Content $envFile | Where-Object { $_ -match '^\s*[^#]' } | ForEach-Object {
        if ($_ -match '(.+?)=(.*)') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($value) {
                [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }

    return $true
}

function Check-Prerequisites {
    $required = @("DAYTONA_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY")
    $optional = @("GITHUB_TOKEN")

    $missing = @()
    $present = @()

    foreach ($key in $required) {
        $value = [System.Environment]::GetEnvironmentVariable($key, "Process")
        if ([string]::IsNullOrWhiteSpace($value)) {
            $missing += $key
        } else {
            $present += $key
        }
    }

    Write-Host "`n=== Phase 0 Prerequisites Status ===" -ForegroundColor Cyan
    Write-Host "`n✅ Keys Present:" -ForegroundColor Green
    if ($present.Count -eq 0) {
        Write-Host "  (none yet)"
    } else {
        foreach ($key in $present) {
            $value = [System.Environment]::GetEnvironmentVariable($key, "Process")
            $masked = if ($value.Length -gt 10) { $value.Substring(0, 10) + "..." } else { $value }
            Write-Host "  • $key = $masked"
        }
    }

    Write-Host "`n❌ Missing Keys ($($missing.Count) of $($required.Count)):" -ForegroundColor Yellow
    foreach ($key in $missing) {
        Write-Host "  • $key"
    }

    # Check optional
    $optionalPresent = @()
    foreach ($key in $optional) {
        $value = [System.Environment]::GetEnvironmentVariable($key, "Process")
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            $optionalPresent += $key
        }
    }

    if ($optionalPresent.Count -gt 0) {
        Write-Host "`n📋 Optional Keys Present:" -ForegroundColor Blue
        foreach ($key in $optionalPresent) {
            Write-Host "  • $key"
        }
    }

    Write-Host "`n" -ForegroundColor Cyan

    if ($missing.Count -eq 0) {
        Write-Host "✨ All required keys configured! Ready for Phase 1.3 (TrueForge setup)" -ForegroundColor Green
        return $true
    } else {
        Write-Host "⏳ Still need $($missing.Count) key(s). Update .env file and run this script again." -ForegroundColor Yellow
        return $false
    }
}

# Main
if (Load-EnvFile) {
    Check-Prerequisites
} else {
    exit 1
}
