#!/usr/bin/env python3
"""
Restore Complete FileHandler
============================

This script checks which methods are missing from your FileHandler class
and explains how to restore them properly.

Usage:
    python restore_file_handler.py

Author: Crypto Extractor Tool
Date: 2025-01-18
Version: 1.0.0
"""

import os
import re
from datetime import datetime


def analyze_file_handler():
    """Analyze the current state of file_handler.py."""
    file_path = "file_handler.py"
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: {file_path} not found")
        return None
    
    print("🔍 Analyzing file_handler.py...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Required methods for FileHandler
    required_methods = [
        '_create_summary_sheet',
        '_create_all_addresses_sheet',
        '_create_duplicate_analysis_sheet',
        '_create_crypto_sheet',
        '_format_exposure_text',
        'write_to_excel',
        'save_to_excel',
        'read_csv',
        'read_excel'
    ]
    
    # Check which methods exist
    existing_methods = []
    missing_methods = []
    
    for method in required_methods:
        pattern = rf'def {method}\s*\('
        if re.search(pattern, content):
            existing_methods.append(method)
        else:
            missing_methods.append(method)
    
    print("\n📊 Analysis Results:")
    print(f"✅ Existing methods ({len(existing_methods)}):")
    for method in existing_methods:
        print(f"   - {method}")
    
    print(f"\n❌ Missing methods ({len(missing_methods)}):")
    for method in missing_methods:
        print(f"   - {method}")
    
    # Check for method calls to missing methods
    print("\n🔍 Checking for calls to missing methods...")
    calls_to_missing = []
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for method in missing_methods:
            if f'self.{method}(' in line and not line.strip().startswith('#'):
                calls_to_missing.append(f"Line {i}: {line.strip()}")
    
    if calls_to_missing:
        print("⚠️  Found calls to missing methods:")
        for call in calls_to_missing[:5]:  # Show first 5
            print(f"   {call}")
        if len(calls_to_missing) > 5:
            print(f"   ... and {len(calls_to_missing) - 5} more")
    
    return missing_methods, content


def find_backup_with_methods(missing_methods):
    """Find a backup file that contains the missing methods."""
    print("\n🔍 Searching for backup files...")
    
    backup_files = []
    for file in os.listdir('.'):
        if file.startswith('file_handler.py.backup_'):
            backup_files.append(file)
    
    if not backup_files:
        print("❌ No backup files found")
        return None
    
    backup_files.sort(reverse=True)  # Most recent first
    print(f"Found {len(backup_files)} backup files")
    
    # Check each backup for missing methods
    best_backup = None
    best_score = 0
    
    for backup in backup_files:
        try:
            with open(backup, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_methods = 0
            for method in missing_methods:
                if f'def {method}' in content:
                    found_methods += 1
            
            if found_methods > best_score:
                best_score = found_methods
                best_backup = backup
            
            print(f"   {backup}: contains {found_methods}/{len(missing_methods)} missing methods")
            
        except Exception as e:
            print(f"   {backup}: ❌ Error reading: {e}")
    
    if best_backup and best_score > 0:
        print(f"\n✅ Best backup: {best_backup} (has {best_score}/{len(missing_methods)} missing methods)")
        return best_backup
    else:
        print("❌ No backup contains the missing methods")
        return None


def show_restoration_options(missing_methods, backup_file):
    """Show options for restoring the file."""
    print("\n" + "=" * 70)
    print("RESTORATION OPTIONS")
    print("=" * 70)
    
    print("\n🚨 The problem: Your file_handler.py is missing essential methods")
    print(f"   Missing: {', '.join(missing_methods)}")
    
    print("\n📋 You have several options:")
    
    print("\n1️⃣  RECOMMENDED: Restore from backup")
    if backup_file:
        print(f"   - Found a good backup: {backup_file}")
        print("   - This backup contains the missing methods")
        print(f"   - To restore: copy {backup_file} to file_handler.py")
        print(f"\n   Command: copy {backup_file} file_handler.py")
    else:
        print("   - Unfortunately, no suitable backup was found")
    
    print("\n2️⃣  Manual fix: Add the missing methods")
    print("   - I can generate the missing methods for you")
    print("   - You would need to add them to your file_handler.py")
    
    print("\n3️⃣  Start fresh: Use a clean file_handler.py")
    print("   - If you have the original file from your project")
    print("   - Copy it over the current file_handler.py")
    
    return backup_file is not None


def generate_missing_method_code(method_name):
    """Generate code for a missing method."""
    
    if method_name == '_create_crypto_sheet':
        return '''
    def _create_crypto_sheet(self, wb: Workbook, crypto_name: str, 
                           addresses: List[ExtractedAddress], 
                           include_api_data: bool = False) -> None:
        """Create sheet for a specific cryptocurrency."""
        try:
            # Remove duplicates
            seen = set()
            unique_addresses = []
            for addr in addresses:
                if addr.address not in seen:
                    seen.add(addr.address)
                    unique_addresses.append(addr)
            
            ws = wb.create_sheet(crypto_name[:31])
            self.logger.info(f"Creating '{crypto_name}' sheet")
            
            # Headers
            headers = ["Address", "Source File", "Row", "Column", "Confidence"]
            if include_api_data:
                headers.extend([
                    "Entity Name", "Direct Exposure", "Indirect Exposure",
                    "Receiving Direct", "Receiving Indirect", 
                    "Sending Direct", "Sending Indirect",
                    "Balance", "Total Received", "Total Sent"
                ])
            
            # Write headers with styling
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            # Write data
            for row, addr in enumerate(unique_addresses, 2):
                ws.cell(row=row, column=1, value=addr.address)
                ws.cell(row=row, column=2, value=addr.filename)
                ws.cell(row=row, column=3, value=addr.row)
                ws.cell(row=row, column=4, value=addr.column)
                ws.cell(row=row, column=5, value=f"{addr.confidence:.1f}%")
                
                if include_api_data:
                    col = 6
                    # Entity Name
                    ws.cell(row=row, column=col, value=getattr(addr, 'api_cluster_name', ''))
                    # Exposures
                    ws.cell(row=row, column=col+1, value=self._format_exposure_text(getattr(addr, 'api_direct_exposure', [])))
                    ws.cell(row=row, column=col+2, value=self._format_exposure_text(getattr(addr, 'api_indirect_exposure', [])))
                    ws.cell(row=row, column=col+3, value=self._format_exposure_text(getattr(addr, 'api_receiving_direct_exposure', [])))
                    ws.cell(row=row, column=col+4, value=self._format_exposure_text(getattr(addr, 'api_receiving_indirect_exposure', [])))
                    ws.cell(row=row, column=col+5, value=self._format_exposure_text(getattr(addr, 'api_sending_direct_exposure', [])))
                    ws.cell(row=row, column=col+6, value=self._format_exposure_text(getattr(addr, 'api_sending_indirect_exposure', [])))
                    # Balances
                    ws.cell(row=row, column=col+7, value=f"{getattr(addr, 'api_balance', 0):,.8f}")
                    ws.cell(row=row, column=col+8, value=f"{getattr(addr, 'api_total_received', 0):,.8f}")
                    ws.cell(row=row, column=col+9, value=f"{getattr(addr, 'api_total_sent', 0):,.8f}")
            
            # Auto-fit columns
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
                
        except Exception as e:
            self.logger.error(f"Failed to create {crypto_name} sheet: {str(e)}")
            raise
'''
    
    elif method_name == '_create_summary_sheet':
        return '''
    def _create_summary_sheet(self, wb: Workbook, addresses: List[ExtractedAddress]) -> None:
        """Create summary sheet with extraction statistics."""
        try:
            ws = wb.create_sheet("Summary", 0)
            self.logger.info("Creating 'Summary' sheet")
            
            # Title
            ws.merge_cells('A1:D1')
            title_cell = ws['A1']
            title_cell.value = "Cryptocurrency Address Extraction Summary"
            title_cell.font = Font(size=16, bold=True)
            title_cell.alignment = Alignment(horizontal="center")
            
            # Statistics
            row = 3
            stats = [
                ("Total Addresses Extracted:", len(addresses)),
                ("Unique Addresses:", len(set(addr.address for addr in addresses))),
                ("Duplicate Addresses:", sum(1 for addr in addresses if addr.is_duplicate)),
                ("Files Processed:", len(set(addr.filename for addr in addresses))),
                ("Extraction Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            ]
            
            for label, value in stats:
                ws.cell(row=row, column=1, value=label).font = Font(bold=True)
                ws.cell(row=row, column=2, value=value)
                row += 1
            
            # Crypto breakdown
            row += 1
            ws.cell(row=row, column=1, value="Addresses by Cryptocurrency:").font = Font(bold=True)
            row += 1
            
            crypto_counts = {}
            for addr in addresses:
                crypto_counts[addr.crypto_name] = crypto_counts.get(addr.crypto_name, 0) + 1
            
            for crypto, count in sorted(crypto_counts.items()):
                ws.cell(row=row, column=1, value=f"  {crypto}:")
                ws.cell(row=row, column=2, value=count)
                row += 1
                
        except Exception as e:
            self.logger.error(f"Failed to create summary sheet: {str(e)}")
            raise
'''
    
    elif method_name == '_create_duplicate_analysis_sheet':
        return '''
    def _create_duplicate_analysis_sheet(self, wb: Workbook, addresses: List[ExtractedAddress]) -> None:
        """Create duplicate analysis sheet."""
        try:
            ws = wb.create_sheet("Duplicate Analysis")
            self.logger.info("Creating 'Duplicate Analysis' sheet")
            
            headers = ["Address", "Crypto", "Occurrences", "Files"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="FF4B4B", end_color="FF4B4B", fill_type="solid")
            
            # Group duplicates
            from collections import defaultdict
            duplicates = defaultdict(list)
            for addr in addresses:
                if addr.is_duplicate:
                    duplicates[addr.address].append(addr)
            
            row = 2
            for address, occurrences in sorted(duplicates.items()):
                if len(occurrences) > 1:
                    ws.cell(row=row, column=1, value=address)
                    ws.cell(row=row, column=2, value=occurrences[0].crypto_name)
                    ws.cell(row=row, column=3, value=len(occurrences))
                    files = list(set(addr.filename for addr in occurrences))
                    ws.cell(row=row, column=4, value=", ".join(files[:3]))
                    row += 1
                    
        except Exception as e:
            self.logger.error(f"Failed to create duplicate analysis sheet: {str(e)}")
            # Don't raise - this is optional
'''
    
    return f"# Method {method_name} not implemented"


def main():
    """Main function."""
    print("=" * 70)
    print("FILE HANDLER RESTORATION ANALYSIS")
    print("=" * 70)
    
    # Analyze current state
    result = analyze_file_handler()
    if not result:
        return 1
    
    missing_methods, content = result
    
    if not missing_methods:
        print("\n✅ Great! All required methods are present.")
        print("The error might be due to indentation or other issues.")
        return 0
    
    # Find suitable backup
    backup_file = find_backup_with_methods(missing_methods)
    
    # Show options
    has_backup = show_restoration_options(missing_methods, backup_file)
    
    # Offer to generate missing methods
    print("\n" + "=" * 70)
    choice = input("\nWould you like me to generate the missing methods? (y/n): ")
    
    if choice.lower() == 'y':
        print("\n📝 Generated code for missing methods:")
        print("=" * 70)
        print("\n# Add these methods to your FileHandler class:\n")
        
        for method in missing_methods:
            print(generate_missing_method_code(method))
            print("\n")
        
        print("=" * 70)
        print("\n📋 Instructions:")
        print("1. Open file_handler.py")
        print("2. Find the FileHandler class")
        print("3. Add these methods inside the class (with proper indentation)")
        print("4. Save the file and try running again")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())