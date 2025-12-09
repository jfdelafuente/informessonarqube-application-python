# GitHub Automation Scripts

Automate GitHub project setup for the performance optimization plan.

---

## Quick Start

```bash
# From project root
cd .github/automation

# Step 1: Create labels
python setup_github_labels.py

# Step 2: Create milestones
python setup_github_milestones.py

# Step 3: Create issues
python create_issues.py
```

---

## Requirements

```bash
pip install requests
```

**GitHub Token:** Create at https://github.com/settings/tokens/new with `repo` scope

---

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| `setup_github_labels.py` | Creates 11 labels | bug, performance, phases, etc. |
| `setup_github_milestones.py` | Creates 6 milestones | Fase 0-5 with due dates |
| `create_issues.py` | Creates 5 issues | Critical bug + 4 quick wins |
| `setup_github_labels.sh` | Labels (bash version) | Requires gh CLI |
| `create_issues.sh` | Issues (bash, full) | Requires gh CLI |
| `create_issues_no_milestones.sh` | Issues (bash, no milestones) | Requires gh CLI |

**Recommended:** Use Python versions (`.py`) - no gh CLI needed.

---

## Environment Setup

**Option 1: Environment Variable**
```bash
export GITHUB_TOKEN="your_token_here"
```

**Option 2: Interactive Prompt**
```bash
python setup_github_labels.py
# Script will prompt for token
```

---

## Documentation

For complete documentation, see: [docs/GITHUB_AUTOMATION.md](../../docs/GITHUB_AUTOMATION.md)

Topics covered:
- Prerequisites and installation
- Detailed script documentation
- Troubleshooting guide
- Security best practices
- Advanced usage

---

## File Structure

```
.github/automation/
├── README.md                          # This file
├── setup_github_labels.py             # Create labels (Python)
├── setup_github_labels.sh             # Create labels (Bash)
├── setup_github_milestones.py         # Create milestones (Python)
├── create_issues.py                   # Create issues (Python)
├── create_issues.sh                   # Create issues (Bash, full)
└── create_issues_no_milestones.sh     # Create issues (Bash, no milestones)
```

---

**For detailed usage:** See [docs/GITHUB_AUTOMATION.md](../../docs/GITHUB_AUTOMATION.md)
