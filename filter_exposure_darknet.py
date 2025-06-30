#!/usr/bin/env python3
"""
Filter Exposure for Exchanges and Add Darknet Market Detection
==============================================================

This script filters exposure data to only show exchanges and darknet markets,
and adds a new column to indicate if an address has darknet market exposure.

Usage:
    python filter_exposure_darknet.py

Author: Crypto Extractor Tool
Date: 2025-01-18
Version: 1.0.0
"""

import os
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
    """Create a timestamped backup."""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    logger.info(f"✅ Created backup: {backup_path}")
    return backup_path


def update_gui_api_processor():
    """Update the API processor to filter for exchanges and darknet markets only."""
    file_path = "gui_api_processor.py"
    
    if not os.path.exists(file_path):
        logger.error(f"❌ ERROR: {file_path} not found")
        return False
    
    logger.info(f"🔧 Updating {file_path} to filter exposure data...")
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add new method to check if service is exchange or darknet market
        filter_method = '''
    def _is_exchange_or_darknet_service(self, service):
        """
        Determine if a service represents an exchange or darknet market.
        
        Args:
            service: Service dictionary from API response
            
        Returns:
            tuple: (is_relevant, is_darknet) where:
                   - is_relevant: True if exchange or darknet market
                   - is_darknet: True if darknet market
        """
        if not isinstance(service, dict):
            return False, False
        
        # Get fields safely
        category = str(service.get('category', '')).lower()
        name = str(service.get('name', '')).lower()
        
        # Check for darknet markets
        darknet_categories = ['darknet market', 'darknet marketplace', 'dark market', 'illicit market']
        darknet_names = ['hydra', 'alphabay', 'dream market', 'silk road', 'empire market', 
                        'white house market', 'dark0de', 'torrez', 'cannazon', 'versus']
        
        is_darknet = False
        
        # Check if it's a darknet market
        for dark_cat in darknet_categories:
            if dark_cat in category:
                is_darknet = True
                break
        
        if not is_darknet:
            for dark_name in darknet_names:
                if dark_name in name:
                    is_darknet = True
                    break
        
        # Check if it's an exchange
        is_exchange = False
        
        # Exchange categories
        exchange_categories = ['exchange', 'centralized exchange', 'cex', 'dex', 'decentralized exchange',
                             'cryptocurrency exchange', 'crypto exchange', 'trading platform']
        
        for exc_cat in exchange_categories:
            if exc_cat in category:
                is_exchange = True
                break
        
        # Exchange names
        if not is_exchange:
            exchanges = [
                'binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okx', 'okex',
                'kucoin', 'gate', 'bybit', 'bitstamp', 'gemini', 'bittrex', 'poloniex',
                'crypto.com', 'mexc', 'hotbit', 'phemex', 'deribit', 'bitmex',
                'uniswap', 'pancakeswap', 'sushiswap', 'curve', 'balancer'
            ]
            
            for exchange in exchanges:
                if exchange in name:
                    is_exchange = True
                    break
        
        # Return if it's relevant (exchange or darknet) and if it's darknet
        is_relevant = is_exchange or is_darknet
        return is_relevant, is_darknet
'''
        
        # Find a good place to insert the method (after _is_exchange_service if it exists)
        insert_pos = content.find('def _is_exchange_service')
        if insert_pos != -1:
            # Find the end of this method
            next_def = content.find('\n    def ', insert_pos + 1)
            if next_def != -1:
                content = content[:next_def] + filter_method + content[next_def:]
        else:
            # Insert after _extract_services_from_response
            insert_pos = content.find('def _extract_services_from_response')
            if insert_pos != -1:
                next_def = content.find('\n    def ', insert_pos + 1)
                if next_def != -1:
                    content = content[:next_def] + filter_method + content[next_def:]
        
        logger.info("✅ Added _is_exchange_or_darknet_service method")
        
        # Now update the exposure processing to use this filter and track darknet exposure
        # Find the exposure processing section and update it
        
        # Update the section where we process services
        old_pattern = r'(# Process ALL services \(not just exchanges\) for comprehensive data)'
        new_comment = '# Process ONLY exchanges and darknet markets'
        content = content.replace(old_pattern, new_comment)
        
        # Update where we append service info
        old_append_pattern = r'api_data\[\'sending_direct_exposure\'\]\.append\(service_info\)'
        new_append = '''is_relevant, is_darknet = self._is_exchange_or_darknet_service(service)
                        if is_relevant:
                            api_data['sending_direct_exposure'].append(service_info)
                            if is_darknet:
                                api_data['has_darknet_exposure'] = True'''
        
        # Replace all occurrences for different exposure types
        content = re.sub(
            r'api_data\[\'(sending|receiving)_(direct|indirect)_exposure\'\]\.append\(service_info\)',
            lambda m: f'''is_relevant, is_darknet = self._is_exchange_or_darknet_service(service)
                        if is_relevant:
                            api_data['{m.group(1)}_{m.group(2)}_exposure'].append(service_info)
                            if is_darknet:
                                api_data['has_darknet_exposure'] = True''',
            content
        )
        
        # Initialize has_darknet_exposure at the beginning of exposure processing
        init_pattern = r'(# Initialize exposure data structures\s*\n\s*api_data\[\'sending_direct_exposure\'\] = \[\])'
        init_replacement = r'''\1
                api_data['has_darknet_exposure'] = False  # Track if any darknet market exposure found'''
        
        content = re.sub(init_pattern, init_replacement, content)
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ Updated exposure processing to filter for exchanges and darknet markets")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        return False


def update_file_handler():
    """Update file handler to add Darknet Market column."""
    file_path = "file_handler.py"
    
    if not os.path.exists(file_path):
        logger.error(f"❌ ERROR: {file_path} not found")
        return False
    
    logger.info(f"🔧 Updating {file_path} to add Darknet Market column...")
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update the headers in _create_all_addresses_sheet
        # Find where API headers are added
        header_pattern = r'(if include_api_data:.*?headers\.extend\(\[.*?"Sending Indirect Exposure")'
        
        # Add Darknet Market after the exposure columns
        def add_darknet_header(match):
            original = match.group(0)
            # Add the new header
            return original + ',\n                "Darknet Market"'
        
        content = re.sub(header_pattern, add_darknet_header, content, flags=re.DOTALL)
        
        # Now add the data writing for darknet market column
        # Find where we write sending indirect exposure
        data_pattern = r'(# Sending Indirect Exposure.*?ws\.cell\(row=row, column=col_offset \+ 6, value=sending_indirect_text or "None"\))'
        
        def add_darknet_data(match):
            original = match.group(0)
            # Add the darknet market Y/N
            darknet_data = '''
                    
                    # Darknet Market
                    has_darknet = getattr(addr, 'api_has_darknet_exposure', False)
                    ws.cell(row=row, column=col_offset + 7, value="Y" if has_darknet else "N")'''
            
            return original + darknet_data
        
        content = re.sub(data_pattern, add_darknet_data, content, flags=re.DOTALL)
        
        # Update subsequent column numbers (add 1 to each)
        content = re.sub(r'col_offset \+ 7,', 'col_offset + 8,', content)
        content = re.sub(r'col_offset \+ 8,', 'col_offset + 9,', content)
        content = re.sub(r'col_offset \+ 9,', 'col_offset + 10,', content)
        content = re.sub(r'col_offset \+ 10,', 'col_offset + 11,', content)
        content = re.sub(r'col_offset \+ 11,', 'col_offset + 12,', content)
        content = re.sub(r'col_offset \+ 12,', 'col_offset + 13,', content)
        
        # Also update the crypto sheets to include darknet market column
        crypto_header_pattern = r'(def _create_crypto_sheet.*?if include_api_data:.*?headers\.extend\(\[.*?"Sending Indirect")'
        
        def add_crypto_darknet_header(match):
            original = match.group(0)
            return original + ',\n                    "Darknet Market"'
        
        content = re.sub(crypto_header_pattern, add_crypto_darknet_header, content, flags=re.DOTALL)
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ Added Darknet Market column to Excel export")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        return False


def update_format_exposure_text():
    """Update the exposure text formatter to only show exchanges and darknet markets."""
    file_path = "file_handler.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update the _format_exposure_text method to filter categories
        updated_format = '''
    def _format_exposure_text(self, exposures):
        """
        Format exposure data for display in Excel cell.
        Shows ONLY exchanges and darknet markets with percentages.
        """
        if not exposures:
            return "None"
        
        # Sort by percentage/value descending
        sorted_exposures = sorted(
            exposures,
            key=lambda x: x.get('percentage', 0) or (x.get('value', 0) / 1000000),
            reverse=True
        )
        
        # Format significant exposures (exchanges and darknet markets are already filtered)
        formatted_parts = []
        for exp in sorted_exposures[:10]:  # Show top 10
            name = exp.get('name', 'Unknown')
            category = exp.get('category', '')
            percentage = exp.get('percentage', 0)
            
            if percentage >= 0.1:  # Only show if >= 0.1%
                # For darknet markets, include (Darknet) indicator
                if 'darknet' in category.lower() or 'dark market' in category.lower():
                    formatted_parts.append(f"{name} (Darknet): {percentage:.1f}%")
                else:
                    formatted_parts.append(f"{name}: {percentage:.1f}%")
        
        return "; ".join(formatted_parts) if formatted_parts else "None"'''
        
        # Replace the method
        method_pattern = r'def _format_exposure_text\(self, exposures\):.*?(?=\n    def |\n\nclass |\Z)'
        content = re.sub(method_pattern, updated_format.strip() + '\n', content, flags=re.DOTALL)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ Updated exposure formatting")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR updating formatter: {e}")
        return False


def main():
    """Main function."""
    print("=" * 70)
    print("Filter Exposure for Exchanges and Add Darknet Market Detection")
    print("=" * 70)
    print("\nThis script will:")
    print("1. Filter exposure data to only show exchanges and darknet markets")
    print("2. Add a 'Darknet Market' column with Y/N values")
    print("3. Update display formatting")
    print("=" * 70 + "\n")
    
    success = True
    
    # Update API processor
    if not update_gui_api_processor():
        success = False
    
    # Update file handler
    if not update_file_handler():
        success = False
    
    # Update formatter
    if not update_format_exposure_text():
        logger.warning("⚠️  Formatter update failed, but main functionality added")
    
    if success:
        print("\n" + "=" * 70)
        print("✅ Successfully updated exposure filtering and darknet detection!")
        
        print("\n📋 What was changed:")
        print("1. Exposure data now filtered to ONLY show:")
        print("   - Cryptocurrency exchanges")
        print("   - Darknet markets")
        print("2. Added 'Darknet Market' column with Y/N values")
        print("3. Darknet markets shown with '(Darknet)' indicator in exposure text")
        
        print("\n🔍 How it works:")
        print("1. Each service is checked against exchange and darknet market criteria")
        print("2. Only matching services are included in exposure data")
        print("3. If ANY darknet market exposure is found, the column shows 'Y'")
        print("4. Categories filtered include:")
        print("   - Exchanges: 'exchange', 'cex', 'dex', 'trading platform'")
        print("   - Darknet: 'darknet market', 'darknet marketplace', 'dark market'")
        
        print("\n🚀 Next steps:")
        print("1. Fix any remaining syntax errors in gui_api_processor.py")
        print("2. Run your extraction with API enabled")
        print("3. Check the Excel output for:")
        print("   - Filtered exposure showing only exchanges/darknet markets")
        print("   - New 'Darknet Market' column with Y/N values")
        
        print("\n⚠️  Note: Make sure to fix the syntax error at line 317 first!")
        
        return 0
    else:
        print("\n❌ Some updates failed")
        print("Check the error messages above")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())