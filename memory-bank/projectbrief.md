# Pakistan Medical Industry Drug Database Scraper - Project Brief

## Project Overview
A comprehensive web scraper designed to collect medicine data from dawaai.pk and store it in a MSSQL database for Pakistan's medical industry. The project focuses on creating a robust, multi-execution secure system with anti-blocking measures.

## Core Objectives
1. **Data Collection**: Extract complete medicine information from dawaai.pk
2. **Database Integration**: Store data in MSSQL with proper schema design
3. **Multi-Execution Security**: Prevent duplicate entries using external IDs
4. **Anti-Blocking**: Implement measures to avoid being blocked by the website
5. **Comprehensive Coverage**: Scrape all medicines A-Z from the website

## Key Requirements

### Data Fields to Extract
1. **Complete Name**: Full medicine name (e.g., "Arnil 75mg tablet 2x10's")
2. **Brand Name**: Manufacturer/brand information (e.g., "Ferozsons")
3. **Generic Name**: Active ingredient information (e.g., "Diclofenac Sodium (75mg)")
4. **Pack Size**: Package information (e.g., "1x10's", "1 Ampx3ml")
5. **Listing Price**: Price from listing page (e.g., "Rs 488")
6. **Listing Original Price**: Original price from listing page (e.g., "Rs 542")
7. **Detail Price**: Price from detail page (if different)
8. **Detail Original Price**: Original price from detail page (if different)
9. **Generic Reference Link**: Link to generic information page
10. **Drug External Link**: Direct link to medicine page on dawaai.pk
11. **System ID**: Auto-generated unique identifier
12. **Medicine Image**: Downloaded and saved with system ID as filename

### Technical Requirements
- **Multi-Execution Security**: Use external IDs to prevent duplicates
- **Anti-Blocking**: Rotating user agents, random delays, retry logic
- **Database**: MSSQL with proper indexing and constraints
- **Image Handling**: Download and validate medicine images
- **Error Recovery**: Continue operation even if individual pages fail
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Data Source Structure
- **Base URL**: https://dawaai.pk
- **Listing Pages**: https://dawaai.pk/all-medicines/{letter} (A-Z)
- **Detail Pages**: https://dawaai.pk/medicine/{medicine-id}.html
- **Generic Pages**: https://dawaai.pk/generic/{generic-name}

## Success Criteria
1. Successfully scrape all medicines from A-Z
2. Store data in properly structured MSSQL database
3. Download and store medicine images
4. Handle duplicate prevention using external IDs
5. Implement anti-blocking measures
6. Provide comprehensive logging and monitoring
7. Support multiple execution runs safely

## Project Scope
- **In Scope**: Medicine data scraping, database storage, image downloading, anti-blocking measures
- **Out of Scope**: User interface, API development, real-time updates, data analysis tools

## Timeline
- **Phase 1**: Core scraper development and database setup
- **Phase 2**: Anti-blocking measures and error handling
- **Phase 3**: Testing and optimization
- **Phase 4**: Documentation and deployment

## Stakeholders
- **Primary**: Pakistan Medical Industry stakeholders
- **Secondary**: Healthcare professionals, researchers, pharmaceutical companies 