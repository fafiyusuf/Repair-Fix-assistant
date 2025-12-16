#!/bin/bash
set -e

echo "Starting IFix-AI Backend..."

# Wait for dependencies if needed (example for database)
# if [ -n "$DATABASE_URL" ]; then
#     echo "Waiting for database..."
#     while ! nc -z database_host 5432; do
#         sleep 1
#     done
#     echo "Database is ready!"
# fi

# Run any pre-startup scripts (migrations, etc.)
# if [ "$RUN_MIGRATIONS" = "true" ]; then
#     echo "Running database migrations..."
#     python scripts/apply_schema.py
# fi

# Check if all required environment variables are set
required_vars=(
    "SUPABASE_URL"
    "SUPABASE_SERVICE_ROLE_KEY"
    "GEMINI_API_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

echo "Environment variables validated successfully"
echo "Starting application..."

# Execute the main command
exec "$@"
