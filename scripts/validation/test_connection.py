#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba de conexión rápida para SonarQube y GitLab

Uso: python test_connection.py [sonar|gitlab|all]
"""

import sys
import os
from dotenv import load_dotenv


class Colors:
    """Colores para la salida en terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")


def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}")


def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}  {text}{Colors.END}")


def print_header(text):
    """Imprime un encabezado destacado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def test_sonar_connection():
    """Prueba la conexión con SonarQube"""
    print_header("Probando conexión con SonarQube")

    try:
        from src.api.SonarAPIHandler import SonarAPIHandler

        sonar = SonarAPIHandler()
        print_info(f"Host: {sonar._host}")

        # Intentar obtener componentes (solo 1 página para probar)
        response = sonar.get_component(qualifiers="TRK", index=1)

        if response.status_code == 200:
            import json
            data = json.loads(response.text)
            total = data.get('paging', {}).get('total', 0)
            print_success("Conexión exitosa!")
            print_success(f"Total de proyectos en SonarQube: {total}")

            if total > 0:
                components = data.get('components', [])
                print_success("Primeros proyectos encontrados:")
                for comp in components[:5]:
                    print_info(f"- {comp.get('name')} ({comp.get('key')})")

            return True
        elif response.status_code == 401:
            print_error("Error de autenticación. Verifica el token de acceso.")
            return False
        else:
            print_error(f"Error: código de respuesta {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error al conectar con SonarQube: {e}")
        return False


def test_gitlab_connection():
    """Prueba la conexión con GitLab"""
    print_header("Probando conexión con GitLab")

    try:
        import gitlab

        gitlab_host = os.getenv('GITLAB_DEFAULT_HOST')
        gitlab_token = os.getenv('GITLAB_ACCESS_TOKEN')

        print_info(f"Host: {gitlab_host}")

        gl = gitlab.Gitlab(url=gitlab_host, private_token=gitlab_token)

        # Autenticar
        gl.auth()
        user = gl.user
        if user:
            print_success(f"Conectado como: {user.username} ({user.name})")
        else:
            print_success("Autenticación exitosa")

        # Obtener información de proyectos
        projects = gl.projects.list(get_all=False, per_page=10)
        total_projects = len(projects)

        print_success("Acceso a proyectos exitoso!")
        print_success(f"Proyectos accesibles (muestra): {total_projects}")

        if total_projects > 0:
            print_success("Primeros proyectos encontrados:")
            for project in projects[:5]:
                namespace = project.attributes.get('namespace', {}).get('name', 'N/A')
                print_info(f"- {project.name} ({namespace})")

        return True

    except gitlab.exceptions.GitlabAuthenticationError:
        print_error("Error de autenticación. Verifica el token de acceso.")
        return False
    except Exception as e:
        print_error(f"Error al conectar con GitLab: {e}")
        return False


def main():
    """Función principal"""
    load_dotenv()

    # Determinar qué probar
    if len(sys.argv) > 1:
        target = sys.argv[1].lower()
    else:
        target = 'all'

    print(f"\n{Colors.BOLD}Script de Prueba de Conexión - ETL SonarQube & GitLab{Colors.END}")
    print(f"{Colors.BLUE}Este script verificará la conectividad con las APIs{Colors.END}\n")

    results = {}

    if target in ['sonar', 'all']:
        results['SonarQube'] = test_sonar_connection()

    if target in ['gitlab', 'all']:
        results['GitLab'] = test_gitlab_connection()

    # Resumen
    print_header("RESUMEN")

    for service, success in results.items():
        if success:
            print(f"{Colors.GREEN}[OK] {service}: CONECTADO{Colors.END}")
        else:
            print(f"{Colors.RED}[ERROR] {service}: FALLÓ{Colors.END}")

    all_success = all(results.values())

    print()  # Línea en blanco

    if all_success:
        print(f"{Colors.GREEN}{Colors.BOLD}[OK] Todas las conexiones exitosas!{Colors.END}\n")
        print(f"{Colors.CYAN}Puedes proceder a ejecutar los scripts ETL:{Colors.END}")
        print_info("python src/main_etl_sonar.py")
        print_info("python src/main_etl_gitlab.py")
    else:
        print(f"{Colors.RED}{Colors.BOLD}[ERROR] Algunas conexiones fallaron.{Colors.END}")
        print(f"{Colors.YELLOW}Verifica la configuración en .env{Colors.END}\n")

    sys.exit(0 if all_success else 1)


if __name__ == '__main__':
    main()
