#!/bin/bash
# SentinelOps Environment Setup Script (Bash version)
# This script loads .env variables and validates Phase 0 prerequisites

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$ROOT_DIR/.env"

function load_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        echo "❌ .env file not found at $ENV_FILE"
        echo "   Create it from .env.example:"
        echo "   cp .env.example .env"
        return 1
    fi

    # Load .env file
    set -a
    source "$ENV_FILE"
    set +a
    return 0
}

function check_prerequisites() {
    local required=("DAYTONA_API_KEY" "GOOGLE_API_KEY" "GROQ_API_KEY")
    local optional=("GITHUB_TOKEN")

    local missing=()
    local present=()

    echo ""
    echo "=== Phase 0 Prerequisites Status ==="
    echo ""

    # Check required keys
    for key in "${required[@]}"; do
        value="${!key}"
        if [ -z "$value" ]; then
            missing+=("$key")
        else
            present+=("$key")
        fi
    done

    # Display present keys
    echo "✅ Keys Present:"
    if [ ${#present[@]} -eq 0 ]; then
        echo "  (none yet)"
    else
        for key in "${present[@]}"; do
            value="${!key}"
            masked="${value:0:10}..."
            echo "  • $key = $masked"
        done
    fi

    # Display missing keys
    echo ""
    echo "❌ Missing Keys (${#missing[@]} of ${#required[@]}):"
    for key in "${missing[@]}"; do
        echo "  • $key"
    done

    # Check optional
    local optional_present=()
    for key in "${optional[@]}"; do
        value="${!key}"
        if [ -n "$value" ]; then
            optional_present+=("$key")
        fi
    done

    if [ ${#optional_present[@]} -gt 0 ]; then
        echo ""
        echo "📋 Optional Keys Present:"
        for key in "${optional_present[@]}"; do
            echo "  • $key"
        done
    fi

    echo ""

    if [ ${#missing[@]} -eq 0 ]; then
        echo "✨ All required keys configured! Ready for Phase 1.3 (TrueForge setup)"
        return 0
    else
        echo "⏳ Still need ${#missing[@]} key(s). Update .env file and run this script again."
        return 1
    fi
}

# Main
if load_env_file; then
    check_prerequisites
else
    exit 1
fi
