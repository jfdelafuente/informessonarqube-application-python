"""
Setup GitHub milestones using GitHub REST API
Creates milestones for the performance optimization plan phases

Usage:
    python setup_github_milestones.py

Requirements:
    pip install requests

    Set GITHUB_TOKEN environment variable with your personal access token
"""

import os
import sys
import requests
from getpass import getpass
from datetime import datetime, timedelta


# Milestone definitions
MILESTONES = [
    {
        "title": "Fase 0: Preparación",
        "description": """Establecer baseline y tests de regresión antes de optimizaciones.

**Tareas:**
- Benchmarking inicial
- Tests de regresión
- Generación de fixtures
- Documentación de proceso

**Objetivo:** Infraestructura lista para medir mejoras""",
        "due_on": None,  # Already completed
        "state": "closed"
    },
    {
        "title": "Fase 1: Quick Wins",
        "description": """Optimizaciones de bajo riesgo con alto impacto.

**Mejora esperada:** 30-40%
**Riesgo:** Bajo

**Incluye:**
- Vectorización de operaciones Pandas (20% mejora)
- Caché de proyectos (50% mejora en dev)
- Fix bug año hardcodeado (crítico)
- Reducción de logging en loops (10% mejora)
- Optimización construcción DataFrames (15% mejora)

**Objetivo:** Ganancias rápidas con mínimo riesgo""",
        "due_on": (datetime.now() + timedelta(days=14)).isoformat(),  # 2 weeks
        "state": "open"
    },
    {
        "title": "Fase 2: Concurrencia",
        "description": """Concurrencia y paralelización para máximo rendimiento.

**Mejora esperada:** 50-70% total (acumulativo con Fase 1)
**Riesgo:** Medio

**Incluye:**
- Llamadas API concurrentes con ThreadPoolExecutor (60-80% mejora)
- Procesamiento paralelo de históricos con multiprocessing (50-70% mejora)
- Rate limiting inteligente
- Manejo de errores en contextos paralelos

**Objetivo:** Aprovechar múltiples cores y I/O concurrente""",
        "due_on": (datetime.now() + timedelta(days=28)).isoformat(),  # 4 weeks
        "state": "open"
    },
    {
        "title": "Fase 3: Mantenibilidad",
        "description": """Refactorización para mejorar mantenibilidad del código.

**Impacto:** Mejora significativa en mantenibilidad
**Riesgo:** Medio-Alto

**Incluye:**
- Extracción de lógica común (eliminar duplicación)
- Separación de responsabilidades (SOLID)
- Configuración centralizada
- Modularización de funciones largas

**Objetivo:** Código más limpio, testeable y mantenible""",
        "due_on": (datetime.now() + timedelta(days=42)).isoformat(),  # 6 weeks
        "state": "open"
    },
    {
        "title": "Fase 4: Claridad",
        "description": """Mejoras de claridad y documentación.

**Impacto:** Mejora significativa en claridad
**Riesgo:** Bajo

**Incluye:**
- Type hints completos (100% funciones públicas)
- Nombres descriptivos (sin i, j, t)
- Constantes nombradas (eliminar magic numbers)
- Documentación consistente (docstrings Google/NumPy)

**Objetivo:** Código auto-documentado y fácil de entender""",
        "due_on": (datetime.now() + timedelta(days=56)).isoformat(),  # 8 weeks
        "state": "open"
    },
    {
        "title": "Fase 5: Optimizaciones Avanzadas (Opcional)",
        "description": """Optimizaciones avanzadas opcionales para casos específicos.

**Mejora esperada:** 20-30% adicional
**Riesgo:** Alto

**Incluye:**
- Sistema de caché distribuido (Redis)
- Streaming processing para grandes volúmenes
- Compresión de datos
- Query optimization avanzado

**Objetivo:** Optimizaciones avanzadas solo si necesarias

**Nota:** Solo implementar si los objetivos de rendimiento no se alcanzan con Fases 1-2""",
        "due_on": None,  # Optional, no deadline
        "state": "open"
    }
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
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )

        remote_url = result.stdout.strip()

        if 'github.com' in remote_url:
            if remote_url.startswith('https://'):
                parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
            else:
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


def create_milestone(token, owner, repo, milestone_data):
    """Create a milestone in GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/milestones"

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.post(url, json=milestone_data, headers=headers)

    if response.status_code == 201:
        return True, "Created"
    elif response.status_code == 422:
        # Check if milestone already exists
        error_message = response.json().get('errors', [{}])[0].get('message', '')
        if 'already exists' in error_message.lower():
            return False, "Already exists"
        return False, f"Validation error: {error_message}"
    else:
        return False, f"Error {response.status_code}: {response.text}"


def close_milestone(token, owner, repo, milestone_number):
    """Close a milestone"""
    url = f"https://api.github.com/repos/{owner}/{repo}/milestones/{milestone_number}"

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    data = {"state": "closed"}
    response = requests.patch(url, json=data, headers=headers)

    return response.status_code == 200


def get_existing_milestones(token, owner, repo):
    """Get list of existing milestones"""
    url = f"https://api.github.com/repos/{owner}/{repo}/milestones"

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get both open and closed milestones
    params = {'state': 'all'}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return {m['title']: m for m in response.json()}
    return {}


def main():
    print("=" * 70)
    print("Setting up GitHub Milestones for Performance Optimization Plan")
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
        print("\nPlease check:")
        print("  1. Token has 'repo' scope")
        print("  2. Repository name is correct")
        print("  3. You have access to the repository")
        sys.exit(1)

    print(f"[OK] Repository access confirmed")

    # Get existing milestones
    print("\nChecking existing milestones...")
    existing_milestones = get_existing_milestones(token, owner, repo)
    print(f"Found {len(existing_milestones)} existing milestone(s)")

    # Create milestones
    print(f"\nCreating {len(MILESTONES)} milestones...\n")

    created = 0
    skipped = 0
    errors = 0
    closed_count = 0

    for milestone_data in MILESTONES:
        title = milestone_data['title']

        if title in existing_milestones:
            print(f"[SKIP] {title} (already exists)")
            skipped += 1
            continue

        # Prepare data for API (remove state field, handle separately)
        api_data = {
            'title': milestone_data['title'],
            'description': milestone_data['description']
        }

        if milestone_data['due_on']:
            api_data['due_on'] = milestone_data['due_on']

        success, message = create_milestone(token, owner, repo, api_data)

        if success:
            print(f"[CREATED] {title}")
            created += 1

            # Close milestone if needed (Fase 0)
            if milestone_data['state'] == 'closed':
                # Get milestone number from newly created
                milestones = get_existing_milestones(token, owner, repo)
                if title in milestones:
                    milestone_number = milestones[title]['number']
                    if close_milestone(token, owner, repo, milestone_number):
                        print(f"  [CLOSED] {title} (already completed)")
                        closed_count += 1

        elif "Already exists" in message:
            print(f"[SKIP] {title} (already exists)")
            skipped += 1
        else:
            print(f"[ERROR] {title} - {message}")
            errors += 1

    # Summary
    print("\n" + "=" * 70)
    print("GitHub Milestones Setup Complete")
    print("=" * 70)
    print(f"\nResults:")
    print(f"  Created: {created}")
    print(f"  Closed: {closed_count}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")

    print("\nMilestones created:")
    print("  - Fase 0: Preparacion (closed - already done)")
    print("  - Fase 1: Quick Wins (2 weeks)")
    print("  - Fase 2: Concurrencia (4 weeks)")
    print("  - Fase 3: Mantenibilidad (6 weeks)")
    print("  - Fase 4: Claridad (8 weeks)")
    print("  - Fase 5: Optimizaciones Avanzadas (optional, no deadline)")

    if errors == 0:
        print("\n[OK] Next step: Run create_issues.sh or create_issues.py")
        print("      Issues can now be assigned to these milestones")
    else:
        print("\n[WARNING] Some milestones failed. Please check errors above.")

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
