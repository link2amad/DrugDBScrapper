# System Patterns - Pakistan Medical Industry Drug Database Scraper

## Architecture Overview

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main Script   │───▶│  DawaaiScraper  │───▶│ DatabaseHandler │
│   (main.py)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  ImageDownloader│    │  Config System  │    │   MSSQL Server  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Project Structure
```
WebScrapper/
├── scraper/
│   ├── __init__.py
│   ├── dawaai_scraper.py      # Main scraping logic
│   ├── database_handler.py    # MSSQL operations
│   └── image_downloader.py    # Image handling
├── config/
│   ├── __init__.py
│   └── database_config.py     # Database connection settings
├── data/
│   └── images/                # Downloaded images
├── logs/                      # Log files
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── env.example               # Environment configuration
└── README.md                 # Documentation
```

## Key Design Patterns

### 1. Multi-Execution Security Pattern
**Problem**: Prevent duplicate entries when scraper runs multiple times
**Solution**: External ID-based duplicate checking
```python
# Extract unique external ID from URL
external_id = self._extract_external_id(medicine_url)

# Check if medicine already exists
if self.db_handler.medicine_exists(external_id):
    return  # Skip if already processed
```

### 2. Anti-Blocking Pattern
**Problem**: Website may block automated requests
**Solution**: Multiple anti-blocking measures
```python
# Rotating user agents
self.session.headers['User-Agent'] = self.ua.random

# Random delays between requests
time.sleep(random.uniform(2, 5))

# Exponential backoff retry logic
wait_time = (2 ** attempt) + random.uniform(0, 1)
```

### 3. Data Extraction Pattern
**Problem**: Extract data from both listing and detail pages
**Solution**: Two-phase data extraction
```python
# Phase 1: Extract from listing page
listing_data = self._extract_listing_page_data(container)

# Phase 2: Extract from detail page
detail_data = self._extract_medicine_data(medicine_url, listing_data)
```

### 4. Error Recovery Pattern
**Problem**: Individual page failures shouldn't stop entire process
**Solution**: Try-catch with continue logic
```python
for medicine_data in medicine_data_list:
    try:
        self._process_medicine(medicine_data)
    except Exception as e:
        self.logger.error(f"Error processing medicine: {e}")
        continue  # Continue with next medicine
```

## Database Schema Design

### Medicines Table
```sql
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
```

### Key Design Decisions
1. **ExternalId UNIQUE**: Prevents duplicate entries
2. **Separate Price Columns**: Captures both listing and detail page prices
3. **Nullable Fields**: Allows partial data when some fields unavailable
4. **Auto-timestamps**: Tracks creation and update times

## Data Flow Patterns

### 1. Scraping Flow
```
Letter Page (A-Z) → Extract Medicine Links → Detail Pages → Database
```

### 2. Data Processing Flow
```
Raw HTML → BeautifulSoup Parsing → Regex Extraction → Data Validation → Database Storage
```

### 3. Image Processing Flow
```
Image URL → Download → Validation → Save with SystemID → Update Database
```

## Configuration Management

### Environment-Based Configuration
```python
class DatabaseConfig:
    SERVER = os.getenv('DB_SERVER', 'localhost')
    DATABASE = os.getenv('DB_NAME', 'MedicineDatabase')
    USERNAME = os.getenv('DB_USERNAME', 'sa')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
```

### Configuration File Structure
```env
# .env file
DB_SERVER=localhost
DB_NAME=MedicineDatabase
DB_USERNAME=sa
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 17 for SQL Server
```

## Logging and Monitoring

### Logging Strategy
- **File Logging**: Timestamped log files in `logs/` directory
- **Console Logging**: Real-time output for monitoring
- **Structured Logging**: Consistent format across all components
- **Error Tracking**: Detailed error information for debugging

### Statistics Tracking
```python
self.stats = {
    'total_processed': 0,
    'new_medicines': 0,
    'updated_medicines': 0,
    'failed_requests': 0,
    'images_downloaded': 0
}
```

## Security Patterns

### 1. Input Validation
- URL validation before processing
- Data type validation before database insertion
- File path validation for image downloads

### 2. Error Handling
- Graceful degradation on failures
- Comprehensive error logging
- Retry logic with exponential backoff

### 3. Resource Management
- Connection pooling for database
- Session management for HTTP requests
- File system cleanup for orphaned images

## Performance Patterns

### 1. Rate Limiting
- Random delays between requests (2-5 seconds)
- Longer delays between letter pages (5-10 seconds)
- Exponential backoff on failures

### 2. Memory Management
- Streaming image downloads
- Batch database operations
- Garbage collection optimization

### 3. Scalability Considerations
- Modular design for easy extension
- Configuration-driven behavior
- Stateless processing for horizontal scaling

## Testing Patterns

### 1. Setup Verification
- Dependency checking
- Database connection testing
- Directory structure validation

### 2. Data Validation
- Field completeness checking
- Data type validation
- Business rule validation

### 3. Error Simulation
- Network failure testing
- Database error handling
- Invalid data processing 