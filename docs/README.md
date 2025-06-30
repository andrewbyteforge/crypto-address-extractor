# Crypto Address Extractor

A comprehensive Python application for extracting and validating cryptocurrency addresses from various sources with GUI and API integration capabilities.

## Features

- **Multi-cryptocurrency support** with advanced validation
- **GUI interface** with tabbed layout for easy use
- **API integration** for enhanced address validation and data retrieval
- **File processing** supporting multiple formats
- **Comprehensive reporting** with Excel export capabilities
- **Performance monitoring** and optimization
- **Detailed logging** system
- **Batch processing** capabilities

## Supported Cryptocurrencies

- Bitcoin (BTC) - Legacy, SegWit, and Bech32 formats
- Ethereum (ETH)
- Cardano (ADA)
- And many more through enhanced validators

## Project Structure

### Core Components
- **`main.py`** - Main application entry point
- **`extractor.py`** - Core address extraction logic
- **`validators.py`** - Basic cryptocurrency address validators
- **`enhanced_validators.py`** - Advanced validation algorithms
- **`patterns.py`** - Regex patterns for different crypto addresses

### GUI Components
- **`gui_tabs.py`** - Main GUI tabbed interface
- **`gui_handlers.py`** - GUI event handlers
- **`gui_styles.py`** - UI styling and themes
- **`gui_extraction_handler.py`** - GUI extraction logic
- **`gui_api_processor.py`** - API integration for GUI

### API and Services
- **`api_tab.py`** - API interface tab
- **`iapi_service.py`** - External API service integration
- **`iapi_class_fix.py`** - API class fixes and improvements

### File Processing
- **`file_handler.py`** - File input/output operations
- **`report_generator.py`** - Report generation and formatting
- **`i2_exporter.py`** - Advanced export functionality

### Utilities
- **`logger_config.py`** - Logging configuration
- **`config.py`** - Application configuration
- **`bech32.py`** - Bech32 address format support
- **`performance_monitor.py`** - Performance tracking

### Batch Scripts
- **`run_crypto_extractor.bat`** - Basic application launcher
- **`run_crypto_extractor_advanced.bat`** - Advanced launcher with options

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/crypto-address-extractor.git
cd crypto-address-extractor
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install required dependencies:
```bash
pip install -r requirements.txt
```

5. Configure the application:
   - Copy `config.json.example` to `config.json`
   - Update configuration settings as needed

## Usage

### GUI Mode
Run the main application with GUI:
```bash
python main.py
```

Or use the batch script:
```bash
run_crypto_extractor.bat
```

### Command Line Mode
For batch processing and automation:
```bash
python extractor.py --input input_file.txt --output results.xlsx
```

## Configuration

The application uses `config.json` for configuration settings. Key settings include:

- API endpoints and keys
- Validation parameters
- Output formats
- Logging levels

**Note:** Never commit your actual `config.json` with API keys to version control.

## Development

### Project Requirements
- Python 3.7+
- tkinter (for GUI)
- Additional dependencies listed in `requirements.txt`

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Notes

- API keys and sensitive configuration should be stored in environment variables or secure config files
- The `.gitignore` file is configured to exclude sensitive files
- Always validate and sanitize input data

## License

This project is open source. Please ensure compliance with all applicable laws and regulations when using this software.

## Support

For issues and questions, please open an issue on GitHub.

---

**Disclaimer:** This tool is for educational and legitimate purposes only. Always ensure compliance with applicable laws and terms of service when extracting and processing cryptocurrency addresses.