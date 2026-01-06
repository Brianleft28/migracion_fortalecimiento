# Sistema de Migración de Beneficiarios - Fortalecimiento

Sistema automatizado para la migración mensual de datos de beneficiarios desde archivos Excel a una base de datos PostgreSQL, con actualización de la tabla `beneficios_ciudadanos`.

## Características

- 📊 Lectura de datos de beneficiarios desde archivos Excel (.xlsx, .xls)
- 🗄️ Migración automática a la base de datos PostgreSQL
- 🔄 Actualización de la tabla `beneficios_ciudadanos`
- 📝 Registro detallado de operaciones (logs)
- ✅ Validación de configuración y datos
- 🔒 Gestión segura de credenciales mediante variables de entorno

## Requisitos Previos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clone el repositorio:
```bash
git clone https://github.com/Brianleft28/migracion_fortalecimiento.git
cd migracion_fortalecimiento
```

2. Cree un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instale las dependencias:
```bash
pip install -r requirements.txt
```

4. Configure las variables de entorno:
```bash
cp .env.example .env
# Edite el archivo .env con sus credenciales de base de datos
```

## Configuración

Edite el archivo `.env` con su configuración:

```env
# Configuración de Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fortalecimiento
DB_USER=su_usuario
DB_PASSWORD=su_contraseña

# Archivo Excel
EXCEL_FILE_PATH=data/beneficiarios.xlsx

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/migration.log
```

## Estructura del Proyecto

```
migracion_fortalecimiento/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuración de la aplicación
│   ├── models/
│   │   ├── __init__.py
│   │   └── migration.py         # Lógica de migración y actualización
│   └── utils/
│       ├── __init__.py
│       ├── database.py          # Gestión de conexiones a BD
│       └── excel_reader.py      # Lectura de archivos Excel
├── migrate.py                   # Script principal de migración
├── requirements.txt             # Dependencias del proyecto
├── .env.example                 # Plantilla de configuración
├── .gitignore                   # Archivos excluidos de git
└── README.md                    # Este archivo
```

## Uso

### Migración Básica

Ejecute el script principal con la configuración por defecto:

```bash
python migrate.py
```

### Opciones Avanzadas

```bash
# Especificar un archivo Excel diferente
python migrate.py --excel-file /ruta/al/archivo.xlsx

# Especificar una hoja específica (por nombre o índice)
python migrate.py --sheet-name "Beneficiarios 2024"
python migrate.py --sheet-name 1

# Validar configuración sin migrar datos (dry run)
python migrate.py --dry-run

# Migrar sin actualizar beneficios_ciudadanos
python migrate.py --skip-beneficios-update
```

### Combinación de Opciones

```bash
python migrate.py --excel-file datos.xlsx --sheet-name 0 --skip-beneficios-update
```

## Estructura de Datos Esperada

### Archivo Excel de Entrada

El archivo Excel debe contener las siguientes columnas (los nombres se ajustarán automáticamente):

- Identificación del ciudadano
- Tipo de beneficio
- Fecha de asignación
- Estado
- Otros campos según la estructura de su tabla `beneficiarios`

**Nota:** Los nombres de columnas se normalizarán automáticamente (espacios a guiones bajos, minúsculas).

### Tablas de Base de Datos

#### Tabla `beneficiarios`
```sql
CREATE TABLE beneficiarios (
    id SERIAL PRIMARY KEY,
    ciudadano_id VARCHAR(50),
    beneficio_id INT,
    fecha_migracion TIMESTAMP,
    -- otros campos según su estructura
);
```

#### Tabla `beneficios_ciudadanos`
```sql
CREATE TABLE beneficios_ciudadanos (
    id SERIAL PRIMARY KEY,
    ciudadano_id VARCHAR(50),
    beneficio_id INT,
    fecha_asignacion TIMESTAMP,
    fecha_actualizacion TIMESTAMP,
    estado VARCHAR(20),
    -- otros campos según su estructura
);
```

## Logs

Los logs se guardan en el archivo especificado en `LOG_FILE` (por defecto: `logs/migration.log`).

Niveles de log disponibles:
- `DEBUG`: Información detallada para diagnóstico
- `INFO`: Confirmación de operaciones normales
- `WARNING`: Advertencias
- `ERROR`: Errores que impiden completar una operación

## Solución de Problemas

### Error de conexión a la base de datos

Verifique que:
- PostgreSQL esté ejecutándose
- Las credenciales en `.env` sean correctas
- El usuario tenga permisos suficientes

### Archivo Excel no encontrado

Verifique que:
- La ruta en `EXCEL_FILE_PATH` sea correcta
- El archivo tenga extensión `.xlsx` o `.xls`
- Tenga permisos de lectura sobre el archivo

### Errores de columnas faltantes

Asegúrese de que:
- El archivo Excel contenga todas las columnas requeridas
- Los nombres de columnas coincidan con la estructura esperada

## Mantenimiento

### Actualización de Dependencias

```bash
pip install --upgrade -r requirements.txt
```

### Respaldo de Datos

Se recomienda realizar respaldos de la base de datos antes de ejecutar migraciones:

```bash
pg_dump -U usuario -d fortalecimiento > backup_$(date +%Y%m%d).sql
```

## Seguridad

- **Nunca** incluya el archivo `.env` en control de versiones
- Mantenga las credenciales de base de datos seguras
- Restrinja permisos de archivos sensibles
- Revise los logs regularmente para detectar problemas

## Contribución

Para contribuir al proyecto:

1. Haga fork del repositorio
2. Cree una rama para su feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit sus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Cree un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.

## Contacto

Para preguntas o soporte, contacte al equipo de desarrollo.

## Changelog

### Versión 1.0.0 (2026-01-06)
- Implementación inicial del sistema de migración
- Soporte para archivos Excel
- Migración a tabla beneficiarios
- Actualización de tabla beneficios_ciudadanos
- Sistema de logging
- Configuración mediante variables de entorno