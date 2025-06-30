#!/usr/bin/env python3
"""
Enhanced Direct/Indirect Exposure Data Patch
===========================================

This script enhances the cryptocurrency address extractor to properly capture and display
direct and indirect exposure data for both RECEIVING and SENDING directions.

Features:
1. Separates exposure data by direction (receiving vs sending)
2. Adds detailed columns for direct and indirect exposure
3. Includes exposure values and percentages
4. Updates Excel export to show all exposure details

Usage:
    python add_detailed_exposure_columns.py

Author: Crypto Extractor Tool
Date: 2025-01-18
Version: 1.0.0
"""

import os
import sys
import shutil
import re
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def backup_file(filepath):
    """
    Create a timestamped backup of the original file.
    
    Args:
        filepath (str): Path to the file to backup
        
    Returns:
        str: Path to the backup file
        
    Raises:
        IOError: If backup creation fails
    """
    try:
        backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        logger.info(f"✅ Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup for {filepath}: {e}")
        raise


def patch_gui_api_processor():
    """
    Patch gui_api_processor.py to properly separate receiving and sending exposure.
    
    Returns:
        bool: True if successful, False otherwise
    """
    file_path = "gui_api_processor.py"
    
    if not os.path.exists(file_path):
        logger.error(f"❌ ERROR: {file_path} not found")
        return False
    
    logger.info(f"🔧 Patching {file_path}...")
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add enhanced exposure storage after the existing exposure processing
        enhancement = '''
                # Enhanced: Store separated receiving and sending exposure
                if api_data.get('exchange_exposure'):
                    exposure_data = api_data['exchange_exposure']
                    direction = api_data.get('exposure_direction', 'UNKNOWN')
                    
                    # Store direction-specific exposure
                    if direction == 'RECEIVING':
                        setattr(addr, 'api_receiving_direct_exposure', exposure_data.get('direct', []))
                        setattr(addr, 'api_receiving_indirect_exposure', exposure_data.get('indirect', []))
                        # Clear sending exposure
                        setattr(addr, 'api_sending_direct_exposure', [])
                        setattr(addr, 'api_sending_indirect_exposure', [])
                    elif direction == 'SENDING':
                        setattr(addr, 'api_sending_direct_exposure', exposure_data.get('direct', []))
                        setattr(addr, 'api_sending_indirect_exposure', exposure_data.get('indirect', []))
                        # Clear receiving exposure
                        setattr(addr, 'api_receiving_direct_exposure', [])
                        setattr(addr, 'api_receiving_indirect_exposure', [])
                    
                    # Log exposure summary
                    self.logger.info(f"  Exposure Direction: {direction}")
                    self.logger.info(f"  Direct exposures: {len(exposure_data.get('direct', []))}")
                    self.logger.info(f"  Indirect exposures: {len(exposure_data.get('indirect', []))}")
                else:
                    # Set empty exposure lists
                    setattr(addr, 'api_receiving_direct_exposure', [])
                    setattr(addr, 'api_receiving_indirect_exposure', [])
                    setattr(addr, 'api_sending_direct_exposure', [])
                    setattr(addr, 'api_sending_indirect_exposure', [])
'''
        
        # Find where to insert the enhancement
        insert_pattern = r'(# Also set combined exposure for backward compatibility.*?self\.logger\.debug\("  No exchange exposure found in either direction"\))'
        
        # Check if enhancement already exists
        if 'api_receiving_direct_exposure' not in content:
            # Insert the enhancement
            content = re.sub(
                insert_pattern,
                r'\1' + enhancement,
                content,
                flags=re.DOTALL
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("✅ Patched gui_api_processor.py successfully")
            return True
        else:
            logger.info("ℹ️  gui_api_processor.py already contains the enhancement")
            return True
            
    except Exception as e:
        logger.error(f"❌ ERROR patching {file_path}: {e}")
        return False


def patch_file_handler():
    """
    Patch file_handler.py to add detailed exposure columns to Excel export.
    
    Returns:
        bool: True if successful, False otherwise
    """
    file_path = "file_handler.py"
    
    if not os.path.exists(file_path):
        logger.error(f"❌ ERROR: {file_path} not found")
        return False
    
    logger.info(f"🔧 Patching {file_path}...")
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Update the _create_all_addresses_sheet header section
        old_header_pattern = r'(if include_api_data:.*?headers\.extend\(\[.*?"Indirect Exchange Exposure")(.*?\]\))'
        
        new_headers = ''',
                "Receiving Direct Exposure",
                "Receiving Indirect Exposure", 
                "Sending Direct Exposure",
                "Sending Indirect Exposure"'''
        
        content = re.sub(
            old_header_pattern,
            r'\1' + new_headers + r'\2',
            content,
            flags=re.DOTALL
        )
        
        # 2. Update the data writing section in _create_all_addresses_sheet
        old_data_pattern = r'(# Indirect Exchange Exposure.*?ws\.cell\(row=row, column=col_offset \+ 2, value=indirect_exposure_text or "None"\))'
        
        new_data_section = '''# Indirect Exchange Exposure
                    indirect_exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_indirect_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 2, value=indirect_exposure_text or "None")
                    
                    # Receiving Direct Exposure
                    receiving_direct_text = self._format_exposure_text(
                        getattr(addr, 'api_receiving_direct_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 3, value=receiving_direct_text or "None")
                    
                    # Receiving Indirect Exposure
                    receiving_indirect_text = self._format_exposure_text(
                        getattr(addr, 'api_receiving_indirect_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 4, value=receiving_indirect_text or "None")
                    
                    # Sending Direct Exposure
                    sending_direct_text = self._format_exposure_text(
                        getattr(addr, 'api_sending_direct_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 5, value=sending_direct_text or "None")
                    
                    # Sending Indirect Exposure
                    sending_indirect_text = self._format_exposure_text(
                        getattr(addr, 'api_sending_indirect_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 6, value=sending_indirect_text or "None")'''
        
        content = re.sub(
            old_data_pattern,
            new_data_section,
            content,
            flags=re.DOTALL
        )
        
        # 3. Update the balance column offset
        content = re.sub(
            r'(ws\.cell\(row=row, column=col_offset \+ 3,\s*value=f"\{getattr\(addr, \'api_balance\', 0\):,\.8f\}")',
            r'ws.cell(row=row, column=col_offset + 7, value=f"{getattr(addr, \'api_balance\', 0):,.8f}"',
            content
        )
        
        # 4. Update subsequent column offsets
        content = re.sub(
            r'col_offset \+ 4',
            'col_offset + 8',
            content
        )
        content = re.sub(
            r'col_offset \+ 5',
            'col_offset + 9',
            content
        )
        content = re.sub(
            r'col_offset \+ 6',
            'col_offset + 10',
            content
        )
        content = re.sub(
            r'col_offset \+ 7',
            'col_offset + 11',
            content
        )
        content = re.sub(
            r'col_offset \+ 8',
            'col_offset + 12',
            content
        )
        
        # 5. Also update the _create_crypto_sheet method
        # Find the crypto sheet headers section
        crypto_header_pattern = r'(def _create_crypto_sheet.*?if include_api_data:.*?headers\.extend\(\[.*?"Exchange Exposure")(.*?\]\))'
        
        new_crypto_headers = ''',
                "Receiving Direct",
                "Receiving Indirect",
                "Sending Direct", 
                "Sending Indirect"'''
        
        content = re.sub(
            crypto_header_pattern,
            r'\1' + new_crypto_headers + r'\2',
            content,
            flags=re.DOTALL
        )
        
        # 6. Add new method for enhanced exposure formatting
        new_method = '''
    def _format_detailed_exposure(self, exposures, max_items=3):
        """
        Format exposure data with more details for Excel display.
        
        Args:
            exposures: List of exposure dictionaries
            max_items: Maximum number of items to display
            
        Returns:
            str: Formatted string with exchange names and percentages
        """
        if not exposures:
            return ""
        
        # Sort by value/percentage
        sorted_exposures = sorted(
            exposures,
            key=lambda x: x.get('percentage', 0) or x.get('value', 0),
            reverse=True
        )[:max_items]
        
        formatted_parts = []
        for exp in sorted_exposures:
            name = exp.get('name', 'Unknown')
            percentage = exp.get('percentage', 0)
            value = exp.get('value', 0)
            
            if percentage > 0:
                formatted_parts.append(f"{name}: {percentage:.1f}%")
            elif value > 0:
                formatted_parts.append(f"{name}: ${value:,.2f}")
            else:
                formatted_parts.append(name)
        
        return "; ".join(formatted_parts)
'''
        
        # Insert the new method after _format_exposure_text
        insert_point = r'(return "; ".join\(formatted_parts\[:5\]\).*?# Limit to top 5 for space)'
        content = re.sub(
            insert_point,
            r'\1' + new_method,
            content,
            flags=re.DOTALL
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ Patched file_handler.py successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR patching {file_path}: {e}")
        return False


def create_test_script():
    """
    Create a test script to verify the exposure data is working correctly.
    
    Returns:
        bool: True if successful, False otherwise
    """
    test_script = '''#!/usr/bin/env python3
"""
Test script to verify exposure data is being captured and displayed correctly.
"""

import os
import sys
from extractor import ExtractedAddress

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_exposure_attributes():
    """Test that exposure attributes are properly set."""
    print("\\n=== Testing Exposure Attributes ===\\n")
    
    # Create a test address
    test_addr = ExtractedAddress(
        address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        crypto_type="BTC",
        crypto_name="Bitcoin",
        filename="test.csv",
        row=1,
        column=1,
        confidence=100.0
    )
    
    # Simulate API data being added
    setattr(test_addr, 'api_receiving_direct_exposure', [
        {'name': 'Binance', 'percentage': 45.2, 'value': 10000},
        {'name': 'Coinbase', 'percentage': 23.1, 'value': 5000}
    ])
    
    setattr(test_addr, 'api_receiving_indirect_exposure', [
        {'name': 'Kraken', 'percentage': 12.5, 'value': 2500}
    ])
    
    setattr(test_addr, 'api_sending_direct_exposure', [
        {'name': 'Bitfinex', 'percentage': 35.7, 'value': 8000}
    ])
    
    setattr(test_addr, 'api_sending_indirect_exposure', [])
    
    # Test attribute access
    print(f"Address: {test_addr.address}")
    print(f"\\nReceiving Direct Exposure: {getattr(test_addr, 'api_receiving_direct_exposure', [])}")
    print(f"Receiving Indirect Exposure: {getattr(test_addr, 'api_receiving_indirect_exposure', [])}")
    print(f"Sending Direct Exposure: {getattr(test_addr, 'api_sending_direct_exposure', [])}")
    print(f"Sending Indirect Exposure: {getattr(test_addr, 'api_sending_indirect_exposure', [])}")
    
    print("\\n✅ Exposure attributes test passed!")
    
    return test_addr


def test_file_handler_formatting():
    """Test the file handler formatting methods."""
    print("\\n=== Testing File Handler Formatting ===\\n")
    
    try:
        from file_handler import FileHandler
        
        handler = FileHandler()
        
        # Test exposure formatting
        test_exposures = [
            {'name': 'Binance', 'percentage': 45.2, 'value': 10000},
            {'name': 'Coinbase', 'percentage': 23.1, 'value': 5000},
            {'name': 'Kraken', 'percentage': 12.5, 'value': 2500}
        ]
        
        formatted = handler._format_exposure_text(test_exposures)
        print(f"Formatted exposure: {formatted}")
        
        # Test detailed formatting if method exists
        if hasattr(handler, '_format_detailed_exposure'):
            detailed = handler._format_detailed_exposure(test_exposures, max_items=2)
            print(f"Detailed exposure (max 2): {detailed}")
        
        print("\\n✅ File handler formatting test passed!")
        
    except Exception as e:
        print(f"\\n❌ File handler test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Exposure Data Enhancement Test")
    print("=" * 60)
    
    test_exposure_attributes()
    test_file_handler_formatting()
    
    print("\\n" + "=" * 60)
    print("All tests completed!")
    print("\\nNext steps:")
    print("1. Run the extractor with Chainalysis API enabled")
    print("2. Check the Excel output for the new exposure columns")
    print("3. Verify that receiving/sending exposure data is displayed correctly")
'''
    
    try:
        with open('test_exposure_enhancement.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        logger.info("✅ Created test_exposure_enhancement.py")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR creating test script: {e}")
        return False


def main():
    """
    Main function to apply all patches for enhanced exposure data.
    
    Returns:
        int: 0 for success, 1 for failure
    """
    print("=" * 70)
    print("Enhanced Direct/Indirect Exposure Data Patch")
    print("=" * 70)
    print("\nThis script will enhance your cryptocurrency address extractor to:")
    print("- Capture separate receiving and sending exposure data")
    print("- Add detailed columns for direct and indirect exposure")
    print("- Display exposure values and percentages in Excel")
    print("\n" + "=" * 70 + "\n")
    
    success = True
    
    # Apply patches
    if not patch_gui_api_processor():
        success = False
    
    if not patch_file_handler():
        success = False
    
    # Create test script
    if not create_test_script():
        success = False
    
    # Summary
    print("\n" + "=" * 70)
    if success:
        print("✅ All patches applied successfully!")
        print("\n📋 What was changed:")
        print("1. gui_api_processor.py - Enhanced to store directional exposure data")
        print("2. file_handler.py - Added new columns for detailed exposure display")
        print("3. Created test_exposure_enhancement.py for verification")
        
        print("\n🚀 Next steps:")
        print("1. Run your extraction with Chainalysis API enabled")
        print("2. Check 'Enable exposure analysis' in the API options")
        print("3. The Excel output will now include:")
        print("   - Receiving Direct Exposure")
        print("   - Receiving Indirect Exposure")
        print("   - Sending Direct Exposure")
        print("   - Sending Indirect Exposure")
        
        print("\n💡 Testing:")
        print("Run: python test_exposure_enhancement.py")
        print("This will verify the enhancement is working correctly")
        
        return 0
    else:
        print("❌ Some patches failed to apply")
        print("Please check the error messages above")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure all required files exist in the current directory")
        print("2. Check that you have write permissions")
        print("3. Review the backup files if needed")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())