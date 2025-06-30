Crypto Address Extractor - Enhanced Version
Updated Overview (January 2025)
🚀 Recent Enhancements
1. Enhanced API Integration

Entity Name Display: Cluster names from Chainalysis API now appear as "Entity Name" in Excel exports
Exchange Exposure Formatting: Exchange exposures are displayed in a user-friendly format (e.g., "Binance: 45.2%, Coinbase: 23.1%")
API Data in Individual Sheets: Entity Name and Exchange Exposure columns now appear prominently in each cryptocurrency sheet

2. Excel Export Improvements

Duplicate Removal: Each cryptocurrency sheet now displays only unique addresses, eliminating duplicates for cleaner analysis
Fixed API Data Export: Resolved issues where API data wasn't appearing in Excel files when API analysis was enabled
Improved Column Layout: Entity Name and Exchange Exposure appear as the first API data columns for better visibility

3. Bug Fixes

Fixed "AttributeError: 'list' object has no attribute 'items'" error during report generation
Resolved missing _create_balance_sheet method error by properly handling optional analysis sheets
Fixed issue where include_api_data parameter wasn't being passed to Excel export functions

📊 Core Features
Address Extraction

Extracts cryptocurrency addresses from CSV and Excel files
Supports 30+ cryptocurrencies including Bitcoin, Ethereum, Solana, and more
Advanced pattern matching with checksum validation
Confidence scoring for each extracted address
Handles multiple file formats and sheet structures

Chainalysis API Integration

Cluster Information: Retrieves entity names and categories
Balance Data: Gets current balances and transaction volumes
Exchange Exposure: Identifies interactions with known exchanges
Risk Analysis: Provides risk levels based on address behavior
Performance: Optimized bulk processing with deduplication to minimize API calls

Excel Export Features

Summary Sheet: Overview statistics of extraction results
All Addresses Sheet: Complete list of all extracted addresses with duplicates marked
Individual Crypto Sheets:

Separate sheet for each cryptocurrency
Shows only unique addresses (no duplicates)
Includes Entity Name and Exchange Exposure when API is enabled
Full API data columns (balance, transactions, risk level)


Duplicate Analysis Sheet: Identifies and groups duplicate addresses across files

Additional Export Formats

i2 Analyst's Notebook: XML export for graph analysis
PDF Reports: Professional investigation reports
Word Documents: Editable report formats
CSV Export: Raw data for further analysis

🔧 Technical Improvements
Performance Optimizations

Bulk deduplication before API calls to avoid redundant requests
Concurrent API processing with configurable thread pools
Efficient memory usage for large datasets
Excel row limit handling with pagination support

Error Handling

Graceful handling of API failures
Comprehensive logging for debugging
Backup creation before file modifications
Clear error messages with suggested fixes

📋 How to Use
Basic Extraction

Select CSV/Excel files containing addresses
Click "Extract Addresses"
Review results in the generated Excel file

With API Enhancement

Enable "Chainalysis API analysis" in Extract Addresses tab
Select desired API options (balance, exposure, cluster info)
Run extraction - API data will appear in Excel sheets
Check individual crypto sheets for Entity Name and Exchange Exposure

Understanding the Output

Entity Name: The cluster/service name associated with the address (e.g., "Binance Hot Wallet")
Exchange Exposure: Percentage of funds exposed to various exchanges
Unique Addresses: Each crypto sheet shows addresses only once, even if they appear multiple times in source files

🛠️ Configuration
API Settings

Configure Chainalysis API key in Settings tab
Adjust concurrent API calls (1-20 threads)
Choose output currency (USD/Native)

Extraction Options

Enable/disable checksum validation
Select specific cryptocurrencies to extract
Add custom cryptocurrency patterns

📈 Best Practices

For Large Datasets: Use the API "SMART" strategy to prioritize high-value addresses
Duplicate Handling: Check "All Addresses" sheet to see all occurrences, individual crypto sheets for unique addresses only
API Usage: Enable only needed API endpoints to optimize processing time
Excel Files: Close Excel files before re-running extraction to avoid permission errors

🔍 Troubleshooting
Common Issues

API data not appearing: Ensure "Enable Chainalysis API analysis" is checked
Excel permission errors: Close the output file before running extraction
Missing methods error: Run the fix_missing_methods.py script
Duplicate addresses: Now automatically removed from crypto sheets

Recent Fixes Applied

api_excel_export_patch.py: Fixes API data not appearing in Excel
fix_report_items_error.py: Resolves report generation errors
fix_missing_methods.py: Handles missing analysis sheet methods
remove_duplicates_crypto_sheets.py: Removes duplicate addresses from crypto sheets

📚 File Structure
crypto_address_extractor/
├── main.py                    # Main application entry point
├── gui_extraction_handler.py  # Handles extraction workflow
├── gui_api_processor.py       # Manages API calls and data enhancement
├── file_handler.py           # Excel file creation and formatting
├── api_service.py            # Chainalysis API interface
├── extractor.py              # Core address extraction logic
└── [various fix scripts]     # Patches for recent enhancements

Future Enhancements
Re-enable advanced analysis sheets (Balance, High Value, Risk Analysis)
Enhanced visualization options
Bulk address investigation workflows

