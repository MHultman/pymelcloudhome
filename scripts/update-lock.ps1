# update-lock.ps1 - PowerShell script to update poetry lock file

Write-Host "Checking poetry lock file status..." -ForegroundColor Cyan

# Check if poetry.lock is up to date
try {
    poetry lock --check *>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "poetry.lock is already up to date!" -ForegroundColor Green
        exit 0
    }
} catch {
    # Continue to update section
}

Write-Host "poetry.lock is out of sync with pyproject.toml" -ForegroundColor Yellow
Write-Host "Updating poetry.lock..." -ForegroundColor Cyan

# Update the lock file
try {
    poetry lock
    if ($LASTEXITCODE -eq 0) {
        Write-Host "poetry.lock updated successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Don't forget to commit the updated poetry.lock file:" -ForegroundColor Yellow
        Write-Host "   git add poetry.lock" -ForegroundColor White
        Write-Host "   git commit -m 'Update poetry.lock'" -ForegroundColor White
    } else {
        Write-Host "Failed to update poetry.lock" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Failed to update poetry.lock" -ForegroundColor Red
    exit 1
}
