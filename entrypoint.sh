#!/bin/bash
set -e

# Debug information
echo "Current directory: $(pwd)"
echo "Contents of current directory:"
ls -la
echo "PYTHONPATH: $PYTHONPATH"

# Function to export env vars from .env file
export_env_vars() {
    if [ -f .env ]; then
        export $(cat .env | sed 's/#.*//g' | xargs)
    fi
}

# Export environment variables
export_env_vars

# Execute CMD
exec "$@"