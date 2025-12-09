# GitHub Automation Scripts

**Project:** informessonarqube-application-python
**Purpose:** Automate GitHub project setup for performance optimization plan

---

## Overview

This directory contains Python scripts to automate the creation of GitHub labels, milestones, and issues for the performance optimization project. All scripts use the GitHub REST API and don't require the `gh` CLI tool.

---

## Prerequisites

### 1. Install Requirements

```bash
pip install requests
```

### 2. Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens/new
2. Select scopes:
   - `repo` (Full control of private repositories)
3. Click "Generate token"
4. **Copy the token** (you won't see it again!)

### 3. Set Environment Variable (Optional)

**Linux/Mac:**
```bash
export GITHUB_TOKEN="your_token_here"
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

**Windows (CMD):**
```cmd
set GITHUB_TOKEN=your_token_here
```

If you don't set the environment variable, the scripts will prompt you to enter the token when running.

---

## Scripts

### 1. setup_github_labels.py

Creates labels for categorizing issues.

**Creates 11 labels:**
- `bug` - Something isn't working
- `priority:critical` - Critical priority
- `quick-win` - High impact, low effort
- `performance` - Performance optimization
- `phase-1` through `phase-4` - Phase tracking
- `refactoring` - Code refactoring
- `documentation` - Documentation improvements
- `phase-0` - Preparation phase

**Usage:**
```bash
python setup_github_labels.py
```

**Output:**
```
======================================================================
Setting up GitHub Labels for Performance Optimization Plan
======================================================================

Detecting repository...
Repository: jfdelafuente/informessonarqube-application-python
[OK] Repository access confirmed

Creating 11 labels...

[CREATED] bug
[CREATED] priority:critical
[CREATED] quick-win
...
```

---

### 2. setup_github_milestones.py

Creates milestones for tracking project phases.

**Creates 6 milestones:**

| Milestone | Status | Due Date | Description |
|-----------|--------|----------|-------------|
| Fase 0: Preparación | Closed | - | Already completed |
| Fase 1: Quick Wins | Open | 2 weeks | 30-40% improvement |
| Fase 2: Concurrencia | Open | 4 weeks | 50-70% total improvement |
| Fase 3: Mantenibilidad | Open | 6 weeks | Code maintainability |
| Fase 4: Claridad | Open | 8 weeks | Documentation & clarity |
| Fase 5: Avanzadas | Open | No deadline | Optional advanced optimizations |

**Usage:**
```bash
python setup_github_milestones.py
```

**Output:**
```
======================================================================
Setting up GitHub Milestones for Performance Optimization Plan
======================================================================

Detecting repository...
Repository: jfdelafuente/informessonarqube-application-python
[OK] Repository access confirmed

Creating 6 milestones...

[CREATED] Fase 0: Preparación
  [CLOSED] Fase 0: Preparación (already completed)
[CREATED] Fase 1: Quick Wins
...
```

---

### 3. create_issues.py

Creates GitHub issues for the optimization tasks.

**Creates 5 critical issues:**

1. **[BUG CRÍTICO]** Año hardcodeado en GitLab transform
   - Labels: `bug`, `priority:critical`, `quick-win`
   - Impact: Filters all data since 2024
   - Effort: 5 minutes

2. **[P2]** Vectorizar iterrows() en extract.py
   - Labels: `performance`, `phase-1`, `quick-win`
   - Impact: 20% improvement
   - Effort: 2 days

3. **[P5]** Reducir logging en bucles
   - Labels: `performance`, `phase-1`, `quick-win`
   - Impact: 10% improvement
   - Effort: 1 day

4. **[P3]** Implementar caché de proyectos
   - Labels: `performance`, `phase-1`
   - Impact: 50% improvement in re-runs
   - Effort: 1 day

5. **Optimizar construcción de DataFrames**
   - Labels: `performance`, `phase-1`
   - Impact: 15% improvement
   - Effort: 1 day

**Usage:**
```bash
python create_issues.py
```

**Output:**
```
======================================================================
Creating GitHub Issues for Performance Optimization Plan
======================================================================

Detecting repository...
Repository: jfdelafuente/informessonarqube-application-python
[OK] Repository access confirmed

Creating 5 issues...

[1/5] [BUG CRÍTICO] Año hardcodeado en GitLab transform...
  [OK] Created: https://github.com/jfdelafuente/informessonarqube-application-python/issues/1
...
```

---

## Complete Setup Workflow

Run scripts in this order:

```bash
# Step 1: Create labels
python setup_github_labels.py

# Step 2: Create milestones
python setup_github_milestones.py

# Step 3: Create issues
python create_issues.py
```

**Expected total time:** 2-3 minutes

---

## Troubleshooting

### Error: "GITHUB_TOKEN not found"

**Solution:** Set the environment variable or enter token when prompted.

```bash
# Option 1: Set environment variable
export GITHUB_TOKEN="your_token_here"
python setup_github_labels.py

# Option 2: Let script prompt you
python setup_github_labels.py
# Then enter token when asked
```

### Error: "Could not access repository"

**Possible causes:**
1. Token doesn't have `repo` scope
2. Repository name is incorrect
3. You don't have access to the repository

**Solution:**
- Verify token has `repo` scope
- Check repository exists: https://github.com/jfdelafuente/informessonarqube-application-python
- Ensure you have write access to the repository

### Error: "Label already exists" / "Milestone already exists"

**This is normal!** Scripts skip existing items automatically.

```
[SKIP] bug (already exists)
[SKIP] performance (already exists)
```

### Error: "Could not parse repository from remote URL"

**Solution:** The script will prompt you to enter owner and repo manually:

```
Repository owner: jfdelafuente
Repository name: informessonarqube-application-python
```

---

## Advanced Usage

### Using a Different Repository

Scripts auto-detect the repository from `git remote origin`. To use a different repository:

**Option 1:** Change git remote temporarily
```bash
git remote set-url origin https://github.com/other-user/other-repo.git
python setup_github_labels.py
git remote set-url origin https://github.com/jfdelafuente/informessonarqube-application-python.git
```

**Option 2:** Enter manually when prompted
```bash
python setup_github_labels.py
# When detection fails, script will prompt:
Repository owner: other-user
Repository name: other-repo
```

### Re-running Scripts Safely

All scripts check for existing items and skip them:

```bash
# Safe to run multiple times
python setup_github_labels.py
# Output: [SKIP] bug (already exists)

python setup_github_milestones.py
# Output: [SKIP] Fase 1: Quick Wins (already exists)
```

### Creating Additional Issues

To create more issues, edit `create_issues.py` and add to the `ISSUES` list:

```python
ISSUES = [
    # ... existing issues ...
    {
        "title": "New issue title",
        "labels": ["performance", "phase-2"],
        "body": """## Description

Your issue description here
"""
    }
]
```

---

## Alternative: Using GitHub CLI

If you have `gh` CLI installed and authenticated:

```bash
# Create labels (bash version)
bash setup_github_labels.sh

# Create issues (bash version, without milestones)
bash create_issues_no_milestones.sh
```

**Note:** The bash versions require `gh` CLI. The Python versions are recommended for better portability.

---

## File Reference

| File | Purpose | Requires gh CLI |
|------|---------|----------------|
| `setup_github_labels.py` | Create labels (Python) | No ✅ |
| `setup_github_labels.sh` | Create labels (Bash) | Yes |
| `setup_github_milestones.py` | Create milestones (Python) | No ✅ |
| `create_issues.py` | Create issues (Python) | No ✅ |
| `create_issues.sh` | Create issues (Bash, with milestones) | Yes |
| `create_issues_no_milestones.sh` | Create issues (Bash, no milestones) | Yes |

**Recommended:** Use Python versions (`.py` files) for cross-platform compatibility.

---

## Security Notes

### GitHub Token Security

- **Never commit** your GitHub token to git
- **Don't share** your token publicly
- **Revoke** token if accidentally exposed: https://github.com/settings/tokens
- **Use minimal scopes** - only `repo` scope is needed

### Token Storage

**Good practices:**
```bash
# Store in environment variable (session only)
export GITHUB_TOKEN="token"

# Or use git config (stored locally)
git config --local github.token "token"
```

**Bad practices:**
```bash
# DON'T hardcode in scripts
token = "ghp_abc123..."  # NEVER DO THIS

# DON'T add to .env and commit
echo "GITHUB_TOKEN=ghp_abc123" >> .env
git add .env  # DANGEROUS
```

---

## Next Steps

After running all setup scripts:

1. **View your issues:** https://github.com/jfdelafuente/informessonarqube-application-python/issues
2. **View milestones:** https://github.com/jfdelafuente/informessonarqube-application-python/milestones
3. **Start Fase 1:** Begin implementing quick wins
4. **Track progress:** Update issue status as you complete tasks

---

## Support

For issues with these scripts:
- Check [Troubleshooting](#troubleshooting) section
- Review script output for error messages
- Verify GitHub token has correct permissions
- Ensure repository exists and you have write access

For questions about the performance optimization plan:
- See [docs/PLAN_MEJORAS.md](PLAN_MEJORAS.md)
- See [docs/OPTIMIZACION_RENDIMIENTO.md](OPTIMIZACION_RENDIMIENTO.md)
- See [docs/HALLAZGOS_TECNICOS.md](HALLAZGOS_TECNICOS.md)

---

**Last updated:** 2025-12-09
**Branch:** feature/performance-optimization-phase-0
