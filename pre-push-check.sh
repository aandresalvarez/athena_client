#!/bin/bash

# Pre-push check script to catch errors before GitHub CI
# This script runs the same checks that GitHub Actions will run

set -e  # Exit on any error

echo "🔍 Running pre-push checks..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Check if hatch is installed
if ! command -v hatch &> /dev/null; then
    echo "❌ Hatch is not installed. Install with: pip install hatch"
    exit 1
fi

echo "📦 Installing dependencies..."
hatch env create

echo "🔧 Installing optional dependencies for testing..."
hatch run pip install -e ".[pandas,db]"

echo "🧪 Running tests with coverage..."
if ! hatch run cov; then
    echo "❌ Tests failed!"
    exit 1
fi

echo "🔒 Running security checks..."
if ! hatch run bandit-check; then
    echo "❌ Security checks failed!"
    exit 1
fi

echo "🎨 Checking code formatting..."
if ! hatch run ruff format --check athena_client tests; then
    echo "❌ Code formatting issues found. Run 'hatch run ruff format athena_client tests' to fix."
    exit 1
fi

echo "📏 Running linter..."
if ! hatch run lint; then
    echo "❌ Linting issues found!"
    exit 1
fi

echo "🔍 Running type checks..."
if ! hatch run type-check; then
    echo "❌ Type checking failed!"
    exit 1
fi

echo "✅ All pre-push checks passed!"
echo "🚀 Ready to push to GitHub!"