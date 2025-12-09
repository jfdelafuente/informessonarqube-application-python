# Guía Rápida de Inicio

Esta guía te ayudará a configurar y ejecutar el proyecto en menos de 5 minutos.

## Pasos Rápidos

### 1. Crear y Activar Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Copia el archivo de ejemplo y edítalo con tus credenciales:

**Windows:**
```bash
copy .env.example .env
notepad .env
```

**Linux/Mac:**
```bash
cp .env.example .env
nano .env  # o usa tu editor preferido
```

Configura las siguientes variables:
- `SONAR_DEFAULT_HOST` - URL de tu SonarQube
- `SONAR_ACCESS_TOKEN` - Token de acceso de SonarQube
- `GITLAB_DEFAULT_HOST` - URL de tu GitLab
- `GITLAB_ACCESS_TOKEN` - Token de acceso de GitLab

### 4. Validar Configuración

```bash
python validate_setup.py
```

Si todo está OK (7/7), continúa al paso 5.

### 5. Ejecutar ETL

**SonarQube:**
```bash
python src/main_etl_sonar.py
```

**GitLab:**
```bash
python src/main_etl_gitlab.py
```

## Archivos de Salida

Los resultados se guardan en:
- `xlsx/SONAR/` - Archivos CSV con datos de SonarQube
- `xlsx/GITLAB/` - Archivos CSV y Excel con datos de GitLab
- `logs/` - Archivos de log para auditoría

## Comandos Útiles

```bash
# Verificar solo conexiones
python test_connection.py

# Ver versión de Python y dependencias
python validate_setup.py

# Desactivar entorno virtual cuando termines
deactivate
```

## Problemas Comunes

### El entorno virtual no se activa (Windows)
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

### Error "ModuleNotFoundError"
```bash
# Verifica que el entorno virtual esté activado (debe aparecer (venv) en el prompt)
pip install -r requirements.txt
```

### Error de autenticación
```bash
# Prueba tus credenciales
python test_connection.py
```

## Próximos Pasos

- Lee el [README.MD](README.MD) para documentación completa
- Revisa [src/configSonar.py](src/configSonar.py) para configuración avanzada de SonarQube
- Revisa [src/configGitlab.py](src/configGitlab.py) para configuración de GitLab

## Soporte

Si encuentras problemas, consulta la sección de Troubleshooting en [README.MD](README.MD).
