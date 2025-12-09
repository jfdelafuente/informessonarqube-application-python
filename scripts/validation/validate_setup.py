#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de validación para el proyecto ETL SonarQube & GitLab

Verifica:
- Variables de entorno requeridas
- Conectividad con SonarQube y GitLab
- Estructura de directorios
- Dependencias de Python
- Permisos de escritura

Uso: python validate_setup.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import importlib.util


class Colors:
    """Colores para la salida en terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Imprime un encabezado destacado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def check_python_version():
    """Verifica la versión de Python"""
    print_header("Verificando versión de Python")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print_info(f"Versión de Python detectada: {version_str}")

    # Verificar si está en un entorno virtual
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print_success("Ejecutando en entorno virtual (venv)")
    else:
        print_warning("No se detectó entorno virtual. Se recomienda usar 'python -m venv venv'")

    if version.major == 3 and version.minor >= 11:
        print_success(f"Python {version_str} es compatible (>= 3.11)")
        return True
    elif version.major == 3 and version.minor >= 8:
        print_warning(f"Python {version_str} puede funcionar, pero se recomienda 3.11+")
        return True
    else:
        print_error(f"Python {version_str} no es compatible. Se requiere Python 3.11+")
        return False


def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print_header("Verificando dependencias de Python")

    required_packages = {
        'pandas': 'pandas',
        'requests': 'requests',
        'gitlab': 'python-gitlab',
        'dotenv': 'python-dotenv',
        'numpy': 'numpy',
        'openpyxl': 'openpyxl'
    }

    all_installed = True

    for module_name, package_name in required_packages.items():
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            try:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', 'unknown')
                print_success(f"{package_name} instalado (versión: {version})")
            except Exception as e:
                print_warning(f"{package_name} encontrado pero no se pudo verificar: {e}")
        else:
            print_error(f"{package_name} NO instalado")
            all_installed = False

    if not all_installed:
        print_info("\nPara instalar las dependencias faltantes, ejecuta:")
        print_info("  pip install -r requirements.txt")

    return all_installed


def check_env_file():
    """Verifica la existencia y contenido del archivo .env"""
    print_header("Verificando archivo de variables de entorno (.env)")

    env_path = Path('.env')

    if not env_path.exists():
        print_error("Archivo .env no encontrado en la raíz del proyecto")
        print_info("\nCrea un archivo .env con el siguiente contenido:")
        print_info("  SONAR_DEFAULT_HOST=https://your-sonarqube-instance.com")
        print_info("  SONAR_ACCESS_TOKEN=your-sonar-token")
        print_info("  GITLAB_DEFAULT_HOST=https://your-gitlab-instance.com")
        print_info("  GITLAB_ACCESS_TOKEN=your-gitlab-token")
        return False

    print_success("Archivo .env encontrado")

    # Cargar variables de entorno
    load_dotenv()

    required_vars = {
        'SONAR_DEFAULT_HOST': 'URL de SonarQube',
        'SONAR_ACCESS_TOKEN': 'Token de acceso SonarQube',
        'GITLAB_DEFAULT_HOST': 'URL de GitLab',
        'GITLAB_ACCESS_TOKEN': 'Token de acceso GitLab'
    }

    all_vars_present = True

    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # Ocultar parte del token por seguridad
            if 'TOKEN' in var_name:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print_success(f"{var_name} = {display_value}")
        else:
            print_error(f"{var_name} NO definida ({description})")
            all_vars_present = False

    return all_vars_present


def check_connectivity():
    """Verifica la conectividad con SonarQube y GitLab"""
    print_header("Verificando conectividad con APIs")

    load_dotenv()

    # Verificar SonarQube
    sonar_host = os.getenv('SONAR_DEFAULT_HOST')
    sonar_token = os.getenv('SONAR_ACCESS_TOKEN')

    if sonar_host and sonar_token:
        try:
            import requests
            headers = {
                'Authorization': f'Bearer {sonar_token}',
                'Accept': 'application/json'
            }
            response = requests.get(
                f"{sonar_host}/api/system/status",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                print_success(f"Conexión exitosa con SonarQube: {sonar_host}")
            elif response.status_code == 401:
                print_error(f"Error de autenticación con SonarQube (token inválido)")
                return False
            else:
                print_warning(f"SonarQube respondió con código: {response.status_code}")
        except requests.exceptions.Timeout:
            print_error(f"Timeout al conectar con SonarQube: {sonar_host}")
            return False
        except requests.exceptions.ConnectionError:
            print_error(f"No se puede conectar con SonarQube: {sonar_host}")
            return False
        except Exception as e:
            print_error(f"Error al verificar SonarQube: {e}")
            return False
    else:
        print_warning("Saltando verificación de SonarQube (credenciales no configuradas)")

    # Verificar GitLab
    gitlab_host = os.getenv('GITLAB_DEFAULT_HOST')
    gitlab_token = os.getenv('GITLAB_ACCESS_TOKEN')

    if gitlab_host and gitlab_token:
        try:
            import requests
            headers = {
                'PRIVATE-TOKEN': gitlab_token
            }
            response = requests.get(
                f"{gitlab_host}/api/v4/version",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                version_info = response.json()
                print_success(f"Conexión exitosa con GitLab: {gitlab_host} (v{version_info.get('version', 'unknown')})")
            elif response.status_code == 401:
                print_error(f"Error de autenticación con GitLab (token inválido)")
                return False
            else:
                print_warning(f"GitLab respondió con código: {response.status_code}")
        except requests.exceptions.Timeout:
            print_error(f"Timeout al conectar con GitLab: {gitlab_host}")
            return False
        except requests.exceptions.ConnectionError:
            print_error(f"No se puede conectar con GitLab: {gitlab_host}")
            return False
        except Exception as e:
            print_error(f"Error al verificar GitLab: {e}")
            return False
    else:
        print_warning("Saltando verificación de GitLab (credenciales no configuradas)")

    return True


def check_directories():
    """Verifica y crea la estructura de directorios necesaria"""
    print_header("Verificando estructura de directorios")

    required_dirs = [
        'src',
        'src/api',
        'src/etl',
        'src/etl/sonar',
        'src/etl/gitlab',
        'src/utils',
        'logs',
        'xlsx',
        'xlsx/SONAR',
        'xlsx/GITLAB'
    ]

    all_dirs_ok = True

    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            if path.is_dir():
                print_success(f"Directorio existe: {dir_path}/")
            else:
                print_error(f"{dir_path} existe pero NO es un directorio")
                all_dirs_ok = False
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print_success(f"Directorio creado: {dir_path}/")
            except Exception as e:
                print_error(f"No se pudo crear directorio {dir_path}: {e}")
                all_dirs_ok = False

    return all_dirs_ok


def check_write_permissions():
    """Verifica permisos de escritura en directorios de salida"""
    print_header("Verificando permisos de escritura")

    test_dirs = ['logs', 'xlsx/SONAR', 'xlsx/GITLAB']
    all_writable = True

    for dir_path in test_dirs:
        path = Path(dir_path)
        test_file = path / '.write_test'

        try:
            test_file.write_text('test')
            test_file.unlink()
            print_success(f"Permiso de escritura OK: {dir_path}/")
        except Exception as e:
            print_error(f"Sin permiso de escritura en {dir_path}: {e}")
            all_writable = False

    return all_writable


def check_config_files():
    """Verifica la existencia de archivos de configuración"""
    print_header("Verificando archivos de configuración")

    config_files = [
        'src/configSonar.py',
        'src/configGitlab.py',
        'src/main_etl_sonar.py',
        'src/main_etl_gitlab.py'
    ]

    all_files_ok = True

    for file_path in config_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"Archivo encontrado: {file_path}")
        else:
            print_error(f"Archivo NO encontrado: {file_path}")
            all_files_ok = False

    return all_files_ok


def print_summary(results):
    """Imprime el resumen de la validación"""
    print_header("Resumen de Validación")

    total_checks = len(results)
    passed_checks = sum(results.values())
    failed_checks = total_checks - passed_checks

    for check_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        color = Colors.GREEN if passed else Colors.RED
        print(f"{color}{status}{Colors.END} - {check_name}")

    print(f"\n{Colors.BOLD}Total: {passed_checks}/{total_checks} verificaciones exitosas{Colors.END}")

    if failed_checks == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}¡Todo está correcto! El proyecto está listo para usar.{Colors.END}")
        print_info("\nPuedes ejecutar los ETL con:")
        print_info("  python src/main_etl_sonar.py")
        print_info("  python src/main_etl_gitlab.py")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Se encontraron {failed_checks} problema(s). Por favor, revisa los errores arriba.{Colors.END}")
        return False


def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}Validador de Configuración - ETL SonarQube & GitLab{Colors.END}")
    print(f"{Colors.BLUE}Este script verificará que tu entorno esté correctamente configurado{Colors.END}")

    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Ejecutar todas las verificaciones
    results = {
        'Versión de Python': check_python_version(),
        'Dependencias instaladas': check_dependencies(),
        'Archivo .env configurado': check_env_file(),
        'Conectividad con APIs': check_connectivity(),
        'Estructura de directorios': check_directories(),
        'Permisos de escritura': check_write_permissions(),
        'Archivos de configuración': check_config_files()
    }

    # Mostrar resumen
    success = print_summary(results)

    # Código de salida
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
