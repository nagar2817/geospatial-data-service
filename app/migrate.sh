#!/bin/bash
set -e

echo "🚀 Applying migrations..."

# Apply migrations
alembic upgrade head

echo "✅ Migrations applied successfully!"