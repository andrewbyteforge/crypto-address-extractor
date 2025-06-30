 
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
        print(f"ERROR: {file_path} not found")
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
            print("\nKey sections found:")
            
            # Find headers section
            headers_match = re.search(r'headers = \[(.*?)\]', method_content, re.DOTALL)
            if headers_match:
                print(f"\nHeaders definition found at line {method_content[:headers_match.start()].count(chr(10)) + 1}")
            
            # Find include_api_data section
            api_match = re.search(r'if include_api_data:(.*?)(?=\n\s{0,8}[^\s])', method_content, re.DOTALL)
            if api_match:
                print(f"\nAPI data section found at line {method_content[:api_match.start()].count(chr(10)) + 1}")
            
        else:
            print("Could not find _create_crypto_sheet method")
            
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    find_crypto_sheet_method()