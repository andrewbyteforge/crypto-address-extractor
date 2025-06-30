"""
GUI API Processor Module
========================
This module handles all Chainalysis API processing with progress tracking.
Enhanced to avoid duplicate API calls and provide detailed logging.
UPDATED: Added proper Solana support and enhanced parsing.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.2.0 - Added Solana support and enhanced parsing
"""

import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
import logging
from typing import List, Dict, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from extractor import ExtractedAddress
from datetime import datetime


class APICallTracker:
    """
    Comprehensive API call tracking for detailed statistics.
    
    This class tracks all API calls made during processing including:
    - Total API calls made
    - Successful vs failed calls  
    - API calls by endpoint type (cluster, balance, exposure)
    - Time spent on API calls
    - Error details and status codes
    """
    
    def __init__(self):
        """Initialize API call tracking with all required metrics."""
        self.logger = logging.getLogger(__name__)
        self.reset_statistics()
    
    def reset_statistics(self):
        """Reset all tracking statistics."""
        self.total_api_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.start_time = None
        self.end_time = None
        
        # Calls by endpoint type
        self.calls_by_endpoint = {
            'cluster': 0,
            'balance': 0,
            'sending_exposure': 0,
            'receiving_exposure': 0
        }
        
        # Success/failure by endpoint
        self.success_by_endpoint = {
            'cluster': 0,
            'balance': 0,
            'sending_exposure': 0,
            'receiving_exposure': 0
        }
        
        self.failure_by_endpoint = {
            'cluster': 0,
            'balance': 0,
            'sending_exposure': 0,
            'receiving_exposure': 0
        }
        
        # Response times by endpoint
        self.response_times = {
            'cluster': [],
            'balance': [],
            'sending_exposure': [],
            'receiving_exposure': []
        }
        
        # Error tracking
        self.error_details = []
        self.status_codes = {}
        
        self.logger.debug("API call tracking statistics reset")
    
    def start_tracking(self):
        """Start timing for API processing."""
        self.start_time = datetime.now()
        self.logger.info("API call tracking started")
    
    def end_tracking(self):
        """End timing for API processing."""
        self.end_time = datetime.now()
        if self.start_time:
            total_time = (self.end_time - self.start_time).total_seconds()
            self.logger.info(f"API call tracking ended. Total time: {total_time:.2f} seconds")
    
    def record_api_call(self, endpoint_type, success, response_time, status_code=None, error_message=None):
        """
        Record an API call with all relevant metrics.
        
        Args:
            endpoint_type (str): Type of API endpoint
            success (bool): Whether the call was successful
            response_time (float): Time taken for the call in seconds
            status_code (int, optional): HTTP status code
            error_message (str, optional): Error message if failed
        """
        if endpoint_type not in self.calls_by_endpoint:
            self.logger.warning(f"Unknown endpoint type: {endpoint_type}")
            return
        
        self.total_api_calls += 1
        self.calls_by_endpoint[endpoint_type] += 1
        self.response_times[endpoint_type].append(response_time)
        
        if success:
            self.successful_calls += 1
            self.success_by_endpoint[endpoint_type] += 1
        else:
            self.failed_calls += 1
            self.failure_by_endpoint[endpoint_type] += 1
            
            if error_message:
                self.error_details.append({
                    'endpoint': endpoint_type,
                    'error': error_message,
                    'status_code': status_code,
                    'timestamp': datetime.now(),
                    'response_time': response_time
                })
        
        if status_code:
            self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
    
    def get_statistics_summary(self):
        """Get comprehensive statistics summary for Excel export."""
        total_time = 0
        if self.start_time and self.end_time:
            total_time = (self.end_time - self.start_time).total_seconds()
        
        # Calculate average response times by endpoint
        avg_response_times = {}
        for endpoint, times in self.response_times.items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
            else:
                avg_response_times[endpoint] = 0.0
        
        success_rate = 0.0
        if self.total_api_calls > 0:
            success_rate = (self.successful_calls / self.total_api_calls) * 100
        
        return {
            'total_calls': self.total_api_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': success_rate,
            'total_time_seconds': total_time,
            'calls_by_endpoint': self.calls_by_endpoint.copy(),
            'success_by_endpoint': self.success_by_endpoint.copy(),
            'failure_by_endpoint': self.failure_by_endpoint.copy(),
            'avg_response_times': avg_response_times,
            'status_codes': self.status_codes.copy(),
            'error_count': len(self.error_details)
        }



class APIProcessor:
    """Handles API processing with progress tracking."""
    
    def __init__(self, parent_gui):
        self.gui = parent_gui
        self.logger = logging.getLogger(__name__)
        self.api_tracker = APICallTracker()
    
    def _bulk_deduplicate_addresses(self, addresses: List[ExtractedAddress]) -> Dict[str, List[int]]:
        """
        OPTIMIZED: Bulk deduplicate addresses before API processing.
        Performance improvement: Avoids duplicate API calls entirely.
        
        Returns:
            Dictionary mapping unique addresses to list of indices
        """
        address_map = defaultdict(list)
        
        for idx, addr in enumerate(addresses):
            key = (addr.address.lower(), addr.crypto_type)
            address_map[key].append(idx)
        
        unique_count = len(address_map)
        total_count = len(addresses)
        duplicate_savings = total_count - unique_count
        
        self.logger.info(f"BULK DEDUPLICATION: {total_count} -> {unique_count} addresses")
        self.logger.info(f"API CALL SAVINGS: {duplicate_savings} duplicate calls avoided")
        
        return dict(address_map)

    def enhance_with_chainalysis_api(self, addresses: List[ExtractedAddress]) -> List[ExtractedAddress]:
        """
        Enhanced version with progress tracking and proper threading.
        Now avoids duplicate API calls for the same address and includes Solana support.
        """
        
        # Initialize API call tracking
        self.api_tracker.reset_statistics()
        self.api_tracker.start_tracking()
        self.logger.info("Starting comprehensive API call tracking")
        if not self.gui.api_service:
            return addresses
        
        # Create progress dialog
        progress_dialog = self._create_api_progress_dialog()
        
        # Group addresses by unique (address, crypto_type) to avoid duplicates
        unique_addresses = {}
        address_indices = defaultdict(list)  # Track which indices have each address
        
        for idx, addr in enumerate(addresses):
            key = (addr.address.lower(), addr.crypto_type)
            if key not in unique_addresses:
                unique_addresses[key] = addr
            address_indices[key].append(idx)
        
        unique_list = list(unique_addresses.values())
        total_unique = len(unique_list)
        total_addresses = len(addresses)
        
        self.logger.info("="*80)
        self.logger.info("API PROCESSING SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Total addresses in file: {total_addresses}")
        self.logger.info(f"Unique addresses to process: {total_unique}")
        self.logger.info(f"Duplicate addresses avoided: {total_addresses - total_unique}")
        self.logger.info("="*80)
        
        # Log duplicate statistics
        duplicate_stats = {}
        for key, indices in address_indices.items():
            if len(indices) > 1:
                addr_str, crypto = key
                if crypto not in duplicate_stats:
                    duplicate_stats[crypto] = []
                duplicate_stats[crypto].append((addr_str, len(indices)))
        
        if duplicate_stats:
            self.logger.info("DUPLICATE ADDRESS STATISTICS:")
            for crypto, dupes in duplicate_stats.items():
                self.logger.info(f"\n{crypto}:")
                for addr, count in sorted(dupes, key=lambda x: x[1], reverse=True)[:5]:
                    self.logger.info(f"  {addr[:20]}... appears {count} times")
        
        # UPDATED: Enhanced crypto mapping with proper Solana support
        crypto_mapping = {
            'BTC':   'BTC',
            'WBTC':  'BTC',   # Wrapped BTC
            'ETH':   'ETH',
            'USDT':  'ETH',   # ERC-20 on Ethereum (primary)
            'USDT_TRX': 'TRX',# USDT on Tron
            'USDC':  'ETH',   # ERC-20
            'DAI':   'ETH',
            'LINK':  'ETH',
            'UNI':   'ETH',
            'AAVE':  'ETH',
            'COMP':  'ETH',
            'MKR':   'ETH',
            'SHIB':  'ETH',
            'MATIC': 'MATIC',
            'POLYGON': 'MATIC',
            'AVAX':  'AVAX',
            'FTM':   'FTM',
            'FANTOM': 'FTM',
            'NEAR':  'NEAR',
            'DOT':   'DOT',
            'POLKADOT': 'DOT',
            'ATOM':  'ATOM',
            'COSMOS': 'ATOM',
            'ADA':   'ADA',
            'CARDANO': 'ADA',
            'SOL':   'SOL',        # Added Solana support
            'SOLANA': 'SOL',       # Added Solana alias
            'TRX':   'TRX',
            'TRON':  'TRX',
            'BCH':   'BCH',
            'DASH':  'DASH',
            'ZEC':   'ZEC',
            'EOS':   'EOS',
            'ALGO':  'ALGO',
            'BSV':   'BSV',
            'ETC':   'ETC',
            'XLM':   'XLM',
            'STELLAR': 'XLM',
            'XRP':   'XRP',
            'RIPPLE': 'XRP',
            'LTC':   'LTC',
            'LITECOIN': 'LTC',
            'DOGE':  'DOGE',
            'DOGECOIN': 'DOGE',
            'XMR':   'XMR',
            'MONERO': 'XMR',
            'FIL':   'FIL',   # Filecoin
            'FILECOIN': 'FIL',
            'ICP':   'ICP',   # Internet Computer
            'FLOW':  'FLOW',
            'THETA': 'THETA',
        }
        
        # Setup progress tracking
        progress_queue = queue.Queue()
        api_results = {}
        stop_event = threading.Event()
        
        # Track API call statistics
        api_stats = {
            'success': 0,
            'errors': 0,
            'status_codes': defaultdict(int),
            'response_times': [],
            'error_types': defaultdict(int)
        }
        
        def update_progress():
            """Update progress dialog from queue"""
            try:
                while True:
                    msg = progress_queue.get_nowait()
                    if msg[0] == 'update':
                        current, total, text = msg[1], msg[2], msg[3]
                        progress_dialog['progress_var'].set((current / total) * 100)
                        progress_dialog['status_label'].config(text=text)
                        
                        # Update detail with savings info
                        saved = total_addresses - total_unique
                        progress_dialog['detail_label'].config(
                            text=f"Processed: {current}/{total} unique addresses (saved {saved} duplicate API calls)"
                        )
                    elif msg[0] == 'error':
                        progress_dialog['errors_text'].insert(tk.END, f"{msg[1]}\n")
                        progress_dialog['errors_text'].see(tk.END)
                    elif msg[0] == 'complete':
                        break
            except queue.Empty:
                pass
            
            if not stop_event.is_set():
                self.gui.root.after(100, update_progress)
        
        def process_addresses_with_api():
            """Process addresses in separate thread"""
            try:
                completed = 0
                errors = 0
                
                with ThreadPoolExecutor(max_workers=self.gui.api_threads_var.get()) as executor:
                    # Submit all tasks
                    future_to_addr = {}
                    
                    for i, addr in enumerate(unique_list):
                        api_symbol = crypto_mapping.get(addr.crypto_type)
                        if not api_symbol:
                            completed += 1
                            progress_queue.put(('update', completed, total_unique, 
                                              f"Skipped {addr.crypto_type} (not supported)"))
                            self.logger.debug(f"Skipped unsupported crypto type: {addr.crypto_type}")
                            continue
                        
                        future = executor.submit(self._process_single_address_with_logging, 
                                               addr, api_symbol, i, api_stats)
                        future_to_addr[future] = addr
                    
                    # Process results as they complete
                    for future in as_completed(future_to_addr):
                        if stop_event.is_set():
                            executor.shutdown(wait=False)
                            break
                        
                        addr = future_to_addr[future]
                        try:
                            api_data, call_stats = future.result()
                            key = (addr.address.lower(), addr.crypto_type)
                            api_results[key] = api_data
                            
                            completed += 1
                            
                            # Update statistics
                            if 'error' not in call_stats:
                                api_stats['success'] += 1
                                status = "Success"
                            else:
                                api_stats['errors'] += 1
                                status = f"Failed ({call_stats.get('error_type', 'Unknown')})"
                            
                            progress_queue.put(('update', completed, total_unique, 
                                              f"Processed {addr.address[:20]}... ({status})"))
                            
                        except Exception as e:
                            errors += 1
                            completed += 1
                            error_msg = f"Error for {addr.address[:20]}...: {str(e)}"
                            progress_queue.put(('error', error_msg))
                            progress_queue.put(('update', completed, total_unique, 
                                              f"Failed: {addr.address[:20]}..."))
                            self.logger.error(error_msg)
                            api_stats['errors'] += 1
                
                # Log final statistics
                self._log_api_statistics(api_stats, total_unique)
                
                # Final summary
                progress_queue.put(('update', total_unique, total_unique, 
                                  f"Complete! Success: {api_stats['success']}, Errors: {api_stats['errors']}"))
                time.sleep(1)  # Let user see the completion
                
            except Exception as e:
                self.logger.error(f"API processing thread error: {e}")
                progress_queue.put(('error', f"Fatal error: {str(e)}"))
            finally:
                progress_queue.put(('complete', None, None, None))
        
        # Start processing thread
        process_thread = threading.Thread(target=process_addresses_with_api)
        process_thread.daemon = True
        process_thread.start()
        
        # Start progress updates
        self.gui.root.after(100, update_progress)
        
        # Show dialog and wait
        progress_dialog['dialog'].transient(self.gui.root)
        progress_dialog['dialog'].grab_set()
        
        # Handle cancel button
        def on_cancel():
            stop_event.set()
            progress_dialog['status_label'].config(text="Cancelling...")
            progress_dialog['cancel_btn'].config(state=tk.DISABLED)
        
        progress_dialog['cancel_btn'].config(command=on_cancel)
        
        # Wait for completion
        self.gui.root.wait_window(progress_dialog['dialog'])
        
        # Apply enhanced data to ALL addresses (including duplicates)
        enhanced_count = 0
        for idx, addr in enumerate(addresses):
            key = (addr.address.lower(), addr.crypto_type)
            if key in api_results:
                api_data = api_results[key]
                for field, value in api_data.items():
                    setattr(addr, f'api_{field}', value)
                enhanced_count += 1
        
        # End API call tracking and log summary
        self.api_tracker.end_tracking()
        
        self.logger.info(f"API analysis complete. Applied data to {enhanced_count} addresses " +
                         f"(from {len(api_results)} unique API calls)")
        return addresses
    
    def _process_single_address_with_logging(self, addr, api_symbol, index, api_stats):
        """
        Process a single address with detailed logging and statistics.
        FIXED: Uses cluster root address for exposure API calls.
        """
        api_data = {}
        call_stats = {}
        
        self.logger.info(f"{'='*60}")
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
                    
                    # Track API call
                    self.api_tracker.record_api_call('balance', True, response_time, 200)
                    
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
                    api_data['cluster_root_address'] = cluster_root_address  # Ensure both are set
                    api_data['cluster_root_address'] = cluster_root_address  # Ensure this is stored
                    
                    if cluster_root_address != addr.address:
                        self.logger.info(f"  📍 Cluster root address: {cluster_root_address}")
                        self.logger.info(f"  📊 This cluster contains {api_data['address_count']} addresses")
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    error_str = str(e)
                    status_code = self._extract_status_code(error_str)
                    api_stats['status_codes'][status_code] += 1
                    api_stats['error_types'][f'balance_{status_code}'] += 1
                    
                    # Track failed API call
                    self.api_tracker.record_api_call('balance', False, response_time, status_code, error_str)
                    
                    self.logger.warning(f"✗ Balance API: FAILED ({status_code}) - {response_time:.2f}s")
                    self.logger.warning(f"  Error: {error_str}")
                    api_data['balance_error'] = error_str
                    # Still use the original address if balance API failed
                    cluster_root_address = addr.address
            
            # Get exposure information using CLUSTER ROOT ADDRESS
            if self.gui.api_exposure_var.get():
                self.logger.info(f"\n  Getting exposure for cluster root: {cluster_root_address[:20]}...")
                
                # Initialize exposure data structures
                api_data['sending_direct_exposure'] = []
                api_data['has_darknet_exposure'] = False  # Track darknet exposure
                api_data['cluster_root_address'] = cluster_root_address  # Store cluster address
                api_data['has_darknet_exposure'] = False  # Track if any darknet market exposure found
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
                    
                    # Track API call
                    self.api_tracker.record_api_call('balance', True, response_time, 200)
                    
                    self.logger.info(f"✓ Exposure API (SENDING): SUCCESS (200) - {response_time:.2f}s")
                    self.logger.debug(f"  Full SENDING exposure response: {sending_exposure_data}")
                    
                    # Extract services from response
                    services_data = self._extract_services_from_response(sending_exposure_data)
                    # Enhanced exposure logging for debugging
                    self.logger.info(f"EXPOSURE ANALYSIS for {addr.address[:20]}...")
                    
                    # Log all services found before filtering
                    all_services_count = len(services_data.get('direct', [])) + len(services_data.get('indirect', []))
                    self.logger.info(f"  Total services found: {all_services_count}")
                    
                    if all_services_count > 0:
                        self.logger.info("  Sample services (first 5):")
                        for i, service in enumerate(services_data.get('direct', [])[:5]):
                            name = service.get('name', 'Unknown')
                            category = service.get('category', 'Unknown')
                            percentage = service.get('percentage', 0)
                            self.logger.info(f"    {i+1}. {name} ({category}) - {percentage:.1f}%")
                    
                    # Log filtering results
                    filtered_count = len(api_data.get('sending_direct_exposure', []))
                    self.logger.info(f"  Services after exchange filtering: {filtered_count}")
                    
                    if filtered_count == 0 and all_services_count > 0:
                        self.logger.warning(f"  WARNING: All {all_services_count} services were filtered out!")
                        self.logger.warning("  This suggests the exchange detection logic may be too restrictive.")

                    # Enhanced exposure logging for debugging
                    self.logger.info(f"EXPOSURE ANALYSIS for {addr.address[:20]}...")
                    
                    # Log all services found before filtering
                    all_services_count = len(services_data.get('direct', [])) + len(services_data.get('indirect', []))
                    self.logger.info(f"  Total services found: {all_services_count}")
                    
                    if all_services_count > 0:
                        self.logger.info("  Sample services (first 5):")
                        for i, service in enumerate(services_data.get('direct', [])[:5]):
                            name = service.get('name', 'Unknown')
                            category = service.get('category', 'Unknown')
                            percentage = service.get('percentage', 0)
                            self.logger.info(f"    {i+1}. {name} ({category}) - {percentage:.1f}%")
                    
                    # Log filtering results
                    filtered_count = len(api_data.get('sending_direct_exposure', []))
                    self.logger.info(f"  Services after exchange filtering: {filtered_count}")
                    
                    if filtered_count == 0 and all_services_count > 0:
                        self.logger.warning(f"  WARNING: All {all_services_count} services were filtered out!")
                        self.logger.warning("  This suggests the exchange detection logic may be too restrictive.")

                    
                    # Process ONLY exchanges and darknet markets
                    # Direct exposure for SENDING
                    for service in services_data.get('direct', []):
                        service_info = {
                            'name': service.get('name', 'Unknown'),
                            'category': service.get('category', 'Unknown'),
                            'value': service.get('value', service.get('amount', service.get('sentAmount', 0))),
                            'percentage': service.get('percentage', 0)
                        }
                        is_relevant, is_darknet, service_type = self._is_exchange_or_darknet_service(service)
                        if is_relevant:
                            api_data['sending_direct_exposure'].append(service_info)
                            if service_type == 'darknet':
                                api_data['has_darknet_exposure'] = True
                                self.logger.info(f"    ⚠️  DARKNET MARKET DETECTED: {service_info['name']}")
                            if is_darknet:
                                api_data['has_darknet_exposure'] = True
                    
                    # Indirect exposure for SENDING
                    for service in services_data.get('indirect', []):
                        service_info = {
                            'name': service.get('name', 'Unknown'),
                            'category': service.get('category', 'Unknown'),
                            'value': service.get('value', service.get('amount', service.get('sentAmount', 0))),
                            'percentage': service.get('percentage', 0)
                        }
                        is_relevant, is_darknet, service_type = self._is_exchange_or_darknet_service(service)
                        if is_relevant:
                            api_data['sending_indirect_exposure'].append(service_info)
                            if service_type == 'darknet':
                                api_data['has_darknet_exposure'] = True
                                self.logger.info(f"    ⚠️  DARKNET MARKET DETECTED: {service_info['name']}")
                            if is_darknet:
                                api_data['has_darknet_exposure'] = True
                    
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
                    
                    # Track API call
                    self.api_tracker.record_api_call('balance', True, response_time, 200)
                    
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
                        is_relevant, is_darknet, service_type = self._is_exchange_or_darknet_service(service)
                        if is_relevant:
                            api_data['receiving_direct_exposure'].append(service_info)
                            if service_type == 'darknet':
                                api_data['has_darknet_exposure'] = True
                                self.logger.info(f"    ⚠️  DARKNET MARKET DETECTED: {service_info['name']}")
                            if is_darknet:
                                api_data['has_darknet_exposure'] = True
                    
                    # Indirect exposure for RECEIVING
                    for service in services_data.get('indirect', []):
                        service_info = {
                            'name': service.get('name', 'Unknown'),
                            'category': service.get('category', 'Unknown'),
                            'value': service.get('value', service.get('amount', service.get('receivedAmount', 0))),
                            'percentage': service.get('percentage', 0)
                        }
                        is_relevant, is_darknet, service_type = self._is_exchange_or_darknet_service(service)
                        if is_relevant:
                            api_data['receiving_indirect_exposure'].append(service_info)
                            if service_type == 'darknet':
                                api_data['has_darknet_exposure'] = True
                                self.logger.info(f"    ⚠️  DARKNET MARKET DETECTED: {service_info['name']}")
                            if is_darknet:
                                api_data['has_darknet_exposure'] = True
                    
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
                    
                    # Track API call
                    self.api_tracker.record_api_call('balance', True, response_time, 200)
                    
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
            
            # Set all API data as attributes on the address object
            for key, value in api_data.items():
                setattr(addr, f'api_{key}', value)
            
            # Specifically ensure cluster_root_address is set
            setattr(addr, 'api_cluster_root_address', cluster_root_address)
            
            self.logger.info(f"Set {len(api_data)} API attributes on address")
            self.logger.debug(f"Cluster root address set to: {cluster_root_address}")

            
        except Exception as e:
            self.logger.error(f"API error for {addr.address}: {e}")
            call_stats['error'] = str(e)
            call_stats['error_type'] = type(e).__name__
            raise
        
        return api_data, call_stats

    
    def _extract_services_from_response(self, response_data):
        """
        Extract services from various Chainalysis API response structures.
        Enhanced to handle both direct and indirect exposure data.
        
        Args:
            response_data: The API response data
            
        Returns:
            Dict with 'direct' and 'indirect' service lists
        """
        if not isinstance(response_data, dict):
            self.logger.debug("Response data is not a dictionary")
            return {'direct': [], 'indirect': []}
        
        result = {'direct': [], 'indirect': []}
        
        # Extract direct exposure services
        if 'directExposure' in response_data and isinstance(response_data['directExposure'], dict):
            direct_services = response_data['directExposure'].get('services', [])
            if isinstance(direct_services, list):
                result['direct'] = direct_services
                self.logger.debug(f"Found {len(direct_services)} direct exposure services")
        
        # Extract indirect exposure services
        if 'indirectExposure' in response_data and isinstance(response_data['indirectExposure'], dict):
            indirect_services = response_data['indirectExposure'].get('services', [])
            if isinstance(indirect_services, list):
                result['indirect'] = indirect_services
                self.logger.debug(f"Found {len(indirect_services)} indirect exposure services")
        
        # Handle alternative response structures (fallback for APIs that don't distinguish)
        if not result['direct'] and not result['indirect']:
            # Try other possible structures as fallback
            if 'services' in response_data:
                services = response_data.get('services', [])
                if isinstance(services, list):
                    result['direct'] = services
                    self.logger.debug(f"Found {len(services)} services in root (treating as direct)")
            elif 'items' in response_data:
                items = response_data.get('items', [])
                if isinstance(items, list):
                    result['direct'] = items
                    self.logger.debug(f"Found {len(items)} items (treating as direct)")
            elif 'data' in response_data and isinstance(response_data['data'], dict):
                services = response_data['data'].get('services', [])
                if isinstance(services, list):
                    result['direct'] = services
                    self.logger.debug(f"Found {len(services)} services in data.services (treating as direct)")
        
        return result

    def _is_relevant_exposure_service(self, service):
        """
        Check if service is an exchange or darknet market.
        Returns: (is_relevant, service_type) where service_type is 'exchange', 'darknet', or None
        """
        if not isinstance(service, dict):
            return False, None
        
        category = str(service.get('category', '')).lower()
        name = str(service.get('name', '')).lower()
        
        # Darknet market checks
        darknet_categories = ['darknet market', 'darknet marketplace', 'dark market', 
                            'darknet vendor', 'illicit market', 'dark web market']
        darknet_names = ['hydra', 'alphabay', 'dream market', 'silk road', 'empire market',
                        'white house market', 'dark0de', 'torrez', 'cannazon', 'versus',
                        'berlusconi', 'apollon', 'nightmare', 'wall street market']
        
        for dark_cat in darknet_categories:
            if dark_cat in category:
                return True, 'darknet'
        
        for dark_name in darknet_names:
            if dark_name in name:
                return True, 'darknet'
        
        # Exchange checks
        exchange_categories = ['exchange', 'centralized exchange', 'cex', 'dex', 
                             'decentralized exchange', 'trading platform', 'crypto exchange']
        
        for exc_cat in exchange_categories:
            if exc_cat in category:
                return True, 'exchange'
        
        # Major exchange names
        exchanges = [
            'binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okx', 'okex',
            'kucoin', 'gate.io', 'gate', 'bybit', 'bitstamp', 'gemini', 'bittrex',
            'poloniex', 'crypto.com', 'mexc', 'lbank', 'hotbit', 'phemex', 'deribit',
            'bitmex', 'uniswap', 'pancakeswap', 'sushiswap', 'curve', 'balancer',
            'upbit', 'bithumb', 'coinone', 'bitflyer', 'liquid', 'bitbank'
        ]
        
        for exchange in exchanges:
            if exchange in name:
                return True, 'exchange'
        
        return False, None

    def _is_exchange_service(self, service):
        """
        Determine if a service represents an exchange.
        Simple version that captures most exchanges.
        """
        if not isinstance(service, dict):
            return False
        
        # Get fields safely
        category = str(service.get('category', '')).lower()
        name = str(service.get('name', '')).lower()
        
        # Category check
        if any(term in category for term in ['exchange', 'cex', 'dex', 'trading']):
            return True
        
        # Name check - major exchanges
        exchanges = [
            'binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okx', 'okex',
            'kucoin', 'gate', 'bybit', 'bitstamp', 'gemini', 'bittrex', 'poloniex',
            'crypto.com', 'mexc', 'hotbit', 'phemex', 'deribit', 'bitmex',
            'uniswap', 'pancakeswap', 'sushiswap', 'curve', 'balancer'
        ]
        
        return any(ex in name for ex in exchanges)
    
    def _is_exchange_or_darknet_service(self, service):
        """
        Enhanced method to determine if a service represents an exchange or darknet market.
        
        This method uses comprehensive pattern matching to identify exchanges and
        darknet markets with improved accuracy and logging for debugging.
        
        Args:
            service (dict): Service dictionary from API response
            
        Returns:
            tuple: (is_relevant, is_darknet, service_type) where:
                   - is_relevant: True if exchange or darknet market
                   - is_darknet: True if darknet market
                   - service_type: 'exchange', 'darknet', or 'other'
                   
        Raises:
            Exception: If service data is invalid
        """
        if not isinstance(service, dict):
            self.logger.warning(f"Invalid service data type: {type(service)}")
            return False, False, 'other'
        
        try:
            # Get fields safely with detailed logging
            category = str(service.get('category', '')).lower().strip()
            name = str(service.get('name', '')).lower().strip()
            
            self.logger.debug(f"Analyzing service - Name: '{name}', Category: '{category}'")
            
            # Enhanced darknet market detection
            darknet_categories = [
                'darknet market', 'darknet marketplace', 'dark market', 'illicit market',
                'darknet vendor', 'dark web market', 'black market', 'illegal marketplace'
            ]
            
            darknet_names = [
                'hydra', 'alphabay', 'dream market', 'silk road', 'empire market', 
                'white house market', 'dark0de', 'torrez', 'cannazon', 'versus',
                'berlusconi', 'apollon', 'nightmare', 'wall street market',
                'darkmarket', 'darkbay', 'genesis'
            ]
            
            # Check for darknet markets first
            is_darknet = False
            for dark_cat in darknet_categories:
                if dark_cat in category:
                    is_darknet = True
                    self.logger.info(f"Darknet market detected by category: {name} ({category})")
                    break
            
            if not is_darknet:
                for dark_name in darknet_names:
                    if dark_name in name:
                        is_darknet = True
                        self.logger.info(f"Darknet market detected by name: {name}")
                        break
            
            # Enhanced exchange detection with comprehensive patterns
            is_exchange = False
            
            # Primary exchange categories
            exchange_categories = [
                'exchange', 'centralized exchange', 'cex', 'dex', 'decentralized exchange',
                'cryptocurrency exchange', 'crypto exchange', 'trading platform',
                'digital asset exchange', 'spot exchange', 'derivatives exchange',
                'trading service', 'exchange service', 'liquidity provider'
            ]
            
            for exc_cat in exchange_categories:
                if exc_cat in category:
                    is_exchange = True
                    self.logger.debug(f"Exchange detected by category: {name} ({category})")
                    break
            
            # Comprehensive exchange name detection
            if not is_exchange:
                # Major centralized exchanges
                major_exchanges = [
                    'binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okx', 'okex',
                    'kucoin', 'gate.io', 'gate', 'bybit', 'bitstamp', 'gemini', 'bittrex',
                    'poloniex', 'crypto.com', 'mexc', 'lbank', 'hotbit', 'phemex', 
                    'deribit', 'bitmex', 'ftx', 'bitget', 'ascendex', 'probit'
                ]
                
                # Regional and smaller exchanges
                regional_exchanges = [
                    'upbit', 'bithumb', 'coinone', 'bitflyer', 'liquid', 'bitbank',
                    'coincheck', 'zaif', 'bitpoint', 'coinex', 'bigone', 'zb.com',
                    'hitbtc', 'yobit', 'exmo', 'livecoin', 'cex.io', 'bitso',
                    'mercado bitcoin', 'foxbit', 'novadax', 'braziliex'
                ]
                
                # DEX and DeFi protocols
                dex_protocols = [
                    'uniswap', 'pancakeswap', 'sushiswap', 'curve', 'balancer',
                    '1inch', 'paraswap', 'kyber', 'bancor', 'airswap', 'loopring',
                    'dydx', 'compound', 'aave', 'maker', 'synthetix'
                ]
                
                all_exchanges = major_exchanges + regional_exchanges + dex_protocols
                
                for exchange in all_exchanges:
                    if exchange in name:
                        is_exchange = True
                        self.logger.debug(f"Exchange detected by name match: {name} -> {exchange}")
                        break
                
                # Additional pattern matching for exchange-like services
                if not is_exchange:
                    exchange_patterns = [
                        'exchange', 'trading', 'swap', 'dex', 'cex', 'market',
                        'trade', 'broker', 'otc', 'liquidity'
                    ]
                    
                    for pattern in exchange_patterns:
                        if pattern in name and len(name) > 3:  # Avoid false positives
                            # Additional validation to avoid false matches
                            non_exchange_patterns = ['wallet', 'mining', 'pool', 'bridge']
                            is_non_exchange = any(ne_pattern in name for ne_pattern in non_exchange_patterns)
                            
                            if not is_non_exchange:
                                is_exchange = True
                                self.logger.debug(f"Exchange detected by pattern: {name} (pattern: {pattern})")
                                break
            
            # Determine service type and relevance
            if is_darknet:
                service_type = 'darknet'
                is_relevant = True
            elif is_exchange:
                service_type = 'exchange'
                is_relevant = True
            else:
                service_type = 'other'
                is_relevant = False
            
            if is_relevant:
                self.logger.debug(f"Service classified: {name}")
            else:
                self.logger.debug(f"Service not classified as exchange/darknet: {name} ({category})")
            
            return is_relevant, is_darknet, service_type
            
        except Exception as e:
            self.logger.error(f"Error analyzing service {service}: {e}")
            return False, False, 'other'

    def _extract_all_exposure_services(self, sending_exposure_data, receiving_exposure_data, addr):
        """
        Extract and log ALL services from exposure data for debugging.
        This helps identify why some exchanges might be missed.
        """
        all_services = {
            'sending_direct': [],
            'sending_indirect': [],
            'receiving_direct': [],
            'receiving_indirect': []
        }
        
        # Extract from sending
        if sending_exposure_data:
            services = self._extract_services_from_response(sending_exposure_data)
            all_services['sending_direct'] = services.get('direct', [])
            all_services['sending_indirect'] = services.get('indirect', [])
        
        # Extract from receiving  
        if receiving_exposure_data:
            services = self._extract_services_from_response(receiving_exposure_data)
            all_services['receiving_direct'] = services.get('direct', [])
            all_services['receiving_indirect'] = services.get('indirect', [])
        
        # Log all services found (not just exchanges)
        self.logger.info(f"\nALL SERVICES found for {addr.address[:20]}...:")
            
        for direction_type, services_list in all_services.items():
            if services_list:
                self.logger.info(f"\n{direction_type.upper()} ({len(services_list)} services):")
                for service in services_list[:10]:  # Show first 10
                    name = service.get('name', 'Unknown')
                    category = service.get('category', 'Unknown')
                    percentage = service.get('percentage', 0)
                    value = service.get('value', 0)
                    is_exchange = self._is_exchange_service(service)
                    
                    self.logger.info(f"    - {name} ({category}) - {percentage:.1f}% or ${value:,.0f} - Exchange: {is_exchange}")
                
                if len(services_list) > 10:
                    self.logger.info(f"    ... and {len(services_list) - 10} more services")
        
        return all_services
    
    def _extract_cluster_info_from_response(self, response_data):
        """
        Extract cluster information from API response.
        NEW: Enhanced parsing for all Chainalysis cluster response formats.
        
        Args:
            response_data: The API response data
            
        Returns:
            Dict with cluster info or None
        """
        if not isinstance(response_data, dict):
            self.logger.debug("Cluster response data is not a dictionary")
            return None
        
        # Try different response formats
        cluster_info = None
        
        # Format 1: items[0] (most common)
        if 'items' in response_data and isinstance(response_data['items'], list) and len(response_data['items']) > 0:
            cluster_info = response_data['items'][0]
            self.logger.debug("Found cluster info in items[0]")
        
        # Format 2: Direct response
        elif 'name' in response_data:
            cluster_info = response_data
            self.logger.debug("Found cluster info in root response")
        
        # Format 3: cluster object
        elif 'cluster' in response_data:
            cluster_info = response_data['cluster']
            self.logger.debug("Found cluster info in cluster object")
        
        # Format 4: data.cluster
        elif 'data' in response_data and isinstance(response_data['data'], dict):
            if 'cluster' in response_data['data']:
                cluster_info = response_data['data']['cluster']
                self.logger.debug("Found cluster info in data.cluster")
            elif 'name' in response_data['data']:
                cluster_info = response_data['data']
                self.logger.debug("Found cluster info in data object")
        
        # Format 5: result.cluster (alternative structure)
        elif 'result' in response_data and isinstance(response_data['result'], dict):
            cluster_info = response_data['result']
            self.logger.debug("Found cluster info in result object")
        
        return cluster_info
    
    def _extract_status_code(self, error_str):
        """Extract HTTP status code from error string"""
        error_lower = error_str.lower()
        if '503' in error_str:
            return 503
        elif '404' in error_str:
            return 404
        elif '403' in error_str:
            return 403
        elif '401' in error_str:
            return 401
        elif '400' in error_str:
            return 400
        elif '429' in error_str:
            return 429  # Rate limit
        elif 'timeout' in error_lower:
            return 408  # Request timeout
        elif 'connection' in error_lower:
            return 0    # Connection error
        else:
            return 500  # Generic server error
    
    def _log_api_statistics(self, api_stats, total_unique):
        """Log comprehensive API call statistics"""
        self.logger.info("\n" + "="*80)
        self.logger.info("API CALL STATISTICS")
        self.logger.info("="*80)
        self.logger.info(f"Total unique addresses processed: {total_unique}")
        self.logger.info(f"Successful API calls: {api_stats['success']}")
        self.logger.info(f"Failed API calls: {api_stats['errors']}")
        
        if api_stats['status_codes']:
            self.logger.info("\nHTTP Status Code Distribution:")
            for code, count in sorted(api_stats['status_codes'].items()):
                percentage = (count / sum(api_stats['status_codes'].values())) * 100
                self.logger.info(f"  {code}: {count} ({percentage:.1f}%)")
        
        if api_stats['response_times']:
            avg_time = sum(api_stats['response_times']) / len(api_stats['response_times'])
            min_time = min(api_stats['response_times'])
            max_time = max(api_stats['response_times'])
            self.logger.info(f"\nResponse Time Statistics:")
            self.logger.info(f"  Average: {avg_time:.2f}s")
            self.logger.info(f"  Minimum: {min_time:.2f}s")
            self.logger.info(f"  Maximum: {max_time:.2f}s")
        
        if api_stats['error_types']:
            self.logger.info("\nError Type Distribution:")
            for error_type, count in sorted(api_stats['error_types'].items()):
                self.logger.info(f"  {error_type}: {count}")
        
        self.logger.info("="*80)
    
    def _create_api_progress_dialog(self):
        """Create a progress dialog for API processing"""
        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Chainalysis API Processing")
        dialog.geometry("600x400")
        dialog.resizable(False, False)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Processing Addresses with Chainalysis API", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame, variable=progress_var, 
                                      maximum=100, length=500, mode='determinate')
        progress_bar.pack(fill='x', pady=(0, 10))
        
        # Status label
        status_label = ttk.Label(main_frame, text="Initializing...")
        status_label.pack(pady=(0, 5))
        
        # Detail label
        detail_label = ttk.Label(main_frame, text="", font=('Arial', 9))
        detail_label.pack(pady=(0, 20))
        
        # Frame for API options display
        options_frame = ttk.LabelFrame(main_frame, text="Processing Options", padding="10")
        options_frame.pack(fill='x', pady=(0, 20))
        
        options_text = []
        if self.gui.api_balance_var.get():
            options_text.append("• Getting balance information")
        if self.gui.api_exposure_var.get():
            options_text.append("• Analyzing exchange exposure (direct & indirect)")
        if self.gui.api_cluster_info_var.get():
            options_text.append("• Retrieving cluster information")
        options_text.append(f"• Using {self.gui.api_threads_var.get()} concurrent threads")
        options_text.append(f"• Output currency: {self.gui.api_currency_var.get()}")
        
        for option in options_text:
            ttk.Label(options_frame, text=option, font=('Arial', 9)).pack(anchor='w')
        
        # Errors frame
        errors_frame = ttk.LabelFrame(main_frame, text="Errors", padding="10")
        errors_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        errors_text = tk.Text(errors_frame, height=6, width=60, font=('Consolas', 8))
        errors_scroll = ttk.Scrollbar(errors_frame, orient="vertical", command=errors_text.yview)
        errors_text.configure(yscrollcommand=errors_scroll.set)
        errors_text.pack(side='left', fill='both', expand=True)
        errors_scroll.pack(side='right', fill='y')
        
        # Cancel button
        cancel_btn = ttk.Button(main_frame, text="Cancel", style="Danger.TButton")
        cancel_btn.pack()
        
        # Store references
        return {
            'dialog': dialog,
            'progress_var': progress_var,
            'progress_bar': progress_bar,
            'status_label': status_label,
            'detail_label': detail_label,
            'errors_text': errors_text,
            'cancel_btn': cancel_btn
        }
    
