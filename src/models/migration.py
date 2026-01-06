"""Data migration models and logic."""
import logging
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class BeneficiariosMigrator:
    """Handles migration of beneficiarios data from Excel to database."""
    
    def __init__(self, db_manager, excel_reader):
        """
        Initialize migrator.
        
        Args:
            db_manager: DatabaseManager instance
            excel_reader: ExcelReader instance
        """
        self.db = db_manager
        self.excel_reader = excel_reader
    
    def prepare_data(self, df):
        """
        Prepare DataFrame for database insertion.
        
        Args:
            df: pandas DataFrame with beneficiarios data
            
        Returns:
            List of dictionaries ready for insertion
        """
        # Clean column names
        df = self.excel_reader.clean_column_names(df)
        
        # Remove rows with all NaN values
        df = df.dropna(how='all')
        
        # Add migration timestamp
        df['fecha_migracion'] = datetime.now()
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        
        logger.info(f"Prepared {len(records)} records for migration")
        return records
    
    def migrate_beneficiarios(self, sheet_name=0, table_name='beneficiarios'):
        """
        Migrate beneficiarios data from Excel to database.
        
        Args:
            sheet_name: Excel sheet to read (default: 0)
            table_name: Target database table (default: 'beneficiarios')
            
        Returns:
            Number of records migrated
        """
        try:
            logger.info(f"Starting migration of beneficiarios to table '{table_name}'")
            
            # Read data from Excel
            df = self.excel_reader.read_beneficiarios(sheet_name=sheet_name)
            
            if df.empty:
                logger.warning("No data to migrate")
                return 0
            
            # Prepare data for insertion
            records = self.prepare_data(df)
            
            # Insert data into database
            count = self.db.bulk_insert(table_name, records)
            
            logger.info(f"Successfully migrated {count} beneficiarios records")
            return count
            
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            raise
    
    def get_migration_summary(self, table_name='beneficiarios'):
        """
        Get summary statistics of migrated data.
        
        Args:
            table_name: Database table name
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            # Validate table name to prevent SQL injection
            allowed_tables = ['beneficiarios', 'beneficios_ciudadanos']
            if table_name not in allowed_tables:
                raise ValueError(f"Table name not allowed: {table_name}")
            
            query = f"SELECT COUNT(*) as total FROM {table_name}"
            result = self.db.execute_query(query)
            total = result[0][0] if result else 0
            
            query_today = f"""
                SELECT COUNT(*) as today_count 
                FROM {table_name} 
                WHERE DATE(fecha_migracion) = CURRENT_DATE
            """
            result_today = self.db.execute_query(query_today)
            today_count = result_today[0][0] if result_today else 0
            
            summary = {
                'total_records': total,
                'migrated_today': today_count,
                'table_name': table_name
            }
            
            logger.info(f"Migration summary: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error getting migration summary: {e}")
            return {
                'total_records': 0,
                'migrated_today': 0,
                'table_name': table_name,
                'error': str(e)
            }


class BeneficiosCiudadanosUpdater:
    """Handles updates to beneficios_ciudadanos table."""
    
    def __init__(self, db_manager):
        """
        Initialize updater.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
    
    def update_from_beneficiarios(self, beneficiarios_table='beneficiarios', 
                                   beneficios_table='beneficios_ciudadanos'):
        """
        Update beneficios_ciudadanos table based on beneficiarios data.
        
        This method synchronizes data between the beneficiarios table
        and the beneficios_ciudadanos table.
        
        Args:
            beneficiarios_table: Source table name
            beneficios_table: Target table name to update
            
        Returns:
            Number of records updated
        """
        try:
            # Validate table names to prevent SQL injection
            allowed_tables = ['beneficiarios', 'beneficios_ciudadanos']
            if beneficiarios_table not in allowed_tables or beneficios_table not in allowed_tables:
                raise ValueError("Table name not allowed")
            
            logger.info(f"Updating {beneficios_table} from {beneficiarios_table}")
            
            # This is a generic update query that should be customized
            # based on actual table structure and business logic
            update_query = f"""
                INSERT INTO {beneficios_table} (
                    ciudadano_id, beneficio_id, fecha_asignacion, estado
                )
                SELECT 
                    b.ciudadano_id,
                    b.beneficio_id,
                    b.fecha_migracion,
                    'ACTIVO' as estado
                FROM {beneficiarios_table} b
                WHERE NOT EXISTS (
                    SELECT 1 
                    FROM {beneficios_table} bc 
                    WHERE bc.ciudadano_id = b.ciudadano_id 
                    AND bc.beneficio_id = b.beneficio_id
                )
            """
            
            updated_count = self.db.execute_update(update_query, {})
            
            logger.info(f"Updated {updated_count} records in {beneficios_table}")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating beneficios_ciudadanos: {e}")
            raise
    
    def update_estado_beneficios(self, ciudadano_id=None, nuevo_estado='ACTIVO', 
                                 beneficios_table='beneficios_ciudadanos'):
        """
        Update estado field for beneficios records.
        
        Args:
            ciudadano_id: Specific ciudadano ID to update (optional)
            nuevo_estado: New estado value
            beneficios_table: Table name
            
        Returns:
            Number of records updated
        """
        try:
            # Validate table name to prevent SQL injection
            allowed_tables = ['beneficiarios', 'beneficios_ciudadanos']
            if beneficios_table not in allowed_tables:
                raise ValueError(f"Table name not allowed: {beneficios_table}")
            
            if ciudadano_id:
                query = f"""
                    UPDATE {beneficios_table}
                    SET estado = :estado, fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE ciudadano_id = :ciudadano_id
                """
                params = {'estado': nuevo_estado, 'ciudadano_id': ciudadano_id}
            else:
                query = f"""
                    UPDATE {beneficios_table}
                    SET estado = :estado, fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE fecha_actualizacion IS NULL OR estado != :estado
                """
                params = {'estado': nuevo_estado}
            
            updated_count = self.db.execute_update(query, params)
            
            logger.info(f"Updated estado for {updated_count} records")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating estado: {e}")
            raise
    
    def get_update_summary(self, beneficios_table='beneficios_ciudadanos'):
        """
        Get summary of beneficios_ciudadanos table.
        
        Args:
            beneficios_table: Table name
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            # Validate table name to prevent SQL injection
            allowed_tables = ['beneficiarios', 'beneficios_ciudadanos']
            if beneficios_table not in allowed_tables:
                raise ValueError(f"Table name not allowed: {beneficios_table}")
            
            query = f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN estado = 'ACTIVO' THEN 1 END) as activos,
                    COUNT(CASE WHEN estado = 'INACTIVO' THEN 1 END) as inactivos
                FROM {beneficios_table}
            """
            result = self.db.execute_query(query)
            
            if result:
                row = result[0]
                summary = {
                    'total_records': row[0],
                    'activos': row[1],
                    'inactivos': row[2],
                    'table_name': beneficios_table
                }
            else:
                summary = {
                    'total_records': 0,
                    'activos': 0,
                    'inactivos': 0,
                    'table_name': beneficios_table
                }
            
            logger.info(f"Update summary: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error getting update summary: {e}")
            return {
                'total_records': 0,
                'activos': 0,
                'inactivos': 0,
                'table_name': beneficios_table,
                'error': str(e)
            }
