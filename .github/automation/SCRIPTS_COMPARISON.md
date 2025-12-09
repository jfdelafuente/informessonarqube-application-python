# Scripts Comparison

## create_issues.sh vs create_issues_no_milestones.sh

### create_issues.sh (Original - 930 lines)

**Features:**
- Creates 14 GitHub issues using `gh` CLI
- Assigns each issue to a milestone
- Full-featured version

**Milestones assigned:**
- Fase 0: Preparación
- Fase 1: Quick Wins (4 issues)
- Fase 2: Concurrencia (2 issues)
- Fase 3: Mantenibilidad (3 issues)
- Fase 4: Claridad (3 issues)

**Usage:**
```bash
cd .github/automation
bash create_issues.sh
```

**Requirements:**
- GitHub CLI (`gh`) installed and authenticated
- Milestones must exist in repository (run `python setup_github_milestones.py` first)

**Example command:**
```bash
gh issue create --repo "$REPO" \
  --title "[Performance] Vectorizar operaciones Pandas" \
  --label "enhancement,performance,phase-1,quick-win" \
  --milestone "Fase 1: Quick Wins" \
  --body "..."
```

---

### create_issues_no_milestones.sh (Simplified - 917 lines)

**Features:**
- Creates 14 GitHub issues using `gh` CLI
- **Does NOT assign milestones** (13 lines removed)
- Works even if milestones don't exist

**Usage:**
```bash
cd .github/automation
bash create_issues_no_milestones.sh
```

**Requirements:**
- GitHub CLI (`gh`) installed and authenticated
- No milestone setup needed

**Example command:**
```bash
gh issue create --repo "$REPO" \
  --title "[Performance] Vectorizar operaciones Pandas" \
  --label "enhancement,performance,phase-1,quick-win" \
  --body "..."
# Note: No --milestone flag
```

---

## Key Differences

| Feature | create_issues.sh | create_issues_no_milestones.sh |
|---------|------------------|--------------------------------|
| **Lines of code** | 930 | 917 |
| **Milestone assignment** | Yes (13 issues) | No |
| **Requires milestones** | Yes | No |
| **Setup script needed** | setup_github_milestones.py | None |
| **Use case** | Full project setup | Quick issue creation |

---

## Why Two Versions?

**Problem:** When you first reported the error:
```
could not add to milestone 'Fase 1: Quick Wins': 'Fase 1: Quick Wins' not found
```

**Solution:** Created `create_issues_no_milestones.sh` to allow issue creation without requiring milestones to exist first.

---

## Recommended Workflow

### Option 1: Full Setup (Recommended)

```bash
cd .github/automation

# Step 1: Create milestones first
python setup_github_milestones.py

# Step 2: Create issues with milestone assignment
bash create_issues.sh
```

**Result:** Issues created AND organized into milestones

---

### Option 2: Quick Setup (No Milestones)

```bash
cd .github/automation

# Create issues without milestones
bash create_issues_no_milestones.sh
```

**Result:** Issues created, can assign milestones manually later in GitHub UI

---

### Option 3: Python Version (Best for portability)

```bash
cd .github/automation

# No gh CLI needed
python setup_github_milestones.py  # Optional
python create_issues.py
```

**Result:** Issues created, no bash or gh CLI needed

---

## Which Script Should You Use?

| Scenario | Recommended Script |
|----------|-------------------|
| **Windows without gh CLI** | `create_issues.py` (Python) |
| **Have gh CLI + want milestones** | `create_issues.sh` |
| **Have gh CLI + no milestones** | `create_issues_no_milestones.sh` |
| **Linux/Mac + full setup** | `create_issues.sh` |
| **CI/CD automation** | `create_issues.py` (most portable) |

---

**Bottom line:** The `_no_milestones` version is a workaround for when milestones don't exist yet. Use the full version (`create_issues.sh` or `create_issues.py`) after setting up milestones.
