#!/bin/bash
set -e

# Ask for migration message
read -p "Enter migration message: " migration_message

# Validate message is not empty
if [ -z "$migration_message" ]; then
    echo "❌ Migration message cannot be empty"
    exit 1
fi

echo "🔄 Generating migration: $migration_message"

# Create a new migration file
alembic revision --autogenerate -m "$migration_message"

# Get the latest migration file
latest_migration=$(ls -t alembic/versions/*.py | head -n 1)

echo "📄 Checking migration file: $(basename "$latest_migration")"

# Check if the migration has actual operations (not just pass statements)
has_operations=false

# Check upgrade function
if grep -A 20 "def upgrade():" "$latest_migration" | grep -v "def upgrade():" | grep -v "pass" | grep -v "^$" | grep -v "^\s*#" | grep -q "."; then
    has_operations=true
fi

# Check downgrade function if upgrade is empty
if [ "$has_operations" = false ]; then
    if grep -A 20 "def downgrade():" "$latest_migration" | grep -v "def downgrade():" | grep -v "pass" | grep -v "^$" | grep -v "^\s*#" | grep -q "."; then
        has_operations=true
    fi
fi

if [ "$has_operations" = true ]; then
    echo "✅ Migration created successfully. Run './migrate.sh' to apply the migration."
else
    echo "❌ Nothing to migrate. Deleting empty migration file."
    rm "$latest_migration"
fi