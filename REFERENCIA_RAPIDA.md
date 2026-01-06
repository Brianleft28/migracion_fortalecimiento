# Referencia Rápida - Migración de Beneficiarios

## Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/Brianleft28/migracion_fortalecimiento.git
cd migracion_fortalecimiento

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
psql -U postgres -d fortalecimiento -f database_setup.sql

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con sus credenciales
```

## Comandos Principales

```bash
# Validar configuración (no migra datos)
python migrate.py --dry-run

# Migración completa
python migrate.py

# Migración con archivo específico
python migrate.py --excel-file data/mi_archivo.xlsx

# Migración de hoja específica
python migrate.py --sheet-name "Beneficiarios Enero"

# Solo migrar, sin actualizar beneficios_ciudadanos
python migrate.py --skip-beneficios-update

# Generar archivo de ejemplo
python generate_example.py
```

## Estructura de Archivos Excel

| Columna Requerida | Tipo | Ejemplo |
|-------------------|------|---------|
| Ciudadano ID | Texto | CC01234567 |
| Beneficio ID | Número | 1, 2, 3, etc. |
| Fecha Asignacion | Fecha | 2024-01-15 |

**Columnas Opcionales**: Nombre, Nombre Beneficio, Monto, Estado, Observaciones

## Verificación en Base de Datos

```sql
-- Ver registros migrados hoy
SELECT COUNT(*) FROM beneficiarios 
WHERE DATE(fecha_migracion) = CURRENT_DATE;

-- Últimos registros
SELECT * FROM beneficiarios 
ORDER BY fecha_migracion DESC LIMIT 10;

-- Estado de beneficios
SELECT estado, COUNT(*) 
FROM beneficios_ciudadanos 
GROUP BY estado;
```

## Logs

```bash
# Ver logs en tiempo real
tail -f logs/migration.log

# Buscar errores
grep ERROR logs/migration.log
```

## Solución Rápida de Problemas

| Error | Solución |
|-------|----------|
| Excel file not found | Verificar ruta en .env o --excel-file |
| Database connection failed | Verificar PostgreSQL activo y credenciales |
| Missing columns | Usar archivo ejemplo como referencia |
| Duplicate key | Ya existe el registro, revisar datos |

## Respaldo de Seguridad

```bash
# Crear respaldo antes de migrar
pg_dump -U usuario -d fortalecimiento > backup_$(date +%Y%m%d).sql

# Restaurar si es necesario
psql -U usuario -d fortalecimiento < backup_20240115.sql
```

## Automatización Mensual

```bash
# Agregar a crontab (primer día del mes a las 2 AM)
crontab -e

# Agregar esta línea:
0 2 1 * * cd /ruta/proyecto && python migrate.py >> /var/log/migracion.log 2>&1
```

## Estructura del Proyecto

```
migracion_fortalecimiento/
├── migrate.py              # Script principal ⭐
├── requirements.txt        # Dependencias
├── .env.example           # Plantilla de configuración
├── database_setup.sql     # Setup de BD
├── generate_example.py    # Generador de ejemplos
├── README.md              # Documentación completa
├── GUIA_USO.md           # Guía detallada de uso
├── src/
│   ├── config/           # Configuración
│   ├── models/           # Lógica de negocio
│   └── utils/            # Utilidades
└── data/
    └── ejemplo_beneficiarios.xlsx  # Archivo de ejemplo
```

## Soporte

- 📖 Documentación completa: `README.md`
- 📚 Guía de uso detallada: `GUIA_USO.md`
- 🔍 Revisar logs: `logs/migration.log`
- 💻 Repositorio: https://github.com/Brianleft28/migracion_fortalecimiento

---
**Versión**: 1.0.0 | **Última actualización**: 2026-01-06
