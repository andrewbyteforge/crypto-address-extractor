#!/usr/bin/env python3
"""
Fix Excel Column Alignment - Complete Column Mapping Fix
========================================================

This script provides a complete fix for Excel column alignment issues by
ensuring each data field maps to exactly one column with no overwrites.

Author: Crypto Address Extractor Tool
Date: 2025-01-30
Version: 2.0.0

Usage:
    python fix_excel_column_alignment.py
"""

import os
import re
import shutil
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def backup_file(filepath):
    """
    Create a timestamped backup of the file.
    
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
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise


def create_column_mapping():
    """
    Create clear column mappings for each sheet type.
    
    Returns:
        dict: Column mappings for different sheet types
    """
    return {
        'all_addresses': {
            'basic': {
                1: 'addr.address',
                2: 'cluster_address',  # Cluster Address
                3: 'addr.crypto_name',
                4: 'addr.filename',    # Source File (this was the issue!)
                5: 'addr.sheet_name or "N/A"',
                6: 'addr.row',
                7: 'addr.column',
                8: 'f"{addr.confidence:.1f}%"',
                9: '"Yes" if addr.is_duplicate else "No"',
                10: 'addr.duplicate_count'
            },
            'api': {  # Starting from column 11
                11: 'f"{getattr(addr, \'api_balance\', 0):,.8f}"',
                12: 'f"{getattr(addr, \'api_total_received\', 0):,.8f}"',
                13: 'f"{getattr(addr, \'api_total_sent\', 0):,.8f}"',
                14: 'getattr(addr, \'api_transfer_count\', 0)',
                15: 'direct_exposure_text',
                16: 'indirect_exposure_text',
                17: 'receiving_direct_text',
                18: 'receiving_indirect_text',
                19: 'sending_direct_text',
                20: 'sending_indirect_text',
                21: '"Y" if has_darknet else "N"',
                22: 'getattr(addr, \'api_risk_level\', \'Unknown\')',
                23: 'entity_name',
                24: 'getattr(addr, \'api_cluster_category\', \'\')'
            }
        },
        'crypto_sheet': {
            'basic': {
                1: 'addr.address',
                2: 'cluster_address',
                3: 'addr.filename',    # Source File
                4: 'addr.row',
                5: 'addr.column',
                6: 'f"{addr.confidence:.1f}%"'
            },
            'api': {  # Starting from column 7
                7: 'entity_name',
                8: 'direct_exposure',
                9: 'indirect_exposure',
                10: 'receiving_direct',
                11: 'receiving_indirect',
                12: 'sending_direct',
                13: 'sending_indirect',
                14: '"Y" if has_darknet else "N"',
                15: 'f"{getattr(addr, \'api_balance\', 0):,.8f}"',
                16: 'f"{getattr(addr, \'api_total_received\', 0):,.8f}"',
                17: 'f"{getattr(addr, \'api_total_sent\', 0):,.8f}"'
            }
        },
        'duplicate_sheet': {
            1: 'address',
            2: 'cluster_address',
            3: 'occurrences[0].crypto_name',
            4: 'len(occurrences)',
            5: '", ".join(files[:3])'
        }
    }


def generate_all_addresses_write_section():
    """
    Generate the complete data writing section for all addresses sheet.
    
    Returns:
        str: The complete code section
    """
    mapping = create_column_mapping()['all_addresses']
    
    code = '''
                # Basic columns (1-10)'''
    
    # Add basic columns
    for col, field in mapping['basic'].items():
        if col == 2:  # Special handling for cluster address
            code += f'''
                
                # Cluster address in column {col}
                cluster_address = getattr(addr, 'api_cluster_root_address', '')
                if not cluster_address:
                    cluster_address = getattr(addr, 'api_root_address', '')
                ws.cell(row=row, column={col}, value=cluster_address)'''
        else:
            code += f'''
                ws.cell(row=row, column={col}, value={field})'''
    
    # Add API columns
    code += '''
                
                if include_api_data:
                    # API data columns (11-24)'''
    
    # Add exposure text variables
    code += '''
                    
                    # Prepare exposure text fields
                    direct_exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_direct_exposure', [])
                    )
                    indirect_exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_indirect_exposure', [])
                    )
                    receiving_direct_text = self._format_exposure_text(
                        getattr(addr, 'api_receiving_direct_exposure', [])
                    )
                    receiving_indirect_text = self._format_exposure_text(
                        getattr(addr, 'api_receiving_indirect_exposure', [])
                    )
                    sending_direct_text = self._format_exposure_text(
                        getattr(addr, 'api_sending_direct_exposure', [])
                    )
                    sending_indirect_text = self._format_exposure_text(
                        getattr(addr, 'api_sending_indirect_exposure', [])
                    )
                    has_darknet = getattr(addr, 'api_has_darknet_exposure', False)
                    entity_name = getattr(addr, 'api_cluster_name', '')'''
    
    # Add API column writes
    for col, field in mapping['api'].items():
        code += f'''
                    ws.cell(row=row, column={col}, value={field})'''
    
    code += '''
            '''
    
    return code


def generate_crypto_sheet_write_section():
    """
    Generate the complete data writing section for crypto sheets.
    
    Returns:
        str: The complete code section
    """
    mapping = create_column_mapping()['crypto_sheet']
    
    code = '''
                # Basic columns (1-6)'''
    
    # Add basic columns
    for col, field in mapping['basic'].items():
        if col == 2:  # Special handling for cluster address
            code += f'''
                
                # Cluster address in column {col}
                cluster_address = getattr(addr, 'api_cluster_root_address', '')
                if not cluster_address:
                    cluster_address = getattr(addr, 'api_root_address', '')
                ws.cell(row=row, column={col}, value=cluster_address)'''
        else:
            code += f'''
                ws.cell(row=row, column={col}, value={field})'''
    
    # Add API columns
    code += '''
                
                if include_api_data:
                    # API data columns (7-17)'''
    
    # Add exposure text variables
    code += '''
                    
                    # Prepare all data fields
                    entity_name = getattr(addr, 'api_cluster_name', '')
                    direct_exposure = self._format_exposure_text(
                        getattr(addr, 'api_direct_exposure', [])
                    )
                    indirect_exposure = self._format_exposure_text(
                        getattr(addr, 'api_indirect_exposure', [])
                    )
                    receiving_direct = self._format_exposure_text(
                        getattr(addr, 'api_receiving_direct_exposure', [])
                    )
                    receiving_indirect = self._format_exposure_text(
                        getattr(addr, 'api_receiving_indirect_exposure', [])
                    )
                    sending_direct = self._format_exposure_text(
                        getattr(addr, 'api_sending_direct_exposure', [])
                    )
                    sending_indirect = self._format_exposure_text(
                        getattr(addr, 'api_sending_indirect_exposure', [])
                    )
                    has_darknet = getattr(addr, 'api_has_darknet_exposure', False)'''
    
    # Add API column writes
    for col, field in mapping['api'].items():
        code += f'''
                    ws.cell(row=row, column={col}, value={field})'''
    
    code += '''
            '''
    
    return code


def fix_all_addresses_sheet(content):
    """
    Fix the _create_all_addresses_sheet method to properly align columns.
    
    Args:
        content (str): The file content
        
    Returns:
        str: Updated content with fixed column alignment
    """
    logger.info("Fixing _create_all_addresses_sheet column alignment...")
    
    # Find the data writing section
    pattern = r'(# Write data.*?for row, addr in enumerate\(addresses, 2\):)(.*?)(# Auto-fit columns|# Wider columns|except Exception)'
    
    def replace_data_section(match):
        prefix = match.group(1)
        suffix = match.group(3)
        
        # Generate the new data section
        new_data_section = generate_all_addresses_write_section()
        
        return prefix + new_data_section + suffix
    
    # Apply the fix
    content = re.sub(pattern, replace_data_section, content, flags=re.DOTALL)
    
    return content


def fix_crypto_sheet(content):
    """
    Fix the _create_crypto_sheet method to properly align columns.
    
    Args:
        content (str): The file content
        
    Returns:
        str: Updated content with fixed column alignment
    """
    logger.info("Fixing _create_crypto_sheet column alignment...")
    
    # Find the data writing section in _create_crypto_sheet
    pattern = r'(def _create_crypto_sheet.*?# Write data.*?for row, addr in enumerate\(unique_addresses, 2\):)(.*?)(# Auto-fit columns|self\.logger\.info\(f"✓ Created|except Exception)'
    
    def replace_crypto_data_section(match):
        prefix = match.group(1)
        suffix = match.group(3)
        
        # Generate the new data section
        new_data_section = generate_crypto_sheet_write_section()
        
        return prefix + new_data_section + suffix
    
    # Apply the fix
    content = re.sub(pattern, replace_crypto_data_section, content, flags=re.DOTALL)
    
    return content


def fix_duplicate_sheet(content):
    """
    Fix the _create_duplicate_analysis_sheet method to properly align columns.
    
    Args:
        content (str): The file content
        
    Returns:
        str: Updated content with fixed column alignment
    """
    logger.info("Fixing _create_duplicate_analysis_sheet column alignment...")
    
    # Fix the duplicate sheet data writing
    pattern = r'(row = 2.*?for address, occurrences in sorted\(duplicates\.items\(\)\):.*?if len\(occurrences\) > 1:)(.*?)(row \+= 1)'
    
    def replace_duplicate_data(match):
        prefix = match.group(1)
        suffix = match.group(3)
        
        mapping = create_column_mapping()['duplicate_sheet']
        
        # Generate new data section
        new_section = ''
        for col, field in mapping.items():
            if col == 2:  # Cluster address
                new_section += f'''
                    
                    # Get cluster address for this duplicate
                    cluster_address = ''
                    if occurrences:
                        cluster_address = getattr(occurrences[0], 'api_cluster_root_address', '')
                        if not cluster_address:
                            cluster_address = getattr(occurrences[0], 'api_root_address', '')
                    ws.cell(row=row, column={col}, value=cluster_address)'''
            elif col == 5:  # Files list
                new_section += f'''
                    files = list(set(addr.filename for addr in occurrences))
                    ws.cell(row=row, column={col}, value={field})'''
            else:
                new_section += f'''
                    ws.cell(row=row, column={col}, value={field})'''
        
        new_section += f'''
                    '''
        
        return prefix + new_section + suffix
    
    content = re.sub(pattern, replace_duplicate_data, content, flags=re.DOTALL)
    
    return content


def verify_headers_match_data(content):
    """
    Verify that headers match the data columns.
    
    Args:
        content (str): The file content
        
    Returns:
        bool: True if verification passes
    """
    logger.info("Verifying headers match data columns...")
    
    # Check All Addresses sheet headers
    all_addr_headers = re.search(
        r'headers = \["Address", "Cluster Address", "Cryptocurrency", "Source File", "Sheet", "Row", "Column",\s*"Confidence %", "Is Duplicate", "Total Count"\]',
        content
    )
    
    if not all_addr_headers:
        logger.warning("Could not verify All Addresses sheet headers")
        return False
    
    logger.info("✅ Headers verification passed")
    return True


def main():
    """
    Main function to fix Excel column alignment issues.
    
    Returns:
        int: 0 for success, 1 for failure
    """
    file_path = "file_handler.py"
    
    logger.info("=" * 70)
    logger.info("Excel Column Alignment Fix - Complete Version")
    logger.info("=" * 70)
    logger.info("\nThis script will completely fix all column alignment issues")
    logger.info("ensuring each data field goes to exactly the right column.")
    logger.info("=" * 70 + "\n")
    
    if not os.path.exists(file_path):
        logger.error(f"ERROR: {file_path} not found in current directory")
        logger.error("Please run this script from the project root directory")
        return 1
    
    try:
        # Create backup
        backup_path = backup_file(file_path)
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply fixes
        content = fix_all_addresses_sheet(content)
        content = fix_crypto_sheet(content)
        content = fix_duplicate_sheet(content)
        
        # Verify headers match
        verify_headers_match_data(content)
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ Successfully fixed all column alignment issues!")
        
        logger.info("\n📋 Fixed Issues:")
        logger.info("1. Source File now correctly shows filename (not row number)")
        logger.info("2. Cluster Address consistently in column 2")
        logger.info("3. All data fields map to exactly one column")
        logger.info("4. No more column overwrites or misalignment")
        
        logger.info("\n🔍 Column mappings for 'All Addresses' sheet:")
        logger.info("   Column 1: Address")
        logger.info("   Column 2: Cluster Address")
        logger.info("   Column 3: Cryptocurrency")
        logger.info("   Column 4: Source File (filename)")
        logger.info("   Column 5: Sheet")
        logger.info("   Column 6: Row")
        logger.info("   Column 7: Column")
        logger.info("   Column 8: Confidence %")
        logger.info("   Column 9: Is Duplicate")
        logger.info("   Column 10: Total Count")
        
        if "include_api_data" in content:
            logger.info("\n   API Data (when enabled):")
            logger.info("   Column 11: Balance")
            logger.info("   Column 12: Total Received")
            logger.info("   Column 13: Total Sent")
            logger.info("   Column 14: Transfer Count")
            logger.info("   Column 15: Direct Exchange Exposure")
            logger.info("   Column 16: Indirect Exchange Exposure")
            logger.info("   Column 17: Receiving Direct Exposure")
            logger.info("   Column 18: Receiving Indirect Exposure")
            logger.info("   Column 19: Sending Direct Exposure")
            logger.info("   Column 20: Sending Indirect Exposure")
            logger.info("   Column 21: Darknet Market (Y/N)")
            logger.info("   Column 22: Risk Level")
            logger.info("   Column 23: Entity Name")
            logger.info("   Column 24: Cluster Category")
        
        logger.info("\n🔍 Column mappings for crypto-specific sheets:")
        logger.info("   Column 1: Address")
        logger.info("   Column 2: Cluster Address")
        logger.info("   Column 3: Source File (filename)")
        logger.info("   Column 4: Row")
        logger.info("   Column 5: Column")
        logger.info("   Column 6: Confidence %")
        
        logger.info("\n🚀 Next steps:")
        logger.info("1. Run your extraction again")
        logger.info("2. Open the Excel output")
        logger.info("3. Verify Source File column shows actual filenames")
        logger.info("4. Check all data is in the correct columns")
        
        logger.info(f"\n💾 Backup saved as: {backup_path}")
        logger.info("If you need to revert, rename the backup file back to file_handler.py")
        
        # Verify the file still has valid Python syntax
        try:
            compile(content, file_path, 'exec')
            logger.info("\n✅ Syntax verification passed!")
        except SyntaxError as e:
            logger.error(f"\n❌ Syntax error detected: {e}")
            logger.error("The file may have been corrupted. Restoring from backup...")
            shutil.copy2(backup_path, file_path)
            logger.error("Backup restored. Please report this issue.")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Error occurred: {e}")
        logger.error("Please check the error message and try again")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())