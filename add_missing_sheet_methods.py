#!/usr/bin/env python3
"""
Add Missing Sheet Creation Methods
==================================

This script adds the missing sheet creation methods to file_handler.py
including _create_duplicate_analysis_sheet and others.

Usage:
    python add_missing_sheet_methods.py

Author: Crypto Extractor Tool
Date: 2025-01-18
Version: 1.0.0
"""

import os
import shutil
from datetime import datetime


def backup_file(filepath):
    """Create a timestamped backup."""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path


def add_missing_methods():
    """Add the missing sheet creation methods."""
    file_path = "file_handler.py"
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: {file_path} not found")
        return False
    
    print(f"🔧 Adding missing methods to {file_path}...")
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if methods already exist
        if '_create_duplicate_analysis_sheet' in content:
            print("ℹ️  _create_duplicate_analysis_sheet already exists")
            return True
        
        # Find where to insert the new methods (after the last method definition)
        # Look for the end of the class or before the last method
        import re
        
        # Find the last method in the FileHandler class
        last_method_pattern = r'(\n    def [^(]+\([^)]*\)[^{]*?(?=\n(?:class|\Z)))'
        matches = list(re.finditer(last_method_pattern, content, re.DOTALL))
        
        if not matches:
            # Try simpler pattern
            insert_position = content.rfind('\n    def ')
            if insert_position == -1:
                print("❌ Could not find appropriate insertion point")
                return False
            # Find the end of this method
            insert_position = content.find('\n\n', insert_position) + 2
        else:
            # Insert after the last match
            insert_position = matches[-1].end()
        
        # Methods to add
        new_methods = '''
    def _create_duplicate_analysis_sheet(self, wb: Workbook, addresses: List[ExtractedAddress]) -> None:
        """
        Create duplicate analysis sheet showing all duplicate addresses.
        
        Args:
            wb: Workbook object
            addresses: List of extracted addresses
            
        Raises:
            Exception: If sheet creation fails
        """
        try:
            ws = wb.create_sheet("Duplicate Analysis")
            self.logger.info("Creating 'Duplicate Analysis' sheet")
            
            # Headers
            headers = [
                "Address", "Crypto", "Total Occurrences", 
                "Files", "First Seen", "Last Seen"
            ]
            
            # Style headers
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="FF4B4B", end_color="FF4B4B", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Group duplicates
            address_groups = defaultdict(list)
            for addr in addresses:
                if addr.is_duplicate:
                    address_groups[addr.address].append(addr)
            
            # Write duplicate data
            row = 2
            for address, occurrences in sorted(address_groups.items()):
                if len(occurrences) > 1:  # Only show actual duplicates
                    ws.cell(row=row, column=1, value=address)
                    ws.cell(row=row, column=2, value=occurrences[0].crypto_name)
                    ws.cell(row=row, column=3, value=len(occurrences))
                    
                    # Unique files
                    files = list(set(addr.filename for addr in occurrences))
                    ws.cell(row=row, column=4, value=", ".join(files[:3]))  # Show first 3
                    
                    # First and last seen (by row number)
                    first_row = min(addr.row for addr in occurrences)
                    last_row = max(addr.row for addr in occurrences)
                    ws.cell(row=row, column=5, value=f"Row {first_row}")
                    ws.cell(row=row, column=6, value=f"Row {last_row}")
                    
                    row += 1
            
            # Auto-fit columns
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            self.logger.info(f"✓ Created Duplicate Analysis sheet with {row-2} duplicate groups")
            
        except Exception as e:
            self.logger.error(f"Failed to create duplicate analysis sheet: {str(e)}")
            raise

    def _create_crypto_sheet(self, wb: Workbook, crypto_name: str, addresses: List[ExtractedAddress], 
                           include_api_data: bool = False) -> None:
        """
        Create sheet for a specific cryptocurrency with unique addresses only.
        
        Args:
            wb: Workbook object
            crypto_name: Name of the cryptocurrency
            addresses: List of addresses for this crypto
            include_api_data: Whether to include API data columns
            
        Raises:
            Exception: If sheet creation fails
        """
        try:
            # Remove duplicates - keep only unique addresses
            seen = set()
            unique_addresses = []
            for addr in addresses:
                if addr.address not in seen:
                    seen.add(addr.address)
                    unique_addresses.append(addr)
            
            ws = wb.create_sheet(crypto_name[:31])  # Excel sheet name limit
            self.logger.info(f"Creating '{crypto_name}' sheet with {len(unique_addresses)} unique addresses")
            
            # Headers
            headers = ["Address", "Source File", "Row", "Column", "Confidence"]
            
            if include_api_data:
                headers.extend([
                    "Entity Name",
                    "Exchange Exposure",
                    "Receiving Direct",
                    "Receiving Indirect",
                    "Sending Direct",
                    "Sending Indirect",
                    "Balance",
                    "Total Received",
                    "Total Sent"
                ])
            
            # Write headers
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Write data
            for row, addr in enumerate(unique_addresses, 2):
                ws.cell(row=row, column=1, value=addr.address)
                ws.cell(row=row, column=2, value=addr.filename)
                ws.cell(row=row, column=3, value=addr.row)
                ws.cell(row=row, column=4, value=addr.column)
                ws.cell(row=row, column=5, value=f"{addr.confidence:.1f}%")
                
                if include_api_data:
                    col_offset = 5
                    
                    # Entity Name
                    entity_name = getattr(addr, 'api_entity_name', getattr(addr, 'api_cluster_name', ''))
                    ws.cell(row=row, column=col_offset + 1, value=entity_name)
                    
                    # Exchange Exposure (combined)
                    exposure_text = self._format_exposure_text(
                        getattr(addr, 'api_exchange_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 2, value=exposure_text or "None")
                    
                    # Receiving Direct
                    receiving_direct = self._format_exposure_text(
                        getattr(addr, 'api_receiving_direct_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 3, value=receiving_direct or "None")
                    
                    # Receiving Indirect
                    receiving_indirect = self._format_exposure_text(
                        getattr(addr, 'api_receiving_indirect_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 4, value=receiving_indirect or "None")
                    
                    # Sending Direct
                    sending_direct = self._format_exposure_text(
                        getattr(addr, 'api_sending_direct_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 5, value=sending_direct or "None")
                    
                    # Sending Indirect
                    sending_indirect = self._format_exposure_text(
                        getattr(addr, 'api_sending_indirect_exposure', [])
                    )
                    ws.cell(row=row, column=col_offset + 6, value=sending_indirect or "None")
                    
                    # Other API data
                    ws.cell(row=row, column=col_offset + 7, 
                           value=f"{getattr(addr, 'api_balance', 0):,.8f}")
                    ws.cell(row=row, column=col_offset + 8, 
                           value=f"{getattr(addr, 'api_total_received', 0):,.8f}")
                    ws.cell(row=row, column=col_offset + 9, 
                           value=f"{getattr(addr, 'api_total_sent', 0):,.8f}")
            
            # Auto-fit columns
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            self.logger.info(f"✓ Created {crypto_name} sheet successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create {crypto_name} sheet: {str(e)}")
            raise
'''
        
        # Insert the new methods
        content = content[:insert_position] + new_methods + content[insert_position:]
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added missing methods successfully")
        
        # Verify syntax
        try:
            compile(content, file_path, 'exec')
            print("✅ Syntax check passed!")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def verify_methods():
    """Verify all required methods exist."""
    print("\n🔍 Verifying required methods...")
    
    required_methods = [
        '_create_summary_sheet',
        '_create_all_addresses_sheet', 
        '_create_duplicate_analysis_sheet',
        '_create_crypto_sheet',
        '_format_exposure_text'
    ]
    
    try:
        with open('file_handler.py', 'r') as f:
            content = f.read()
        
        missing = []
        for method in required_methods:
            if f'def {method}' not in content:
                missing.append(method)
        
        if missing:
            print("❌ Missing methods:")
            for m in missing:
                print(f"   - {m}")
            return False
        else:
            print("✅ All required methods are present!")
            return True
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def main():
    """Main function."""
    print("=" * 70)
    print("Add Missing Sheet Creation Methods")
    print("=" * 70)
    print("\nThis script adds the missing sheet creation methods")
    print("=" * 70 + "\n")
    
    if add_missing_methods():
        verify_methods()
        
        print("\n" + "=" * 70)
        print("✅ Methods added successfully!")
        print("\n🚀 Next steps:")
        print("1. Run your application: python main.py")
        print("2. The extraction should now complete successfully")
        print("3. Your Excel file will include:")
        print("   - Summary sheet")
        print("   - All Addresses sheet with exposure data")
        print("   - Duplicate Analysis sheet")
        print("   - Individual crypto sheets with unique addresses")
        
        return 0
    else:
        print("\n❌ Failed to add methods")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())