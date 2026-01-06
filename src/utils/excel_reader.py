"""Excel file reader module for beneficiarios data."""
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)


class ExcelReader:
    """Reads beneficiarios data from Excel files."""
    
    def __init__(self, file_path):
        """
        Initialize Excel reader.
        
        Args:
            file_path: Path to the Excel file
        """
        self.file_path = Path(file_path)
        self._validate_file()
    
    def _validate_file(self):
        """Validate that the Excel file exists and is readable."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")
        
        if self.file_path.suffix.lower() not in ['.xlsx', '.xls']:
            raise ValueError(f"File must be an Excel file (.xlsx or .xls): {self.file_path}")
        
        logger.info(f"Excel file validated: {self.file_path}")
    
    def read_beneficiarios(self, sheet_name=0):
        """
        Read beneficiarios data from Excel file.
        
        Args:
            sheet_name: Name or index of the sheet to read (default: 0)
                       Must be int or str type.
            
        Returns:
            pandas DataFrame with beneficiarios data
        """
        if not isinstance(sheet_name, (int, str)):
            raise TypeError(f"sheet_name must be int or str, got {type(sheet_name).__name__}")
        
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            logger.info(f"Successfully read {len(df)} rows from Excel file")
            return df
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            raise
    
    def get_sheet_names(self):
        """Get list of sheet names in the Excel file."""
        try:
            xl_file = pd.ExcelFile(self.file_path)
            return xl_file.sheet_names
        except Exception as e:
            logger.error(f"Error getting sheet names: {e}")
            raise
    
    def read_all_sheets(self):
        """
        Read all sheets from Excel file.
        
        Returns:
            Dictionary with sheet names as keys and DataFrames as values
        """
        try:
            sheets = pd.read_excel(self.file_path, sheet_name=None)
            logger.info(f"Successfully read {len(sheets)} sheets from Excel file")
            return sheets
        except Exception as e:
            logger.error(f"Error reading all sheets: {e}")
            raise
    
    @staticmethod
    def clean_column_names(df):
        """
        Clean column names by removing spaces and special characters.
        Modifies the DataFrame in-place.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            DataFrame with cleaned column names (same object, modified in-place)
        """
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(r'[^a-z0-9_]', '', regex=True)
        return df
    
    @staticmethod
    def validate_required_columns(df, required_columns):
        """
        Validate that required columns exist in DataFrame.
        
        Args:
            df: pandas DataFrame
            required_columns: List of required column names
            
        Raises:
            ValueError if any required columns are missing
        """
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        logger.info("All required columns present")
