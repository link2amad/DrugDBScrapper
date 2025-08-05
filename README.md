# Pakistan Medical Industry Drug Database Scraper

A robust web scraper for collecting medicine data from dawaai.pk and storing it in a MSSQL database. This tool is designed to be multi-execution secure, anti-blocking, and comprehensive in data collection.

## Features

- **Multi-Execution Secure**: Uses external IDs to prevent duplicate entries
- **Anti-Blocking Measures**: Rotating user agents, random delays, and retry logic
- **Comprehensive Data Collection**: Extracts complete medicine information including images
- **Robust Error Handling**: Continues operation even if individual pages fail
- **Database Integration**: Direct MSSQL integration with auto-incremented system IDs
- **Image Download**: Downloads and validates medicine images
- **Detailed Logging**: Comprehensive logging for monitoring and debugging

## Data Collected

For each medicine, the scraper collects:

1. **Complete Name**: Full medicine name (e.g., "Arnil 75mg tablet 2x10's")
2. **Generic Name**: Active ingredient information (e.g., "Diclofenac Sodium (75mg)")
3. **Generic Reference Link**: Link to generic information page
4. **Drug External Link**: Direct link to the medicine page on dawaai.pk
5. **System ID**: Auto-generated unique identifier
6. **Medicine Image**: Downloaded and saved with system ID as filename

## Project Structure

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
├── env.example               # Environment configuration example
└── README.md                 # This file
```

## Prerequisites

- Python 3.7 or higher
- MSSQL Server (local or remote)
- ODBC Driver for SQL Server
- Internet connection

## Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd WebScrapper
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database connection**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your database settings
   nano .env
   ```

4. **Database Setup**
   - Create a new database in MSSQL Server
   - Update the `.env` file with your database credentials
   - The scraper will automatically create the required table

## Configuration

### Database Configuration (.env file)

```env
# Database Server
DB_SERVER=localhost

# Database Name
DB_NAME=MedicineDatabase

# Database Username
DB_USERNAME=sa

# Database Password (leave empty for Windows Authentication)
DB_PASSWORD=

# Database Driver
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### Common ODBC Drivers

- **Windows**: `ODBC Driver 17 for SQL Server` or `ODBC Driver 18 for SQL Server`
- **Linux**: `ODBC Driver 17 for SQL Server` (requires Microsoft driver installation)
- **Legacy**: `SQL Server Native Client 11.0`

## Usage

### Command Line Interface

The scraper provides a comprehensive command-line interface:

```bash
# Test database connection
python main.py --test-db

# Scrape medicines for a specific letter
python main.py --scrape-letter a

# Scrape all letters A-Z
python main.py --scrape-all

# Show database statistics
python main.py --stats

# Enable verbose logging
python main.py --scrape-all --verbose

# Get help
python main.py --help
```

### Examples

```bash
# Test your setup first
python main.py --test-db

# Start with a single letter to test
python main.py --scrape-letter a --verbose

# Run full scraping (this will take several hours)
python main.py --scrape-all

# Check progress
python main.py --stats
```

## Database Schema

The scraper creates the following table structure:

```sql
CREATE TABLE Medicines (
    SystemId INT IDENTITY(1,1) PRIMARY KEY,
    ExternalId NVARCHAR(100) UNIQUE NOT NULL,
    CompleteName NVARCHAR(500),
    GenericName NVARCHAR(300),
    GenericRefLink NVARCHAR(500),
    DrugExternalLink NVARCHAR(500),
    ImagePath NVARCHAR(200),
    CreatedDate DATETIME DEFAULT GETDATE(),
    UpdatedDate DATETIME DEFAULT GETDATE()
)
```

## Anti-Blocking Features

The scraper implements several measures to avoid being blocked:

- **Rotating User Agents**: Uses different browser user agents for each request
- **Random Delays**: 2-5 second delays between requests with additional randomization
- **Exponential Backoff**: Retry logic with increasing delays on failures
- **Session Management**: Maintains session cookies and headers
- **Respectful Scraping**: Longer delays between letter pages (5-10 seconds)

## Multi-Execution Security

- **External ID Tracking**: Each medicine has a unique external ID from the source URL
- **Duplicate Prevention**: Checks existing records before insertion
- **Resume Capability**: Can be run multiple times safely
- **Update Support**: Can update existing records if needed

## Monitoring and Logging

- **Comprehensive Logging**: All operations are logged to both file and console
- **Timestamped Log Files**: Logs are saved with timestamps in the `logs/` directory
- **Statistics Tracking**: Real-time statistics on scraping progress
- **Error Reporting**: Detailed error messages for troubleshooting

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify SQL Server is running
   - Check database credentials in `.env` file
   - Ensure ODBC driver is installed

2. **No Medicines Found**
   - Check internet connection
   - Verify website structure hasn't changed
   - Try with `--verbose` flag for detailed logging

3. **Images Not Downloading**
   - Check disk space in `data/images/` directory
   - Verify image URLs are accessible
   - Check firewall/proxy settings

4. **Scraper Getting Blocked**
   - Increase delays in the scraper configuration
   - Use VPN or proxy if necessary
   - Run during off-peak hours

### Performance Tips

- **Start Small**: Test with single letters first
- **Monitor Resources**: Check disk space and memory usage
- **Network Stability**: Ensure stable internet connection
- **Database Performance**: Consider indexing for large datasets

## Legal and Ethical Considerations

- **Respectful Scraping**: The scraper includes delays to avoid overwhelming the server
- **Terms of Service**: Ensure compliance with dawaai.pk's terms of service
- **Data Usage**: Use collected data responsibly and in accordance with applicable laws
- **Attribution**: Consider providing attribution to the source website

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with all applicable laws and website terms of service.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the `logs/` directory
3. Create an issue with detailed error information

## Changelog

### Version 1.0.0
- Initial release
- Complete scraping functionality
- MSSQL database integration
- Image downloading
- Anti-blocking measures
- Multi-execution security 