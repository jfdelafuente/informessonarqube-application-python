"""
Setup GitHub labels using GitHub REST API
Alternative to setup_github_labels.sh that doesn't require gh CLI

Usage:
    python setup_github_labels.py

Requirements:
    pip install requests

    Set GITHUB_TOKEN environment variable with your personal access token
    Or provide token when prompted
"""

import os
import sys
import requests
from getpass import getpass


# Label definitions
LABELS = [
    # Bug labels
    {"name": "bug", "color": "d73a4a", "description": "Something isn't working"},
    {"name": "priority:critical", "color": "b60205", "description": "Critical priority - must fix immediately"},
    {"name": "quick-win", "color": "0e8a16", "description": "Quick win - high impact, low effort"},

    # Performance labels
    {"name": "performance", "color": "fbca04", "description": "Performance optimization"},
    {"name": "phase-1", "color": "d4c5f9", "description": "Phase 1: Low-risk optimizations"},
    {"name": "phase-2", "color": "c5def5", "description": "Phase 2: Concurrency and parallelization"},

    # Refactoring labels
    {"name": "refactoring", "color": "5319e7", "description": "Code refactoring and cleanup"},
    {"name": "phase-3", "color": "bfdadc", "description": "Phase 3: Refactoring for maintainability"},

    # Documentation labels
    {"name": "documentation", "color": "0075ca", "description": "Improvements or additions to documentation"},
    {"name": "phase-4", "color": "e99695", "description": "Phase 4: Clarity and documentation"},

    # Setup label
    {"name": "phase-0", "color": "f9d0c4", "description": "Phase 0: Preparation and foundations"},
]


def get_github_token():
    """Get GitHub token from environment or prompt user"""
    token = os.environ.get('GITHUB_TOKEN')

    if not token:
        print("\n[WARNING] GITHUB_TOKEN not found in environment variables")
        print("\nYou need a GitHub Personal Access Token with 'repo' scope.")
        print("Create one at: https://github.com/settings/tokens/new")
        print("")
        token = getpass("Enter your GitHub token: ")

    return token.strip()


def get_repo_info():
    """Get repository owner and name from git remote"""
    import subprocess

    try:
        # Get remote URL
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )

        remote_url = result.stdout.strip()

        # Parse owner/repo from URL
        # Supports: https://github.com/owner/repo.git or git@github.com:owner/repo.git
        if 'github.com' in remote_url:
            if remote_url.startswith('https://'):
                # https://github.com/owner/repo.git
                parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
            else:
                # git@github.com:owner/repo.git
                parts = remote_url.split(':')[1].replace('.git', '').split('/')

            if len(parts) >= 2:
                return parts[0], parts[1]

        raise ValueError("Could not parse repository from remote URL")

    except Exception as e:
        print(f"[ERROR] Error getting repository info: {e}")
        print("\nPlease provide repository information manually:")
        owner = input("Repository owner: ").strip()
        repo = input("Repository name: ").strip()
        return owner, repo


def create_label(token, owner, repo, label_data):
    """Create a label in GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/labels"

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.post(url, json=label_data, headers=headers)

    if response.status_code == 201:
        return True, "Created"
    elif response.status_code == 422:
        # Label already exists
        return False, "Already exists"
    else:
        return False, f"Error {response.status_code}: {response.text}"


def main():
    print("=" * 70)
    print("Setting up GitHub Labels for Performance Optimization Plan")
    print("=" * 70)
    print()

    # Get token
    token = get_github_token()

    # Get repository info
    print("\nDetecting repository...")
    owner, repo = get_repo_info()
    print(f"Repository: {owner}/{repo}")

    # Verify token works
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    test_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(test_url, headers=headers)

    if response.status_code != 200:
        print(f"\n[ERROR] Could not access repository")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print("\nPlease check:")
        print("  1. Token has 'repo' scope")
        print("  2. Repository name is correct")
        print("  3. You have access to the repository")
        sys.exit(1)

    print(f"[OK] Repository access confirmed")

    # Create labels
    print(f"\nCreating {len(LABELS)} labels...\n")

    created = 0
    skipped = 0
    errors = 0

    for label_data in LABELS:
        success, message = create_label(token, owner, repo, label_data)

        if success:
            print(f"[CREATED] {label_data['name']}")
            created += 1
        elif "Already exists" in message:
            print(f"[SKIP] {label_data['name']} (already exists)")
            skipped += 1
        else:
            print(f"[ERROR] {label_data['name']} - {message}")
            errors += 1

    # Summary
    print("\n" + "=" * 70)
    print("GitHub Labels Setup Complete")
    print("=" * 70)
    print(f"\nResults:")
    print(f"  Created: {created}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")

    print("\nLabels created for:")
    print("  - Bugs and priorities")
    print("  - Performance optimizations")
    print("  - Refactoring tasks")
    print("  - Documentation improvements")
    print("  - Phase tracking (0-4)")

    if errors == 0:
        print("\n[OK] Next step: Run create_issues.sh to create all issues")
    else:
        print("\n[WARNING] Some labels failed. Please check errors above.")

    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
