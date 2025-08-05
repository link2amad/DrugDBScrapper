import pyodbc
import logging
from datetime import datetime
from config.database_config import DatabaseConfig

class DatabaseHandler:
    def __init__(self):
        self.connection_string = DatabaseConfig.get_connection_string()
        self.logger = logging.getLogger(__name__)
        
    def create_connection(self):
        """Create database connection"""
        try:
            connection = pyodbc.connect(self.connection_string)
            return connection
        except pyodbc.Error as e:
            self.logger.error(f"Database connection failed: {e}")
            # Try trusted connection as fallback
            try:
                connection = pyodbc.connect(DatabaseConfig.get_trusted_connection_string())
                return connection
            except pyodbc.Error as e2:
                self.logger.error(f"Trusted connection also failed: {e2}")
                raise
    
    def create_table_if_not_exists(self):
        """Create the Medicines table if it doesn't exist"""
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Medicines' AND xtype='U')
        CREATE TABLE Medicines (
            SystemId INT IDENTITY(1,1) PRIMARY KEY,
            ExternalId NVARCHAR(100) UNIQUE NOT NULL,
            CompleteName NVARCHAR(500),
            BrandName NVARCHAR(200),
            GenericName NVARCHAR(300),
            PackSize NVARCHAR(100),
            ListingPrice DECIMAL(10,2),
            ListingOriginalPrice DECIMAL(10,2),
            DetailPrice DECIMAL(10,2),
            DetailOriginalPrice DECIMAL(10,2),
            GenericRefLink NVARCHAR(500),
            DrugExternalLink NVARCHAR(500),
            ImagePath NVARCHAR(200),
            CreatedDate DATETIME DEFAULT GETDATE(),
            UpdatedDate DATETIME DEFAULT GETDATE()
        )
        """
        
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                conn.commit()
                self.logger.info("Medicines table created/verified successfully")
        except Exception as e:
            self.logger.error(f"Error creating table: {e}")
            raise
    
    def add_new_columns_if_not_exist(self):
        """Add new columns if they don't exist (for existing databases)"""
        columns_to_add = [
            ('BrandName', 'NVARCHAR(200)'),
            ('PackSize', 'NVARCHAR(100)'),
            ('ListingPrice', 'DECIMAL(10,2)'),
            ('ListingOriginalPrice', 'DECIMAL(10,2)'),
            ('DetailPrice', 'DECIMAL(10,2)'),
            ('DetailOriginalPrice', 'DECIMAL(10,2)')
        ]
        
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                
                for column_name, column_type in columns_to_add:
                    # Check if column exists
                    check_sql = f"""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'Medicines' AND COLUMN_NAME = '{column_name}'
                    """
                    cursor.execute(check_sql)
                    exists = cursor.fetchone()[0]
                    
                    if not exists:
                        # Add column
                        add_sql = f"ALTER TABLE Medicines ADD {column_name} {column_type}"
                        cursor.execute(add_sql)
                        self.logger.info(f"Added column: {column_name}")
                
                conn.commit()
                self.logger.info("Database schema updated successfully")
                
        except Exception as e:
            self.logger.error(f"Error updating database schema: {e}")
            raise
    
    def medicine_exists(self, external_id):
        """Check if medicine already exists in database"""
        check_sql = "SELECT COUNT(*) FROM Medicines WHERE ExternalId = ?"
        
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(check_sql, (external_id,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            self.logger.error(f"Error checking medicine existence: {e}")
            return False
    
    def insert_medicine(self, external_id, complete_name, brand_name, generic_name, pack_size, 
                       listing_price, listing_original_price, detail_price, detail_original_price,
                       generic_ref_link, drug_external_link, image_path):
        """Insert new medicine record"""
        insert_sql = """
        INSERT INTO Medicines (ExternalId, CompleteName, BrandName, GenericName, PackSize, 
                              ListingPrice, ListingOriginalPrice, DetailPrice, DetailOriginalPrice,
                              GenericRefLink, DrugExternalLink, ImagePath)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(insert_sql, (
                    external_id, complete_name, brand_name, generic_name, 
                    pack_size, listing_price, listing_original_price, 
                    detail_price, detail_original_price, generic_ref_link, 
                    drug_external_link, image_path
                ))
                conn.commit()
                
                # Get the auto-generated SystemId
                cursor.execute("SELECT @@IDENTITY")
                system_id = cursor.fetchone()[0]
                
                self.logger.info(f"Medicine inserted successfully with SystemId: {system_id}")
                return system_id
        except Exception as e:
            self.logger.error(f"Error inserting medicine: {e}")
            raise
    
    def update_medicine(self, external_id, complete_name, brand_name, generic_name, pack_size,
                       listing_price, listing_original_price, detail_price, detail_original_price,
                       generic_ref_link, drug_external_link, image_path):
        """Update existing medicine record"""
        update_sql = """
        UPDATE Medicines 
        SET CompleteName = ?, BrandName = ?, GenericName = ?, PackSize = ?, 
            ListingPrice = ?, ListingOriginalPrice = ?, DetailPrice = ?, DetailOriginalPrice = ?,
            GenericRefLink = ?, DrugExternalLink = ?, ImagePath = ?, UpdatedDate = GETDATE()
        WHERE ExternalId = ?
        """
        
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(update_sql, (
                    complete_name, brand_name, generic_name, pack_size, 
                    listing_price, listing_original_price, detail_price, detail_original_price,
                    generic_ref_link, drug_external_link, image_path, external_id
                ))
                conn.commit()
                
                self.logger.info(f"Medicine updated successfully: {external_id}")
        except Exception as e:
            self.logger.error(f"Error updating medicine: {e}")
            raise
    
    def get_statistics(self):
        """Get database statistics"""
        stats_sql = """
        SELECT 
            COUNT(*) as TotalMedicines,
            COUNT(CASE WHEN ImagePath IS NOT NULL THEN 1 END) as MedicinesWithImages,
            COUNT(CASE WHEN GenericName IS NOT NULL THEN 1 END) as MedicinesWithGenericNames,
            COUNT(CASE WHEN ListingPrice IS NOT NULL THEN 1 END) as MedicinesWithListingPrices,
            COUNT(CASE WHEN DetailPrice IS NOT NULL THEN 1 END) as MedicinesWithDetailPrices,
            MIN(CreatedDate) as FirstRecord,
            MAX(CreatedDate) as LastRecord
        FROM Medicines
        """
        
        try:
            with self.create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(stats_sql)
                result = cursor.fetchone()
                
                return {
                    'total_medicines': result[0],
                    'medicines_with_images': result[1],
                    'medicines_with_generic_names': result[2],
                    'medicines_with_listing_prices': result[3],
                    'medicines_with_detail_prices': result[4],
                    'first_record': result[5],
                    'last_record': result[6]
                }
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return None 