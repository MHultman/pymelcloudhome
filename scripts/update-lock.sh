#!/bin/bash
# update-lock.sh - Script to update poetry lock file

echo "🔒 Checking poetry lock file status..."

# Check if poetry.lock is up to date
if poetry check --lock > /dev/null 2>&1; then
    echo "✅ poetry.lock is already up to date!"
    exit 0
else
    echo "⚠️  poetry.lock is out of sync with pyproject.toml"
    echo "🔄 Updating poetry.lock..."

    # Update the lock file
    if poetry lock; then
        echo "✅ poetry.lock updated successfully!"

        # Run tests to make sure everything still works
        echo "🧪 Running tests to verify changes..."
        if poetry run pytest --tb=short -q; then
            echo "✅ All tests pass!"
            echo ""
            echo "📝 Don't forget to commit the updated poetry.lock file:"
            echo "   git add poetry.lock"
            echo "   git commit -m 'Update poetry.lock'"
        else
            echo "❌ Tests failed after lock file update"
            exit 1
        fi
    else
        echo "❌ Failed to update poetry.lock"
        exit 1
    fi
fi
