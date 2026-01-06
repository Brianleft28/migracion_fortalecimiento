#!/usr/bin/env python3
"""
Main script for monthly beneficiarios data migration.

This script performs the following tasks:
1. Reads beneficiarios data from an Excel file
2. Migrates the data to the beneficiarios table in the database
3. Updates the beneficios_ciudadanos table based on the migrated data
"""
import argparse
import logging
import sys
from pathlib import Path

from src.config import Config
from src.utils import DatabaseManager, ExcelReader
from src.models import BeneficiariosMigrator, BeneficiosCiudadanosUpdater


def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path(Config.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Migración mensual de datos de beneficiarios'
    )
    parser.add_argument(
        '--excel-file',
        type=str,
        help='Path to Excel file with beneficiarios data'
    )
    parser.add_argument(
        '--sheet-name',
        type=str,
        default='0',
        help='Excel sheet name or index (default: 0)'
    )
    parser.add_argument(
        '--skip-beneficios-update',
        action='store_true',
        help='Skip updating beneficios_ciudadanos table'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate configuration and file without performing migration'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info("=" * 80)
    logger.info("Starting monthly beneficiarios migration process")
    logger.info("=" * 80)
    
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Determine Excel file path
        excel_file = args.excel_file or Config.EXCEL_FILE_PATH
        logger.info(f"Excel file: {excel_file}")
        
        # Initialize Excel reader
        logger.info("Initializing Excel reader...")
        excel_reader = ExcelReader(excel_file)
        
        # Convert sheet name to int if it's numeric
        sheet_name = args.sheet_name
        if sheet_name.isdigit():
            sheet_name = int(sheet_name)
        
        logger.info(f"Sheet name: {sheet_name}")
        
        # Show available sheets
        sheets = excel_reader.get_sheet_names()
        logger.info(f"Available sheets in Excel file: {sheets}")
        
        if args.dry_run:
            logger.info("Dry run mode - validation completed successfully")
            logger.info("No data was migrated")
            return 0
        
        # Initialize database manager
        logger.info("Connecting to database...")
        db_manager = DatabaseManager()
        
        # Test database connection
        if not db_manager.test_connection():
            logger.error("Database connection test failed")
            return 1
        
        logger.info("Database connection successful")
        
        # Initialize migrator
        logger.info("Initializing beneficiarios migrator...")
        migrator = BeneficiariosMigrator(db_manager, excel_reader)
        
        # Perform migration
        logger.info("Starting data migration...")
        migrated_count = migrator.migrate_beneficiarios(
            sheet_name=sheet_name,
            table_name='beneficiarios'
        )
        
        logger.info(f"Migration completed: {migrated_count} records migrated")
        
        # Get migration summary
        summary = migrator.get_migration_summary()
        logger.info(f"Migration summary: {summary}")
        
        # Update beneficios_ciudadanos table
        if not args.skip_beneficios_update:
            logger.info("Updating beneficios_ciudadanos table...")
            updater = BeneficiosCiudadanosUpdater(db_manager)
            
            updated_count = updater.update_from_beneficiarios()
            logger.info(f"Update completed: {updated_count} records updated")
            
            # Get update summary
            update_summary = updater.get_update_summary()
            logger.info(f"Update summary: {update_summary}")
        else:
            logger.info("Skipping beneficios_ciudadanos update (--skip-beneficios-update flag)")
        
        # Close database connections
        db_manager.close()
        
        logger.info("=" * 80)
        logger.info("Migration process completed successfully")
        logger.info("=" * 80)
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
