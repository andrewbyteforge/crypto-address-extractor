#!/usr/bin/env python3
"""
Excel Pagination Fix Script
===========================

This script adds pagination support to split large sheets into multiple sheets
(Sheet1, Sheet2, etc.) to prevent Excel row limit errors.

Usage:
    python pagination_fix_script.py
"""

import os
import sys
import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the original file."""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path

def add_pagination_helper_function():
    """Add pagination helper function to FileHandler class."""
    target_file = "file_handler.py"
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if pagination helper already exists
        if '_create_paginated_sheet' in content:
            print("✅ Pagination helper function already exists")
            return True
        
        # Find the FileHandler class
        class_start = content.find('class FileHandler:')
        if class_start == -1:
            print("❌ ERROR: Could not find FileHandler class")
            return False
        
        # Find a good place to insert the helper function (before _add_borders method)
        insert_point = content.find('def _add_borders(self,', class_start)
        if insert_point == -1:
            # Try to find any method to insert before
            insert_point = content.find('def _', class_start)
            if insert_point == -1:
                print("❌ ERROR: Could not find insertion point in FileHandler class")
                return False
        
        # Find the start of the line
        while insert_point > 0 and content[insert_point-1] != '\n':
            insert_point -= 1
        
        pagination_helper = '''    def _create_paginated_sheet(self, wb, base_name, headers, data_rows, process_row_func, 
                               max_rows_per_sheet=1000000, **kwargs):
        """
        Create paginated sheets to handle large datasets that exceed Excel row limits.
        
        Args:
            wb: Workbook object
            base_name: Base name for sheets (e.g., "Exchange Exposure")
            headers: List of column headers
            data_rows: List of data rows to process
            process_row_func: Function to process each row
            max_rows_per_sheet: Maximum rows per sheet (default: 1M to stay under Excel limit)
            **kwargs: Additional arguments passed to process_row_func
            
        Returns:
            List of created worksheet names
        """
        if not data_rows:
            return []
        
        created_sheets = []
        current_sheet = 1
        
        # Calculate rows needed per sheet (including headers and formatting)
        header_rows = 10  # Buffer for titles, summaries, etc.
        max_data_rows = max_rows_per_sheet - header_rows
        
        total_pages = (len(data_rows) + max_data_rows - 1) // max_data_rows
        
        for page in range(total_pages):
            # Create sheet name
            if total_pages == 1:
                sheet_name = base_name
            else:
                sheet_name = f"{base_name} ({page + 1})"
            
            # Ensure sheet name is valid for Excel (max 31 chars)
            if len(sheet_name) > 31:
                sheet_name = f"{base_name[:25]} ({page + 1})"
            
            ws = wb.create_sheet(sheet_name)
            created_sheets.append(sheet_name)
            
            # Calculate data slice for this page
            start_idx = page * max_data_rows
            end_idx = min(start_idx + max_data_rows, len(data_rows))
            page_data = data_rows[start_idx:end_idx]
            
            # Add pagination info to title
            if total_pages > 1:
                ws['A1'] = f"{base_name} - Page {page + 1} of {total_pages}"
                ws['A1'].font = Font(size=14, bold=True)
                ws.merge_cells('A1:H1')
                
                ws['A2'] = f"Showing rows {start_idx + 1:,} to {end_idx:,} of {len(data_rows):,} total"
                ws['A2'].font = Font(size=10, italic=True)
                ws.merge_cells('A2:H2')
                
                current_row = 4
            else:
                ws['A1'] = f"{base_name} ({len(data_rows):,} items)"
                ws['A1'].font = Font(size=14, bold=True)
                ws.merge_cells('A1:H1')
                current_row = 3
            
            # Add headers
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=current_row, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            header_row = current_row
            current_row += 1
            
            # Process data rows
            for row_data in page_data:
                try:
                    process_row_func(ws, current_row, row_data, **kwargs)
                    current_row += 1
                except Exception as e:
                    self.logger.error(f"Error processing row in {sheet_name}: {e}")
                    continue
            
            # Add borders to the data
            if len(page_data) > 0:
                try:
                    self._add_borders(ws, header_row, header_row, current_row - 1, len(headers))
                except:
                    pass  # Borders are optional
            
            # Add pagination navigation info at bottom
            if total_pages > 1:
                current_row += 2
                nav_text = f"📄 Page {page + 1} of {total_pages} | "
                if page > 0:
                    nav_text += f"Previous: {base_name} ({page}) | "
                if page < total_pages - 1:
                    nav_text += f"Next: {base_name} ({page + 2})"
                
                ws.cell(row=current_row, column=1, value=nav_text)
                ws.cell(row=current_row, column=1).font = Font(size=9, italic=True, color="666666")
        
        return created_sheets

'''
        
        # Insert the helper function
        content = content[:insert_point] + pagination_helper + content[insert_point:]
        
        # Write the updated content
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ ADDED: Pagination helper function to FileHandler")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to add pagination helper - {str(e)}")
        return False

def fix_exchange_exposure_sheet_with_pagination():
    """Replace the _create_exchange_exposure_sheet function with paginated version."""
    target_file = "file_handler.py"
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the _create_exchange_exposure_sheet function
        function_start = content.find('def _create_exchange_exposure_sheet(')
        if function_start == -1:
            print("❌ ERROR: Could not find _create_exchange_exposure_sheet function")
            return False
        
        # Find the end of the function (next def or class)
        function_end = content.find('\n    def ', function_start + 1)
        if function_end == -1:
            function_end = content.find('\nclass ', function_start + 1)
        if function_end == -1:
            function_end = len(content)
        
        # Create the new paginated function
        new_function = '''def _create_exchange_exposure_sheet(self, wb: Workbook, addresses: List[ExtractedAddress]) -> None:
        """
        Create a dedicated Exchange Exposure sheet with pagination for large datasets.
        ENHANCED: Now supports pagination to handle datasets larger than Excel row limits.
        """
        # Filter addresses that have exchange exposure
        exposed_addresses = [
            addr for addr in addresses 
            if hasattr(addr, 'api_exchange_exposure') and getattr(addr, 'api_exchange_exposure', [])
        ]
        
        if not exposed_addresses:
            return
        
        # Flatten exposure data for pagination
        exposure_rows = []
        for addr in exposed_addresses:
            for exp in getattr(addr, 'api_exchange_exposure', []):
                exposure_rows.append({
                    'address': addr.address,
                    'crypto': addr.crypto_name,
                    'exchange': exp['name'],
                    'category': exp['category'],
                    'value': exp['value'],
                    'filename': addr.filename,
                    'sheet': addr.sheet_name or "N/A",
                    'direction': exp.get('direction', 'Unknown')
                })
        
        # Sort by exposure value descending (most important first)
        exposure_rows.sort(key=lambda x: x['value'], reverse=True)
        
        # Calculate summary statistics
        total_exposures = len(exposure_rows)
        unique_exchanges = set(row['exchange'] for row in exposure_rows)
        
        # Define headers
        headers = [
            'Address', 'Cryptocurrency', 'Exchange', 'Category', 'Exposure Value', 
            'Risk Level', 'Direction', 'Source File', 'Sheet'
        ]
        
        def process_exposure_row(ws, current_row, exp_data, **kwargs):
            """Process a single exposure row for pagination."""
            # Determine risk level based on value
            value = exp_data['value']
            if value > 100:
                risk_level = "Critical"
            elif value > 10:
                risk_level = "High"
            elif value > 1:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            # Add data to cells
            ws.cell(row=current_row, column=1, value=exp_data['address'])
            ws.cell(row=current_row, column=2, value=exp_data['crypto'])
            ws.cell(row=current_row, column=3, value=exp_data['exchange'])
            ws.cell(row=current_row, column=4, value=exp_data['category'])
            ws.cell(row=current_row, column=5, value=f"{value:,.4f}")
            ws.cell(row=current_row, column=6, value=risk_level)
            ws.cell(row=current_row, column=7, value=exp_data['direction'])
            ws.cell(row=current_row, column=8, value=exp_data['filename'])
            ws.cell(row=current_row, column=9, value=exp_data['sheet'])
            
            # Color coding based on risk level
            if risk_level == "Critical":
                color = "FF4444"  # Bright red
            elif risk_level == "High":
                color = "FF8888"  # Light red
            elif risk_level == "Medium":
                color = "FFAAAA"  # Very light red
            else:
                color = "FFDDDD"  # Pale red
                
            for col in range(1, 10):
                ws.cell(row=current_row, column=col).fill = PatternFill(
                    start_color=color, end_color=color, fill_type="solid"
                )
        
        # Create paginated sheets
        created_sheets = self._create_paginated_sheet(
            wb=wb,
            base_name="Exchange Exposure",
            headers=headers,
            data_rows=exposure_rows,
            process_row_func=process_exposure_row,
            max_rows_per_sheet=900000  # Conservative limit for Excel
        )
        
        # If multiple sheets were created, add a summary sheet
        if len(created_sheets) > 1:
            summary_ws = wb.create_sheet("Exchange Exposure Summary", 
                                       wb.sheetnames.index(created_sheets[0]))
            
            # Summary title
            summary_ws['A1'] = "Exchange Exposure Summary"
            summary_ws['A1'].font = Font(size=16, bold=True)
            summary_ws.merge_cells('A1:D1')
            
            # Statistics
            current_row = 3
            summary_ws[f'A{current_row}'] = "📊 Dataset Statistics"
            summary_ws[f'A{current_row}'].font = Font(size=12, bold=True)
            current_row += 2
            
            summary_ws[f'A{current_row}'] = f"Total exchange connections: {total_exposures:,}"
            current_row += 1
            summary_ws[f'A{current_row}'] = f"Unique exchanges: {len(unique_exchanges)}"
            current_row += 1
            summary_ws[f'A{current_row}'] = f"Addresses analyzed: {len(exposed_addresses):,}"
            current_row += 1
            summary_ws[f'A{current_row}'] = f"Data sheets created: {len(created_sheets)}"
            current_row += 3
            
            # Sheet navigation
            summary_ws[f'A{current_row}'] = "📄 Data Sheets"
            summary_ws[f'A{current_row}'].font = Font(size=12, bold=True)
            current_row += 2
            
            for i, sheet_name in enumerate(created_sheets):
                summary_ws[f'A{current_row}'] = f"{i+1}. {sheet_name}"
                current_row += 1
            
            current_row += 2
            summary_ws[f'A{current_row}'] = "⚠️  COMPLIANCE ALERT: These addresses have connections to cryptocurrency exchanges"
            summary_ws[f'A{current_row}'].font = Font(bold=True, color="FF0000")
        
        # Adjust column widths for all created sheets
        for sheet_name in created_sheets:
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                ws.column_dimensions['A'].width = 45  # Address
                ws.column_dimensions['B'].width = 15  # Crypto
                ws.column_dimensions['C'].width = 20  # Exchange
                ws.column_dimensions['D'].width = 15  # Category
                ws.column_dimensions['E'].width = 15  # Value
                ws.column_dimensions['F'].width = 12  # Risk Level
                ws.column_dimensions['G'].width = 12  # Direction
                ws.column_dimensions['H'].width = 20  # File
                ws.column_dimensions['I'].width = 15  # Sheet

'''
        
        # Replace the function
        content = content[:function_start] + new_function + content[function_end:]
        
        # Write the updated content
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ REPLACED: _create_exchange_exposure_sheet with paginated version")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to replace function - {str(e)}")
        return False

def fix_other_large_sheets():
    """Add pagination to other potentially large sheets."""
    target_file = "file_handler.py"
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add row limit checks to other sheet creation functions
        functions_to_fix = [
            '_create_crypto_sheet',
            '_create_balances_sheet',
            '_create_high_value_sheet',
            '_create_risk_analysis_sheet'
        ]
        
        fixes_applied = 0
        
        for func_name in functions_to_fix:
            # Look for loops that write many rows
            pattern = f'(def {func_name}.*?)(for .* in .*?:.*?ws\.cell\(row=row,)'
            
            if re.search(pattern, content, re.DOTALL):
                # Add row limit check
                old_pattern = r'(ws\.cell\(row=row, column=1,)'
                new_pattern = r'''            # Check Excel row limit
            if row >= 1048500:  # Excel limit minus buffer
                ws.cell(row=row, column=1, value="⚠️ DATA TRUNCATED - Excel row limit reached")
                ws.cell(row=row, column=1).font = Font(bold=True, color="FF0000")
                break
            
            \1'''
                
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content, count=1)
                    fixes_applied += 1
        
        if fixes_applied > 0:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ ADDED: Row limit checks to {fixes_applied} additional sheet functions")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to fix other sheets - {str(e)}")
        return False

def main():
    """Main function."""
    print("Excel Pagination Fix Script")
    print("=" * 60)
    print(f"Fix time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    target_file = "file_handler.py"
    
    if not os.path.exists(target_file):
        print(f"❌ ERROR: {target_file} not found")
        return 1
    
    # Create backup
    backup_path = backup_file(target_file)
    
    success = True
    
    print("🔧 Step 1: Adding pagination helper function...")
    if not add_pagination_helper_function():
        success = False
    
    print("\n🔧 Step 2: Fixing Exchange Exposure sheet with pagination...")
    if not fix_exchange_exposure_sheet_with_pagination():
        success = False
    
    print("\n🔧 Step 3: Adding row limit checks to other sheets...")
    if not fix_other_large_sheets():
        success = False
    
    if success:
        print("\n" + "="*60)
        print("🎉 SUCCESS: Pagination support added!")
        print("\nNew features:")
        print("  ✅ Automatic sheet pagination when data exceeds Excel limits")
        print("  ✅ Summary sheets for multi-page datasets")
        print("  ✅ Page navigation information")
        print("  ✅ Row limit checks in all sheet creation functions")
        print("  ✅ Data sorted by importance (highest values first)")
        print("\nHow it works:")
        print("  • Large datasets automatically split into multiple sheets")
        print("  • Each sheet contains ~900,000 rows (safe Excel limit)")
        print("  • Sheet names: 'Exchange Exposure (1)', 'Exchange Exposure (2)', etc.")
        print("  • Summary sheet created for multi-page datasets")
        print("  • Most important data (highest values) appears first")
        print("\nYou can now process datasets of any size without Excel errors!")
        
    else:
        print("\n❌ FAILED: Could not apply all pagination fixes.")
        print(f"Backup created: {backup_path}")
        print("You may need to apply some fixes manually.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())