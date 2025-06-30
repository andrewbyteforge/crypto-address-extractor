#!/usr/bin/env python3
"""
IAPIService Class Fix
====================

This script fixes the IAPIService class import issue in iapi_service.py.

Usage:
    python iapi_class_fix.py
"""

import os
import sys
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the original file."""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path

def check_and_fix_iapi_service():
    """
    Check and fix the IAPIService class in iapi_service.py.
    
    Filename: iapi_service.py
    Class: IAPIService
    """
    target_file = "iapi_service.py"
    
    if not os.path.exists(target_file):
        print(f"❌ ERROR: {target_file} not found")
        return False
    
    # Create backup
    backup_path = backup_file(target_file)
    
    try:
        # Read the file
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Analyzing iapi_service.py...")
        
        # Check if IAPIService class exists
        if 'class IAPIService' not in content:
            print("❌ IAPIService class not found in file!")
            print("🔧 Recreating the complete IAPIService class...")
            
            # Create a complete working version
            fixed_content = create_working_iapi_service()
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print("✅ FIXED: Recreated complete IAPIService class")
            return True
        
        # Check for syntax issues
        lines = content.split('\n')
        issues_found = []
        fixed_lines = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Check for common syntax issues
            if line.strip().startswith('class IAPIService') and not line.endswith(':'):
                issues_found.append(f"Line {line_num}: Class definition missing colon")
                fixed_lines.append(line.rstrip() + ':')
            elif 'def __init__' in line and 'self' not in line:
                issues_found.append(f"Line {line_num}: Missing self parameter")
                fixed_lines.append(line.replace('def __init__(', 'def __init__(self, '))
            else:
                fixed_lines.append(line)
        
        if issues_found:
            print(f"🔧 Found {len(issues_found)} syntax issues:")
            for issue in issues_found:
                print(f"  - {issue}")
            
            # Write fixed content
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            
            print("✅ FIXED: Applied syntax fixes")
            return True
        
        # If no obvious issues, try to compile and check for other problems
        try:
            compile(content, target_file, 'exec')
            print("✅ File syntax is correct")
            
            # Check if the class is properly defined
            if 'def __init__(self' in content and 'def _get(' in content:
                print("✅ IAPIService class structure looks correct")
                return True
            else:
                print("⚠️  Class structure might be incomplete")
                return fix_incomplete_class(content)
                
        except SyntaxError as e:
            print(f"❌ Syntax error found: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            return fix_syntax_error(content, e)
        
    except Exception as e:
        print(f"❌ ERROR: Failed to analyze iapi_service.py - {str(e)}")
        # Restore backup if something went wrong
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, target_file)
            print(f"📦 Restored backup from {backup_path}")
        return False

def create_working_iapi_service():
    """Create a complete working IAPIService class."""
    return '''import requests
import time
import logging

class IAPIService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.server = "iapi.chainalysis.com"
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.logger = logging.getLogger(__name__)
        
        # Use session for connection pooling - this is the key performance improvement
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Token": self.api_key
        })
        
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=100,  # Number of connection pools to cache
            pool_maxsize=100,      # Maximum number of connections to save in the pool
            max_retries=0          # We handle retries manually
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

    def _get(self, path, params=None):
        url = f"https://{self.server}{path}"
        
        for attempt in range(self.max_retries):
            try:
                # Use session instead of requests.get for connection reuse
                req = self.session.get(url, params=params, timeout=30)
                
                if req.status_code == 200:
                    return req.json()
                elif req.status_code == 503:
                    # Service unavailable, retry with exponential backoff
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(req.status_code, req.text)
                else:
                    raise Exception(req.status_code, req.text)
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception("Request timeout", "The API request timed out")
                    
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception("Connection error", "Failed to connect to API")
        
        raise Exception(503, "Service unavailable after retries")
    
    def close(self):
        """Close the session to free up resources."""
        self.session.close()

    # --------------------------------
    # Cluster Info Endpoints
    # --------------------------------

    def get_cluster_name_and_category(self, address, asset):
        """
        Cluster Name and Category
        For a given cryptocurrency address, this endpoint returns
        the respective cluster's name, category, and cluster root address.
        """
        params = {
            "filterAsset": asset
        }
        path = f"/clusters/{address}"
        return self._get(path, params)

    def get_cluster_addresses(self, address, asset, params=None):
        """
        Cluster Addresses
        This endpoint returns a list of addresses associated
        with a specific cluster for given a cryptocurrency address and asset.
        """
        path = f"/clusters/{address}/{asset}/addresses"
        return self._get(path, params)

    def get_cluster_balance(self, address, asset, output_asset="NATIVE"):
        """
        Cluster balance
        This endpoint returns cluster balance details including
        address count, transfer count, deposit count, withdrawal count,
        and total sent and received fees for a given cryptocurrency address.
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        params = {
            "outputAsset": output_asset
        }
        path = f"/clusters/{address}/{asset}/summary"
        return self._get(path, params=params)

    def get_cluster_transactions(self, address, asset, params=None):
        """
        Cluster Transactions
        This endpoint returns the transaction hashes associated
        with a specific cluster for a given cryptocurrency address and asset.
        """
        path = f"/clusters/{address}/{asset}/transactions"
        return self._get(path, params)

    def get_cluster_counterparties(self, address, asset, output_asset="NATIVE", params=None):
        """
        Cluster Counterparties
        This endpoint returns the counterparties associated with
        a specific cluster for a given cryptocurrency address and asset.
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        if params is None:
            params = {}
        params["outputAsset"] = output_asset
        path = f"/clusters/{address}/{asset}/counterparties"
        return self._get(path, params)

    # --------------------------------
    # Transaction Info Endpoints
    # --------------------------------

    def get_transaction_time_and_asset(self, hash, params=None):
        """
        Transaction Time & Asset
        This endpoint returns the asset, blockhash, block height
        and block time for a given transaction hash.
        """
        path = f"/transactions/{hash}"
        return self._get(path, params)

    def get_transaction_details(self, hash, asset):
        """
        Transaction Time & Asset
        This endpoint returns the asset, blockhash, block height
        and block time for a given transaction hash.
        """
        path = f"/transactions/{hash}/{asset}/details"
        return self._get(path)

    def get_address_transactions(self, address, asset, direction):
        """
        Transaction hashes by address
        This endpoint returns transaction hashes of transactions
        where the given address is either a sender or receiver.
        """
        params = {
            "direction": direction
        }
        path = f"/addresses/{address}/{asset}/transactions"
        return self._get(path, params=params)

    # --------------------------------
    # Exposure Info Endpoint
    # --------------------------------

    def get_exposure_by_category(self, address, asset, direction, output_asset="NATIVE"):
        """
        Exposure
        This endpoint returns direct and indirect exposure values and percentages by category for a given cluster.
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        params = {
            "outputAsset": output_asset
        }
        path = f"/exposures/clusters/{address}/{asset}/directions/{direction}"
        return self._get(path, params=params)

    def get_exposure_by_service(self, address, asset, direction, output_asset="NATIVE"):
        """
        Exposure
        This endpoint returns direct and indirect exposure values and percentages by services for a given cluster.
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        params = {
            "outputAsset": output_asset
        }
        path = f"/exposures/clusters/{address}/{asset}/directions/{direction}/services"
        return self._get(path, params=params)

    # --------------------------------
    # Wallet Observations Endpoints
    # --------------------------------

    def get_cluster_observations_by_ip(self, ip, params=None):
        """
        Get Observations by Cluster endpoint
        """
        path = f"/observations/ips/{ip}"
        return self._get(path, params)

    def get_observations_by_country(self, country, params=None):
        """
        Get Observations by Country endpoint
        """
        path = f"/observations/countries/{country}"
        return self._get(path, params)

    def get_observations_by_city(self, country, city, params=None):
        """
        Get Observations by City endpoint
        """
        path = f"/observations/countries/{country}/cities/{city}"
        return self._get(path, params)

    def get_observations_for_cluster(self, address, params=None):
        """
        Get Observations by Cluster endpoint
        """
        path = f"/observations/clusters/{address}/BTC"
        return self._get(path, params)

    # --------------------------------
    # Usage Info Endpoints
    # --------------------------------

    def get_usage_by_org(self, startDate, endDate, params=None):
        """
        Get Usage by Organization endpoint
        """
        path = f"/usage/org/{startDate}/{endDate}"
        return self._get(path, params)

    def get_usage_by_user(self, startDate, endDate, params=None):
        """
        Get Usage by User endpoint
        """
        path = f"/usage/user/{startDate}/{endDate}"
        return self._get(path, params)
'''

def fix_incomplete_class(content):
    """Fix incomplete class structure."""
    print("🔧 Fixing incomplete class structure...")
    
    # Basic fixes for common issues
    if 'def __init__' not in content:
        print("❌ Missing __init__ method")
        return False
    
    if 'def _get(' not in content:
        print("❌ Missing _get method")
        return False
    
    # The class seems to have basic structure
    return True

def fix_syntax_error(content, error):
    """Fix specific syntax errors."""
    print(f"🔧 Attempting to fix syntax error on line {error.lineno}...")
    
    lines = content.split('\n')
    
    if error.lineno <= len(lines):
        problematic_line = lines[error.lineno - 1]
        print(f"   Problematic line: {problematic_line}")
        
        # Common fixes
        if 'class IAPIService' in problematic_line and not problematic_line.endswith(':'):
            lines[error.lineno - 1] = problematic_line.rstrip() + ':'
            print("   Fixed: Added missing colon to class definition")
        elif 'def ' in problematic_line and not problematic_line.endswith(':'):
            lines[error.lineno - 1] = problematic_line.rstrip() + ':'
            print("   Fixed: Added missing colon to method definition")
        else:
            print("   Could not auto-fix this syntax error")
            return False
        
        # Write the fixed content
        with open("iapi_service.py", 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
    
    return False

def test_import():
    """Test that the IAPIService class can be imported."""
    try:
        # Clear any cached imports
        if 'iapi_service' in sys.modules:
            del sys.modules['iapi_service']
        
        # Try to import
        from iapi_service import IAPIService
        
        # Try to create an instance
        service = IAPIService("test_key")
        
        print("✅ IMPORT TEST PASSED: IAPIService can be imported and instantiated")
        return True
        
    except ImportError as e:
        print(f"❌ IMPORT TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ IMPORT TEST ERROR: {str(e)}")
        return False

def main():
    """Main function."""
    print("IAPIService Class Fix")
    print("=" * 50)
    print(f"Fix time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("🔧 Step 1: Checking and fixing IAPIService class...")
    if not check_and_fix_iapi_service():
        print("❌ FAILED: Could not fix IAPIService class")
        return 1
    
    print("\n🧪 Step 2: Testing import functionality...")
    if not test_import():
        print("❌ FAILED: Import test failed")
        print("\nThe file may need manual review:")
        print("1. Check that 'class IAPIService:' line exists")
        print("2. Check that '__init__' method is properly defined")
        print("3. Check for missing colons after method definitions")
        return 1
    
    print("\n✅ SUCCESS: IAPIService class is working correctly!")
    print("You can now run your application:")
    print("    python main.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())