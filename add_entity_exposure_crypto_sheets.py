#!/usr/bin/env python3
"""
Find and Display _create_crypto_sheet Method
============================================

This script finds and displays the current _create_crypto_sheet method
to help identify where to make manual changes.

Usage:
    python find_crypto_sheet_method.py
"""

import os
import re


def find_crypto_sheet_method():
    """Find and display the _create_crypto_sheet method."""
    file_path = "file_handler.py"
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: {file_path} not found")
        return
    
    print("Finding _create_crypto_sheet method...\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the method
        pattern = r'(def _create_crypto_sheet\(.*?\):.*?)(?=\n    def |\nclass |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            method_content = match.group(1)
            
            # Display the method with line numbers
            lines = method_content.split('\n')
            print("=" * 80)
            print("Current _create_crypto_sheet method:")
            print("=" * 80)
            
            for i, line in enumerate(lines[:100], 1):  # Show first 100 lines
                print(f"{i:3d}: {line}")
            
            if len(lines) > 100:
                print(f"\n... (method continues for {len(lines) - 100} more lines)")
            
            print("\n" + "=" * 80)
            
            # Look for specific patterns
            print("\n📍 Key sections found:")
            
            # Find headers section
            headers_match = re.search(r'headers = \[(.*?)\]', method_content, re.DOTALL)
            if headers_match:
                print(f"\n✅ Headers definition found at line {method_content[:headers_match.start()].count(chr(10)) + 1}")
                print("Current headers:", headers_match.group(0)[:100] + "...")
            
            # Find include_api_data section
            api_match = re.search(r'if include_api_data:(.*?)(?=\n\s{0,8}[^\s])', method_content, re.DOTALL)
            if api_match:
                print(f"\n✅ API data section found at line {method_content[:api_match.start()].count(chr(10)) + 1}")
                api_section = api_match.group(0)
                
                # Check for headers.extend
                if 'headers.extend' in api_section:
                    extend_match = re.search(r'headers\.extend\(\[(.*?)\]\)', api_section, re.DOTALL)
                    if extend_match:
                        print("Current API headers:", extend_match.group(1).strip())
                
                # Check for data writing
                if 'ws.cell' in api_section:
                    print("\n✅ Data writing section found")
                    # Count ws.cell calls
                    cell_calls = re.findall(r'ws\.cell\(.*?\)', api_section)
                    print(f"Number of ws.cell calls in API section: {len(cell_calls)}")
            
            # Provide modification instructions
            print("\n" + "=" * 80)
            print("📝 MODIFICATION INSTRUCTIONS:")
            print("=" * 80)
            
            if 'headers.extend' in method_content:
                print("\n1. Find the line with 'headers.extend([' in the include_api_data section")
                print("   Add 'Entity Name' and 'Exchange Exposure' at the BEGINNING of the list")
                print("   Example: headers.extend(['Entity Name', 'Exchange Exposure', 'Balance', ...])")
            
            print("\n2. In the data writing section (where ws.cell calls are):")
            print("   Add these lines BEFORE writing other API data:")
            print("""
                # Entity Name (from cluster name)
                entity_name = getattr(addr, 'api_cluster_name', None) or 'Unknown'
                ws.cell(row=row, column=10, value=entity_name)
                
                # Exchange Exposure - formatted
                exchange_exposure = getattr(addr, 'api_exchange_exposure', None)
                if exchange_exposure and isinstance(exchange_exposure, list):
                    exposure_parts = []
                    for exp in exchange_exposure[:5]:
                        name = exp.get('name', 'Unknown')
                        value = exp.get('value', 0)
                        exposure_parts.append(f"{name}: {value:.1f}%")
                    exposure_text = ", ".join(exposure_parts)
                else:
                    exposure_text = "None"
                ws.cell(row=row, column=11, value=exposure_text)
            """)
            print("\n3. Update the column numbers for other API data (add 2 to each)")
            
        else:
            print("❌ Could not find _create_crypto_sheet method")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    find_crypto_sheet_method()