-- Database setup script for beneficiarios migration system
-- PostgreSQL version

-- Create beneficiarios table
CREATE TABLE IF NOT EXISTS beneficiarios (
    id SERIAL PRIMARY KEY,
    ciudadano_id VARCHAR(50) NOT NULL,
    nombre VARCHAR(200),
    beneficio_id INTEGER,
    nombre_beneficio VARCHAR(200),
    fecha_asignacion DATE,
    monto DECIMAL(10, 2),
    estado VARCHAR(50),
    observaciones TEXT,
    fecha_migracion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ciudadano_id, beneficio_id, fecha_asignacion)
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_beneficiarios_ciudadano_id ON beneficiarios(ciudadano_id);
CREATE INDEX IF NOT EXISTS idx_beneficiarios_beneficio_id ON beneficiarios(beneficio_id);
CREATE INDEX IF NOT EXISTS idx_beneficiarios_fecha_migracion ON beneficiarios(fecha_migracion);

-- Create beneficios_ciudadanos table
CREATE TABLE IF NOT EXISTS beneficios_ciudadanos (
    id SERIAL PRIMARY KEY,
    ciudadano_id VARCHAR(50) NOT NULL,
    beneficio_id INTEGER NOT NULL,
    fecha_asignacion TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(50) DEFAULT 'ACTIVO',
    monto DECIMAL(10, 2),
    observaciones TEXT,
    UNIQUE(ciudadano_id, beneficio_id)
);

-- Create indexes for beneficios_ciudadanos
CREATE INDEX IF NOT EXISTS idx_beneficios_ciudadanos_ciudadano_id ON beneficios_ciudadanos(ciudadano_id);
CREATE INDEX IF NOT EXISTS idx_beneficios_ciudadanos_beneficio_id ON beneficios_ciudadanos(beneficio_id);
CREATE INDEX IF NOT EXISTS idx_beneficios_ciudadanos_estado ON beneficios_ciudadanos(estado);

-- Create trigger to update fecha_actualizacion automatically
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fecha_actualizacion
    BEFORE UPDATE ON beneficios_ciudadanos
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

-- Comments on tables
COMMENT ON TABLE beneficiarios IS 'Tabla que almacena los datos de beneficiarios migrados desde Excel';
COMMENT ON TABLE beneficios_ciudadanos IS 'Tabla que almacena los beneficios asignados a ciudadanos';

-- Comments on important columns
COMMENT ON COLUMN beneficiarios.fecha_migracion IS 'Fecha y hora en que se realizó la migración del registro';
COMMENT ON COLUMN beneficios_ciudadanos.fecha_actualizacion IS 'Fecha y hora de la última actualización del registro';
