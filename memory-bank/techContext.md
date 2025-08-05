# Technical Context - Pakistan Medical Industry Drug Database Scraper

## Technology Stack

### Core Technologies
- **Python 3.13.5**: Primary programming language
- **MSSQL Server**: Database management system
- **ODBC Driver**: Database connectivity
- **BeautifulSoup4**: HTML parsing and data extraction
- **Requests**: HTTP client for web scraping

### Key Dependencies

#### Web Scraping
```python
requests==2.32.4              # HTTP client library
beautifulsoup4==4.13.4        # HTML/XML parser
lxml==6.0.0                   # XML/HTML processor
fake-useragent==2.2.0         # Rotating user agents
urllib3==2.5.0                # HTTP library
```

#### Database
```python
pyodbc==5.2.0                 # ODBC database adapter
python-dotenv==1.1.1          # Environment variable management
```

#### Image Processing
```python
Pillow==11.3.0                # Image processing library
```

#### Utilities
```python
charset_normalizer==3.4.2     # Character encoding detection
certifi==2025.8.3             # SSL certificate verification
```

## Development Environment

### System Requirements
- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: 3.7 or higher (tested with 3.13.5)
- **MSSQL Server**: 2016 or higher
- **ODBC Driver**: 17 or 18 for SQL Server
- **Memory**: Minimum 4GB RAM
- **Storage**: 10GB+ for images and database

### Python Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Database Setup
```sql
-- Create database
CREATE DATABASE MedicineDatabase;

-- Create table (auto-created by scraper)
-- Medicines table with all required columns
```

## Configuration Management

### Environment Variables
```env
# Database Configuration
DB_SERVER=localhost
DB_NAME=MedicineDatabase
DB_USERNAME=sa
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### Configuration Classes
```python
class DatabaseConfig:
    SERVER = os.getenv('DB_SERVER', 'localhost')
    DATABASE = os.getenv('DB_NAME', 'MedicineDatabase')
    USERNAME = os.getenv('DB_USERNAME', 'sa')
    PASSWORD = os.getenv('DB_PASSWORD', '')
    DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
```

## Data Extraction Techniques

### HTML Parsing Strategy
```python
# BeautifulSoup parsing
soup = BeautifulSoup(response.content, 'html.parser')

# Multiple selector strategies
selectors = [
    'h1', '.product-title', '.medicine-title',
    '.generic-name', '.price', '.brand-name'
]
```

### Regular Expression Patterns
```python
# External ID extraction
r'/medicine/([^/]+)\.html'

# Price extraction
r'Rs\s*(\d+(?:,\d+)*)'

# Brand name cleaning
r'^Brand\s*:\s*'
r'\s+(Health|Limited|Pharma|Laboratories?)$'
```

### Anti-Blocking Measures
```python
# Rotating user agents
self.session.headers['User-Agent'] = self.ua.random

# Random delays
time.sleep(random.uniform(2, 5))

# Exponential backoff
wait_time = (2 ** attempt) + random.uniform(0, 1)
```

## Database Connectivity

### Connection String Formats
```python
# Standard connection
f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

# Trusted connection (Windows Authentication)
f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
```

### Connection Management
```python
# Connection pooling
with self.create_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
```

## File System Management

### Directory Structure
```
data/
├── images/           # Downloaded medicine images
│   ├── 1.jpg        # Image for SystemId 1
│   ├── 2.png        # Image for SystemId 2
│   └── ...
logs/
├── scraper_20240805_143022.log
├── scraper_20240805_150145.log
└── ...
```

### Image Processing
```python
# Image validation
image = Image.open(BytesIO(image_data))
image.verify()

# File naming
filename = f"{system_id}.{file_extension}"
```

## Error Handling Strategies

### Network Errors
```python
try:
    response = self.session.get(url, timeout=30)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    # Retry logic with exponential backoff
    wait_time = (2 ** attempt) + random.uniform(0, 1)
    time.sleep(wait_time)
```

### Database Errors
```python
try:
    with self.create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
except pyodbc.Error as e:
    self.logger.error(f"Database error: {e}")
    # Fallback to trusted connection
```

### Data Validation
```python
# Field validation
if brand and len(brand) > 2 and len(brand) < 50:
    if re.match(r'^[A-Za-z\s\-\.&]+$', brand):
        return brand
```

## Performance Optimization

### Memory Management
```python
# Streaming downloads
response = self.session.get(image_url, timeout=30, stream=True)
with open(filepath, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
```

### Database Optimization
```python
# Batch operations
cursor.executemany(sql, params_list)

# Connection reuse
self.session = requests.Session()
```

### Rate Limiting
```python
# Request delays
time.sleep(random.uniform(2, 5))  # Between requests
time.sleep(random.uniform(5, 10)) # Between letter pages
```

## Monitoring and Logging

### Logging Configuration
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

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

## Security Considerations

### Input Validation
- URL validation before processing
- SQL injection prevention with parameterized queries
- File path validation for image downloads

### Data Protection
- Environment variable usage for sensitive data
- No hardcoded credentials
- Secure file permissions

### Network Security
- HTTPS usage for all requests
- Certificate verification
- Timeout settings to prevent hanging connections

## Deployment Considerations

### Production Requirements
- **Server**: Dedicated server with stable internet connection
- **Database**: MSSQL Server with adequate storage
- **Monitoring**: Log monitoring and alerting
- **Backup**: Regular database and image backups

### Scalability
- Modular design for horizontal scaling
- Configuration-driven behavior
- Stateless processing architecture

### Maintenance
- Regular dependency updates
- Log rotation and cleanup
- Database maintenance and optimization
- Image storage management 