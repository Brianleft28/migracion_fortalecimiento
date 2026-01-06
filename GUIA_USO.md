# Guía de Uso - Sistema de Migración de Beneficiarios

## Índice
1. [Configuración Inicial](#configuración-inicial)
2. [Preparación de Datos](#preparación-de-datos)
3. [Ejecución de la Migración](#ejecución-de-la-migración)
4. [Casos de Uso Comunes](#casos-de-uso-comunes)
5. [Verificación y Monitoreo](#verificación-y-monitoreo)
6. [Solución de Problemas](#solución-de-problemas)

## Configuración Inicial

### 1. Configuración de la Base de Datos

Antes de ejecutar la migración, asegúrese de tener una base de datos PostgreSQL configurada.

#### Crear la base de datos:
```sql
CREATE DATABASE fortalecimiento;
```

#### Ejecutar el script de configuración:
```bash
psql -U postgres -d fortalecimiento -f database_setup.sql
```

### 2. Configuración del Archivo .env

Copie el archivo de ejemplo y edítelo con sus credenciales:

```bash
cp .env.example .env
nano .env  # o use su editor preferido
```

Ejemplo de configuración:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fortalecimiento
DB_USER=mi_usuario
DB_PASSWORD=mi_contraseña_segura
EXCEL_FILE_PATH=data/beneficiarios.xlsx
LOG_LEVEL=INFO
LOG_FILE=logs/migration.log
```

## Preparación de Datos

### Formato del Archivo Excel

El archivo Excel debe contener las siguientes columnas (mínimo):

| Columna | Tipo | Descripción | Requerido |
|---------|------|-------------|-----------|
| Ciudadano ID | Texto | Identificación única del ciudadano | Sí |
| Nombre | Texto | Nombre completo del ciudadano | No |
| Beneficio ID | Número | ID del tipo de beneficio | Sí |
| Nombre Beneficio | Texto | Descripción del beneficio | No |
| Fecha Asignacion | Fecha | Fecha de asignación del beneficio | Sí |
| Monto | Número | Valor monetario del beneficio | No |
| Estado | Texto | Estado del beneficio (ACTIVO, PENDIENTE, etc.) | No |
| Observaciones | Texto | Notas adicionales | No |

### Generar un Archivo de Ejemplo

Si necesita un archivo de ejemplo para probar el sistema:

```bash
python3 generate_example.py
```

Esto creará `data/ejemplo_beneficiarios.xlsx` con datos de prueba.

## Ejecución de la Migración

### 1. Validación Previa (Dry Run)

Siempre ejecute primero en modo dry-run para validar la configuración:

```bash
python3 migrate.py --dry-run
```

### 2. Migración Completa

Una vez validado, ejecute la migración real:

```bash
python3 migrate.py
```

### 3. Migración con Archivo Específico

Si tiene múltiples archivos:

```bash
python3 migrate.py --excel-file data/beneficiarios_enero_2024.xlsx
```

### 4. Migración de una Hoja Específica

Si su Excel tiene múltiples hojas:

```bash
# Por índice (0 = primera hoja)
python3 migrate.py --sheet-name 0

# Por nombre
python3 migrate.py --sheet-name "Beneficiarios Enero"
```

## Casos de Uso Comunes

### Caso 1: Migración Mensual Regular

```bash
#!/bin/bash
# Script para migración mensual automatizada

# 1. Validar archivo
echo "Validando archivo y configuración..."
python3 migrate.py --dry-run

# 2. Si la validación es exitosa, ejecutar migración
if [ $? -eq 0 ]; then
    echo "Iniciando migración..."
    python3 migrate.py
else
    echo "Error en validación. Revise los logs."
    exit 1
fi
```

### Caso 2: Migrar sin Actualizar beneficios_ciudadanos

Si solo necesita migrar datos sin actualizar la tabla relacionada:

```bash
python3 migrate.py --skip-beneficios-update
```

### Caso 3: Migración de Múltiples Archivos

```bash
#!/bin/bash
# Procesar múltiples archivos Excel

for file in data/beneficiarios_*.xlsx; do
    echo "Procesando: $file"
    python3 migrate.py --excel-file "$file"
    sleep 2  # Pequeña pausa entre migraciones
done
```

### Caso 4: Migración con Backup Automático

```bash
#!/bin/bash
# Backup antes de migración

# Crear backup
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -U usuario -d fortalecimiento > "backups/$BACKUP_FILE"

# Ejecutar migración
python3 migrate.py

# Verificar resultado
if [ $? -eq 0 ]; then
    echo "Migración exitosa. Backup guardado en: $BACKUP_FILE"
else
    echo "Error en migración. Puede restaurar desde: $BACKUP_FILE"
fi
```

## Verificación y Monitoreo

### 1. Revisar Logs

Los logs se guardan en el archivo especificado en `LOG_FILE`:

```bash
# Ver logs en tiempo real
tail -f logs/migration.log

# Ver últimas 50 líneas
tail -n 50 logs/migration.log

# Buscar errores
grep ERROR logs/migration.log
```

### 2. Verificar en Base de Datos

```sql
-- Contar registros migrados hoy
SELECT COUNT(*) 
FROM beneficiarios 
WHERE DATE(fecha_migracion) = CURRENT_DATE;

-- Ver últimos 10 registros migrados
SELECT * 
FROM beneficiarios 
ORDER BY fecha_migracion DESC 
LIMIT 10;

-- Verificar actualización de beneficios_ciudadanos
SELECT estado, COUNT(*) 
FROM beneficios_ciudadanos 
GROUP BY estado;
```

### 3. Script de Verificación

Cree un script SQL para verificación rápida:

```sql
-- verificacion.sql
\echo 'Resumen de Migración'
\echo '===================='

\echo '\nRegistros en beneficiarios:'
SELECT COUNT(*) as total FROM beneficiarios;

\echo '\nRegistros migrados hoy:'
SELECT COUNT(*) as hoy 
FROM beneficiarios 
WHERE DATE(fecha_migracion) = CURRENT_DATE;

\echo '\nEstado de beneficios_ciudadanos:'
SELECT estado, COUNT(*) as cantidad 
FROM beneficios_ciudadanos 
GROUP BY estado;
```

Ejecutar:
```bash
psql -U usuario -d fortalecimiento -f verificacion.sql
```

## Solución de Problemas

### Error: "Excel file not found"

**Causa**: El archivo Excel no existe en la ruta especificada.

**Solución**:
```bash
# Verificar la ruta del archivo
ls -l data/beneficiarios.xlsx

# O especificar la ruta completa
python3 migrate.py --excel-file /ruta/completa/al/archivo.xlsx
```

### Error: "Missing required columns"

**Causa**: El archivo Excel no tiene las columnas esperadas.

**Solución**:
1. Abra el archivo Excel y verifique los nombres de las columnas
2. Use el archivo de ejemplo como referencia:
   ```bash
   python3 generate_example.py
   ```
3. Asegúrese de que los nombres de columnas coincidan (el sistema los normalizará automáticamente)

### Error: "Database connection failed"

**Causa**: No se puede conectar a la base de datos.

**Solución**:
```bash
# 1. Verificar que PostgreSQL esté ejecutándose
sudo systemctl status postgresql

# 2. Probar conexión manualmente
psql -U usuario -d fortalecimiento -h localhost

# 3. Verificar credenciales en .env
cat .env

# 4. Verificar permisos del usuario
psql -U postgres
\du  # Lista usuarios y permisos
```

### Error: "Duplicate key violation"

**Causa**: Intento de insertar registros duplicados.

**Solución**:
El sistema tiene restricciones UNIQUE. Si esto ocurre:

1. Revise si ya migró estos datos
2. Considere limpiar registros previos si es una re-migración:
   ```sql
   DELETE FROM beneficiarios 
   WHERE DATE(fecha_migracion) = CURRENT_DATE;
   ```

### Logs Muestran Advertencias

Si ve advertencias en los logs:

```bash
# Filtrar solo errores críticos
grep -E "ERROR|CRITICAL" logs/migration.log

# Ver contexto de errores (3 líneas antes y después)
grep -C 3 ERROR logs/migration.log
```

## Automatización con Cron

Para ejecutar la migración automáticamente cada mes:

```bash
# Editar crontab
crontab -e

# Agregar entrada (primer día del mes a las 2 AM)
0 2 1 * * cd /ruta/al/proyecto && /usr/bin/python3 migrate.py >> /var/log/migracion.log 2>&1
```

## Contacto y Soporte

Para soporte adicional o reportar problemas:
- Revise los logs en detalle
- Verifique la configuración de base de datos
- Consulte la documentación en README.md
- Contacte al equipo de desarrollo

---

**Última actualización**: 2026-01-06  
**Versión**: 1.0.0
