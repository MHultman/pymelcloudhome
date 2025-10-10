@echo off
REM update-lock.bat - Windows batch script to update poetry lock file

echo 🔒 Checking poetry lock file status...

REM Check if poetry.lock is up to date
poetry lock --check >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ poetry.lock is already up to date!
    exit /b 0
) else (
    echo ⚠️  poetry.lock is out of sync with pyproject.toml
    echo 🔄 Updating poetry.lock...

    REM Update the lock file
    poetry lock
    if %ERRORLEVEL% EQU 0 (
        echo ✅ poetry.lock updated successfully!

        REM Run tests to make sure everything still works
        echo 🧪 Running tests to verify changes...
        poetry run pytest --tb=short -q
        if %ERRORLEVEL% EQU 0 (
            echo ✅ All tests pass!
            echo.
            echo 📝 Don't forget to commit the updated poetry.lock file:
            echo    git add poetry.lock
            echo    git commit -m "Update poetry.lock"
        ) else (
            echo ❌ Tests failed after lock file update
            exit /b 1
        )
    ) else (
        echo ❌ Failed to update poetry.lock
        exit /b 1
    )
)
