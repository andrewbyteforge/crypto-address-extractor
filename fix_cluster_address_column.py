#!/usr/bin/env python3
"""
Fix for the Unicode encoding error in fix_cluster_address_column.py
===================================================================

This shows how to fix the UnicodeEncodeError by specifying UTF-8 encoding
when writing files that contain Unicode characters.
"""

def create_test_script():
    """
    Create a test script to verify cluster address column.
    Fixed to use UTF-8 encoding for proper Unicode support.
    
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        IOError: If file cannot be written
    """
    test_script = '''#!/usr/bin/env python3
"""
Test script to verify cluster address column is properly displayed.
"""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cluster_address():
    """Test that cluster addresses are properly stored and displayed."""
    print("\\n=== Testing Cluster Address Storage ===\\n")
    
    # ... test code ...
    
    print("\\n✅ Cluster address test passed!")  # Unicode character that was causing the error
    
    return True

if __name__ == "__main__":
    test_cluster_address()
'''
    
    try:
        # FIX: Specify UTF-8 encoding when writing files with Unicode characters
        with open('test_cluster_address.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print("✅ Created test_cluster_address.py")  # This will also work now
        return True
        
    except Exception as e:
        print(f"❌ ERROR creating test script: {e}")
        return False


# Example of the fix pattern to apply throughout the script
def fix_file_writing_patterns():
    """
    Examples of how to fix file writing throughout the script.
    """
    
    # WRONG - Will cause UnicodeEncodeError on Windows:
    # with open('somefile.py', 'w') as f:
    #     f.write(content_with_unicode)
    
    # CORRECT - Specify UTF-8 encoding:
    # with open('somefile.py', 'w', encoding='utf-8') as f:
    #     f.write(content_with_unicode)
    
    # For reading files that might contain Unicode:
    # with open('somefile.py', 'r', encoding='utf-8') as f:
    #     content = f.read()
    
    pass


# If you need to fix the entire file, here's a pattern:
def patch_fix_cluster_script():
    """
    Patch the fix_cluster_address_column.py script to add UTF-8 encoding.
    """
    import re
    
    try:
        # Read the original file with UTF-8 encoding
        with open('fix_cluster_address_column.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find file open statements without encoding
        # This regex finds: open(filename, 'w') patterns
        pattern = r"open\(([^,]+),\s*'w'\)"
        replacement = r"open(\1, 'w', encoding='utf-8')"
        
        # Apply the fix
        fixed_content = re.sub(pattern, replacement, content)
        
        # Also fix 'r' mode if needed
        pattern_read = r"open\(([^,]+),\s*'r'\)"
        replacement_read = r"open(\1, 'r', encoding='utf-8')"
        fixed_content = re.sub(pattern_read, replacement_read, fixed_content)
        
        # Write the fixed content back
        with open('fix_cluster_address_column.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ Successfully patched fix_cluster_address_column.py with UTF-8 encoding")
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: fix_cluster_address_column.py not found")
        return False
    except Exception as e:
        print(f"❌ ERROR patching file: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    create_test_script()
    
    # Or patch the entire file:
    # patch_fix_cluster_script()