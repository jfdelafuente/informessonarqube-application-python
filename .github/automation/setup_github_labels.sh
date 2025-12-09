#!/bin/bash

# Script to create GitHub labels for the improvement plan issues
# Run this BEFORE create_issues.sh

set -e

echo "======================================================================"
echo "🏷️  Setting up GitHub Labels for Performance Optimization Plan"
echo "======================================================================"
echo ""

# Get repository from git remote
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)

if [ -z "$REPO" ]; then
    echo "❌ Error: Could not determine repository."
    echo "Please run this script from inside the repository directory."
    exit 1
fi

echo "Repository: $REPO"
echo ""

# Function to create label if it doesn't exist
create_label() {
    local name="$1"
    local color="$2"
    local description="$3"

    # Check if label exists
    if gh label list --repo "$REPO" | grep -q "^$name"; then
        echo "⏭️  Label '$name' already exists, skipping"
    else
        gh label create "$name" \
            --repo "$REPO" \
            --color "$color" \
            --description "$description"
        echo "✅ Created label: $name"
    fi
}

echo "Creating labels..."
echo ""

# Bug labels
create_label "bug" "d73a4a" "Something isn't working"
create_label "priority:critical" "b60205" "Critical priority - must fix immediately"
create_label "quick-win" "0e8a16" "Quick win - high impact, low effort"

# Performance labels
create_label "performance" "fbca04" "Performance optimization"
create_label "phase-1" "d4c5f9" "Phase 1: Low-risk optimizations"
create_label "phase-2" "c5def5" "Phase 2: Concurrency and parallelization"

# Refactoring labels
create_label "refactoring" "5319e7" "Code refactoring and cleanup"
create_label "phase-3" "bfdadc" "Phase 3: Refactoring for maintainability"

# Documentation labels
create_label "documentation" "0075ca" "Improvements or additions to documentation"
create_label "phase-4" "e99695" "Phase 4: Clarity and documentation"

# Setup label
create_label "phase-0" "f9d0c4" "Phase 0: Preparation and foundations"

echo ""
echo "======================================================================"
echo "✅ GitHub Labels Setup Complete"
echo "======================================================================"
echo ""
echo "Labels created for:"
echo "  - Bugs and priorities"
echo "  - Performance optimizations"
echo "  - Refactoring tasks"
echo "  - Documentation improvements"
echo "  - Phase tracking (0-4)"
echo ""
echo "Next step: Run create_issues.sh to create all issues"
echo "======================================================================"
