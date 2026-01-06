"""Database connection and operations module."""
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize database manager with configuration."""
        self.engine = None
        self.Session = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine."""
        try:
            database_url = Config.get_database_url()
            self.engine = create_engine(
                database_url,
                pool_pre_ping=True,
                echo=False
            )
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self):
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Execute a query and return results."""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.fetchall()
    
    def execute_insert(self, query, params):
        """Execute an insert query."""
        with self.get_session() as session:
            session.execute(text(query), params)
    
    def execute_update(self, query, params):
        """Execute an update query."""
        with self.get_session() as session:
            result = session.execute(text(query), params)
            return result.rowcount
    
    def bulk_insert(self, table_name, data_list):
        """Bulk insert data into a table using executemany for better performance."""
        if not data_list:
            logger.warning("No data to insert")
            return 0
        
        # Validate table name to prevent SQL injection
        allowed_tables = ['beneficiarios', 'beneficios_ciudadanos']
        if table_name not in allowed_tables:
            raise ValueError(f"Table name not allowed: {table_name}")
        
        # Get column names from first record
        columns = list(data_list[0].keys())
        columns_str = ", ".join(columns)
        placeholders = ", ".join([f":{col}" for col in columns])
        
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        with self.get_session() as session:
            # Use connection.execute with multiple parameters for true bulk insert
            session.connection().execute(text(query), data_list)
        
        logger.info(f"Inserted {len(data_list)} records into {table_name}")
        return len(data_list)
    
    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
