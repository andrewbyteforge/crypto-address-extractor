#!/usr/bin/env python3
"""
Fix Cluster-Based Exposure API Calls
====================================

This script fixes the exposure API calls to use the cluster's root address
instead of the individual address, which is required for proper exposure data.

Usage:
    python fix_cluster_exposure.py

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


def create_fixed_exposure_method():
    """Create the fixed method that uses cluster root address for exposure."""
    
    fixed_method = '''def _process_single_address_with_logging(self, addr, api_symbol, index, api_stats):
        """
        Process a single address with detailed logging and statistics.
        FIXED: Uses cluster root address for exposure API calls.
        """
        api_data = {}
        call_stats = {}
        
        self.logger.info(f"\\n{'='*60}")
        self.logger.info(f"Processing address {index + 1}: {addr.address}")
        self.logger.info(f"Crypto type: {api_symbol}")
        
        try:
            # Add small delay to prevent rate limiting
            if index > 0:
                time.sleep(0.1)
            
            # Track overall timing
            overall_start = time.time()
            
            # IMPORTANT: We need to get the cluster/root address first from balance API
            cluster_root_address = addr.address  # Default to the address itself
            
            # Get balance information (this also gives us the root address)
            if self.gui.api_balance_var.get():
                start_time = time.time()
                try:
                    self.logger.debug(f"Calling get_cluster_balance for {addr.address[:20]}...")
                    
                    balance_data = self.gui.api_service.get_cluster_balance(
                        addr.address, 
                        api_symbol, 
                        self.gui.api_currency_var.get()
                    )
                    
                    response_time = time.time() - start_time
                    api_stats['response_times'].append(response_time)
                    api_stats['status_codes'][200] += 1
                    
                    self.logger.info(f"✓ Balance API: SUCCESS (200) - {response_time:.2f}s")
                    self.logger.debug(f"  Full balance response: {balance_data}")
                    
                    # Extract balance data
                    api_data['balance'] = balance_data.get('balance', 0)
                    api_data['total_received'] = balance_data.get('totalReceivedAmount', 0)
                    api_data['total_sent'] = balance_data.get('totalSentAmount', 0)
                    api_data['transfer_count'] = balance_data.get('transferCount', 0)
                    api_data['deposit_count'] = balance_data.get('depositCount', 0)
                    api_data['withdrawal_count'] = balance_data.get('withdrawalCount', 0)
                    api_data['address_count'] = balance_data.get('addressCount', 1)
                    api_data['total_fees'] = balance_data.get('totalFeesAmount', 0)
                    
                    # CRITICAL: Get the root address for the cluster
                    cluster_root_address = balance_data.get('rootAddress', addr.address)
                    api_data['root_address'] = cluster_root_address
                    
                    if cluster_root_address != addr.address:
                        self.logger.info(f"  📍 Cluster root address: {cluster_root_address}")
                        self.logger.info(f"  📊 This cluster contains {api_data['address_count']} addresses")
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    error_str = str(e)
                    status_code = self._extract_status_code(error_str)
                    api_stats['status_codes'][status_code] += 1
                    api_stats['error_types'][f'balance_{status_code}'] += 1
                    
                    self.logger.warning(f"✗ Balance API: FAILED ({status_code}) - {response_time:.2f}s")
                    self.logger.warning(f"  Error: {error_str}")
                    api_data['balance_error'] = error_str
                    # Still use the original address if balance API failed
                    cluster_root_address = addr.address
            
            # Get exposure information using CLUSTER ROOT ADDRESS
            if self.gui.api_exposure_var.get():
                self.logger.info(f"\\n  🔍 Getting exposure for cluster root: {cluster_root_address[:20]}...")
                
                # Initialize exposure data structures
                api_data['sending_direct_exposure'] = []
                api_data['sending_indirect_exposure'] = []
                api_data['receiving_direct_exposure'] = []
                api_data['receiving_indirect_exposure'] = []
                
                # Get SENDING exposure using cluster root address
                start_time = time.time()
                try:
                    self.logger.debug(f"Calling get_exposure_by_service (SENDING) for cluster {cluster_root_address[:20]}...")
                    
                    sending_exposure_data = self.gui.api_service.get_exposure_by_service(
                        cluster_root_address,  # USE CLUSTER ROOT ADDRESS
                        api_symbol, 
                        'SENDING',
                        self.gui.api_currency_var.get()
                    )
                    
                    response_time = time.time() - start_time
                    api_stats['response_times'].append(response_time)
                    api_stats['status_codes'][200] += 1
                    
                    self.logger.info(f"✓ Exposure API (SENDING): SUCCESS (200) - {response_time:.2f}s")
                    self.logger.debug(f"  Full SENDING exposure response: {sending_exposure_data}")
                    
                    # Extract services from response
                    services_data = self._extract_services_from_response(sending_exposure_data)
                    
                    # Process ALL services (not just exchanges) for comprehensive data
                    # Direct exposure for SENDING
                    for service in services_data.get('direct', []):
                        service_info = {
                            'name': service.get('name', 'Unknown'),
                            'category': service.get('category', 'Unknown'),
                            'value': service.get('value', service.get('amount', service.get('sentAmount', 0))),
                            'percentage': service.get('percentage', 0)
                        }
                        api_data['sending_direct_exposure'].append(service_info)
                    
                    # Indirect exposure for SENDING
                    for service in services_data.get('indirect', []):
                        service_info = {
                            'name': service.get('name', 'Unknown'),
                            'category': service.get('category', 'Unknown'),
                            'value': service.get('value', service.get('amount', service.get('sentAmount', 0))),
                            'percentage': service.get('percentage', 0)
                        }
                        api_data['sending_indirect_exposure'].append(service_info)
                    
                    self.logger.info(f"  📊 SENDING: {len(api_data['sending_direct_exposure'])} direct, {len(api_data['sending_indirect_exposure'])} indirect exposures")
                    
                    # Log top exposures
                    if api_data['sending_direct_exposure']:
                        self.logger.info("  Top SENDING direct exposures:")
                        for exp in sorted(api_data['sending_direct_exposure'], key=lambda x: x['percentage'], reverse=True)[:3]:
                            self.logger.info(f"    - {exp['name']} ({exp['category']}): {exp['percentage']:.1f}%")
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    error_str = str(e)
                    status_code = self._extract_status_code(error_str)
                    api_stats['status_codes'][status_code] += 1
                    api_stats['error_types'][f'exposure_sent_{status_code}'] += 1
                    self.logger.warning(f"✗ Exposure API (SENDING): FAILED ({status_code}) - {response_time:.2f}s")
                    self.logger.warning(f"  Error: {error_str}")
                
                # Get RECEIVING exposure using cluster root address
                start_time = time.time()
                try:
                    self.logger.debug(f"Calling get_exposure_by_service (RECEIVING) for cluster {cluster_root_address[:20]}...")
                    
                    receiving_exposure_data = self.gui.api_service.get_exposure_by_service(
                        cluster_root_address,  # USE CLUSTER ROOT ADDRESS
                        api_symbol, 
                        'RECEIVING',
                        self.gui.api_currency_var.get()
                    )
                    
                    response_time = time.time() - start_time
                    api_stats['response_times'].append(response_time)
                    api_stats['status_codes'][200] += 1
                    
                    self.logger.info(f"✓ Exposure API (RECEIVING): SUCCESS (200) - {response_time:.2f}s")
                    self.logger.debug(f"  Full RECEIVING exposure response: {receiving_exposure_data}")
                    
                    # Extract services from response
                    services_data = self._extract_services_from_response(receiving_exposure_data)
                    
                    # Process ALL services (not just exchanges)
                    # Direct exposure for RECEIVING
                    for service in services_data.get('direct', []):
                        service_info = {
                            'name': service.get('name', 'Unknown'),
                            'category': service.get('category', 'Unknown'),
                            'value': service.get('value', service.get('amount', service.get('receivedAmount', 0))),
                            'percentage': service.get('percentage', 0)
                        }
                        api_data['receiving_direct_exposure'].append(service_info)
                    
                    # Indirect exposure for RECEIVING
                    for service in services_data.get('indirect', []):
                        service_info = {
                            'name': service.get('name', 'Unknown'),
                            'category': service.get('category', 'Unknown'),
                            'value': service.get('value', service.get('amount', service.get('receivedAmount', 0))),
                            'percentage': service.get('percentage', 0)
                        }
                        api_data['receiving_indirect_exposure'].append(service_info)
                    
                    self.logger.info(f"  📊 RECEIVING: {len(api_data['receiving_direct_exposure'])} direct, {len(api_data['receiving_indirect_exposure'])} indirect exposures")
                    
                    # Log top exposures
                    if api_data['receiving_direct_exposure']:
                        self.logger.info("  Top RECEIVING direct exposures:")
                        for exp in sorted(api_data['receiving_direct_exposure'], key=lambda x: x['percentage'], reverse=True)[:3]:
                            self.logger.info(f"    - {exp['name']} ({exp['category']}): {exp['percentage']:.1f}%")
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    error_str = str(e)
                    status_code = self._extract_status_code(error_str)
                    api_stats['status_codes'][status_code] += 1
                    api_stats['error_types'][f'exposure_received_{status_code}'] += 1
                    self.logger.warning(f"✗ Exposure API (RECEIVING): FAILED ({status_code}) - {response_time:.2f}s")
                    self.logger.warning(f"  Error: {error_str}")
            
            # Get cluster information
            if self.gui.api_cluster_info_var.get():
                start_time = time.time()
                try:
                    self.logger.debug(f"Calling get_cluster_name_and_category for {addr.address[:20]}...")
                    
                    cluster_data = self.gui.api_service.get_cluster_name_and_category(
                        addr.address, 
                        api_symbol
                    )
                    
                    response_time = time.time() - start_time
                    api_stats['response_times'].append(response_time)
                    api_stats['status_codes'][200] += 1
                    
                    self.logger.info(f"✓ Cluster API: SUCCESS (200) - {response_time:.2f}s")
                    self.logger.debug(f"  Full cluster response: {cluster_data}")
                    
                    # Enhanced cluster info parsing
                    cluster_info = self._extract_cluster_info_from_response(cluster_data)
                    
                    if cluster_info:
                        api_data['cluster_name'] = cluster_info.get('name', 'Unknown')
                        api_data['cluster_category'] = cluster_info.get('category', 'Unknown')
                        api_data['cluster_root_address'] = cluster_info.get('rootAddress', cluster_root_address)
                        self.logger.debug(f"  Cluster: {api_data['cluster_name']} ({api_data['cluster_category']})")
                    else:
                        self.logger.debug("  No cluster information found in response")
                        api_data['cluster_name'] = 'Unknown'
                        api_data['cluster_category'] = 'Unknown'
                        api_data['cluster_root_address'] = cluster_root_address
                        
                except Exception as e:
                    response_time = time.time() - start_time
                    error_str = str(e)
                    status_code = self._extract_status_code(error_str)
                    api_stats['status_codes'][status_code] += 1
                    api_stats['error_types'][f'cluster_{status_code}'] += 1
                    
                    self.logger.warning(f"✗ Cluster API: FAILED ({status_code}) - {response_time:.2f}s")
                    self.logger.warning(f"  Error: {error_str}")
                    api_data['cluster_error'] = error_str
            
            # Log overall timing
            total_time = time.time() - overall_start
            self.logger.info(f"Total processing time: {total_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"API error for {addr.address}: {e}")
            call_stats['error'] = str(e)
            call_stats['error_type'] = type(e).__name__
            raise
        
        return api_data, call_stats'''
    
    return fixed_method


def fix_gui_api_processor():
    """Fix the API processor to use cluster root address for exposure."""
    file_path = "gui_api_processor.py"
    
    if not os.path.exists(file_path):
        logger.error(f"❌ ERROR: {file_path} not found")
        return False
    
    logger.info(f"🔧 Fixing API processor to use cluster root address...")
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get the fixed method
        fixed_method = create_fixed_exposure_method()
        
        # Find and replace the _process_single_address_with_logging method
        method_pattern = r'def _process_single_address_with_logging\(self, addr, api_symbol, index, api_stats\):.*?(?=\n    def |\n\nclass |\Z)'
        
        if re.search(method_pattern, content, re.DOTALL):
            content = re.sub(method_pattern, fixed_method.strip() + '\n\n    ', content, flags=re.DOTALL)
            logger.info("✅ Replaced _process_single_address_with_logging method")
        else:
            logger.error("❌ Could not find method to replace")
            return False
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ Applied cluster-based exposure fix")
        
        # Verify syntax
        try:
            compile(content, file_path, 'exec')
            logger.info("✅ Syntax check passed!")
            return True
        except SyntaxError as e:
            logger.error(f"❌ Syntax error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        return False


def update_file_handler_format():
    """Update file handler to show ALL exposure services, not just exchanges."""
    file_path = "file_handler.py"
    
    if not os.path.exists(file_path):
        logger.info("⚠️  file_handler.py not found, skipping format update")
        return True
    
    logger.info(f"🔧 Updating file handler to show all exposure services...")
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update the _format_exposure_text method to show all services
        updated_format_method = '''
    def _format_exposure_text(self, exposures):
        """
        Format exposure data for display in Excel cell.
        Shows ALL services with their categories and percentages.
        """
        if not exposures:
            return "None"
        
        # Sort by percentage/value descending
        sorted_exposures = sorted(
            exposures,
            key=lambda x: x.get('percentage', 0) or (x.get('value', 0) / 1000000),
            reverse=True
        )
        
        # Format all significant exposures
        formatted_parts = []
        for exp in sorted_exposures[:10]:  # Show top 10
            name = exp.get('name', 'Unknown')
            category = exp.get('category', '')
            percentage = exp.get('percentage', 0)
            
            if percentage >= 0.1:  # Only show if >= 0.1%
                # Include category if it's not "exchange"
                if category and category.lower() not in ['exchange', 'unknown']:
                    formatted_parts.append(f"{name} ({category}): {percentage:.1f}%")
                else:
                    formatted_parts.append(f"{name}: {percentage:.1f}%")
        
        return "; ".join(formatted_parts) if formatted_parts else "None"'''
        
        # Find and replace the method
        method_pattern = r'def _format_exposure_text\(self, exposures\):.*?(?=\n    def |\n\nclass |\Z)'
        
        if re.search(method_pattern, content, re.DOTALL):
            content = re.sub(method_pattern, updated_format_method.strip() + '\n', content, flags=re.DOTALL)
            logger.info("✅ Updated _format_exposure_text method")
        
        # Write the updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR updating file handler: {e}")
        return False


def main():
    """Main function."""
    print("=" * 70)
    print("Fix Cluster-Based Exposure API Calls")
    print("=" * 70)
    print("\nThis script fixes exposure API calls to use the cluster root address")
    print("=" * 70 + "\n")
    
    success = True
    
    # Fix API processor
    if not fix_gui_api_processor():
        success = False
    
    # Update file handler formatting
    if not update_file_handler_format():
        logger.warning("⚠️  File handler update failed, but main fix applied")
    
    if success:
        print("\n" + "=" * 70)
        print("✅ Cluster-based exposure fix applied successfully!")
        
        print("\n🔍 What was fixed:")
        print("1. Balance API response now extracts the cluster root address")
        print("2. Exposure API calls use the CLUSTER ROOT ADDRESS, not individual address")
        print("3. All services are captured (not filtered for exchanges only)")
        print("4. Better logging shows cluster information")
        
        print("\n📊 How it works now:")
        print("1. Balance API returns rootAddress (cluster address)")
        print("2. If rootAddress differs from input address, it logs this")
        print("3. Exposure APIs are called with the cluster root address")
        print("4. This ensures you get ALL exposure for the entire cluster")
        
        print("\n🚀 Next steps:")
        print("1. Run your extraction again")
        print("2. Watch the logs - you'll see messages like:")
        print('   "📍 Cluster root address: 1A1zP..."')
        print('   "📊 This cluster contains 523 addresses"')
        print("3. The exposure data will now be complete for the cluster")
        
        print("\n💡 Important:")
        print("- Individual addresses in a cluster share the same exposure")
        print("- The cluster root address is the key to getting complete data")
        print("- All services are now shown, not just those identified as exchanges")
        
        return 0
    else:
        print("\n❌ Failed to apply cluster-based fix")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())