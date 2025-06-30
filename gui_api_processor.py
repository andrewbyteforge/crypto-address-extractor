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


class APIProcessor:
    """Handles API processing with progress tracking."""
    
    def __init__(self, parent_gui):
        self.gui = parent_gui
        self.logger = logging.getLogger(__name__)
    
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
        
        self.logger.info(f"🚀 BULK DEDUPLICATION: {total_count} → {unique_count} addresses")
        self.logger.info(f"💰 API CALL SAVINGS: {duplicate_savings} duplicate calls avoided")
        
        return dict(address_map)

    def enhance_with_chainalysis_api(self, addresses: List[ExtractedAddress]) -> List[ExtractedAddress]:
        """
        Enhanced version with progress tracking and proper threading.
        Now avoids duplicate API calls for the same address and includes Solana support.
        """
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
            'SOL':   'SOL',        # ← FIXED: Added Solana support
            'SOLANA': 'SOL',       # ← FIXED: Added Solana alias
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
        
        self.logger.info(f"API analysis complete. Applied data to {enhanced_count} addresses " +
                        f"(from {len(api_results)} unique API calls)")
        return addresses
    
    def _process_single_address_with_logging(self, addr, api_symbol, index, api_stats):
        """
        Process a single address with detailed logging and statistics.
        UPDATED: Enhanced to handle all Chainalysis API response formats including Solana.
        """
        api_data = {}
        call_stats = {}
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Processing address {index + 1}: {addr.address}")
        self.logger.info(f"Crypto type: {api_symbol}")
        
        try:
            # Add small delay to prevent rate limiting
            if index > 0:
                time.sleep(0.1)
            
            # Track overall timing
            overall_start = time.time()
            
            # Get balance information
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
                    
                    # Enhanced balance data extraction
                    api_data['balance'] = balance_data.get('balance', 0)
                    api_data['total_received'] = balance_data.get('totalReceivedAmount', 0)
                    api_data['total_sent'] = balance_data.get('totalSentAmount', 0)
                    api_data['transfer_count'] = balance_data.get('transferCount', 0)
                    api_data['deposit_count'] = balance_data.get('depositCount', 0)
                    api_data['withdrawal_count'] = balance_data.get('withdrawalCount', 0)
                    api_data['address_count'] = balance_data.get('addressCount', 1)
                    api_data['total_fees'] = balance_data.get('totalFeesAmount', 0)
                    api_data['root_address'] = balance_data.get('rootAddress', addr.address)
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    error_str = str(e)
                    
                    # Extract status code from error
                    status_code = self._extract_status_code(error_str)
                    api_stats['status_codes'][status_code] += 1
                    api_stats['error_types'][f'balance_{status_code}'] += 1
                    
                    self.logger.warning(f"✗ Balance API: FAILED ({status_code}) - {response_time:.2f}s")
                    self.logger.warning(f"  Error: {error_str}")
                    
                    if status_code == 503:
                        raise Exception("API service temporarily unavailable")
                    api_data['balance_error'] = error_str
            
            # Enhanced exposure information - check BOTH directions with better parsing
            if self.gui.api_exposure_var.get():
                exchange_exposure = {
                    'direct': [],
                    'indirect': []
                }
                exposure_direction = None
                
                # Check SENDING direction first
                start_time = time.time()
                try:
                    self.logger.debug(f"Calling get_exposure_by_service (SENDING) for {addr.address[:20]}...")
                    
                    sent_exposure_data = self.gui.api_service.get_exposure_by_service(
                        addr.address, 
                        api_symbol, 
                        'SENDING',
                        self.gui.api_currency_var.get()
                    )
                    
                    response_time = time.time() - start_time
                    api_stats['response_times'].append(response_time)
                    api_stats['status_codes'][200] += 1
                    
                    self.logger.info(f"✓ Exposure API (SENDING): SUCCESS (200) - {response_time:.2f}s")
                    self.logger.debug(f"  Full SENDING exposure response: {sent_exposure_data}")
                    
                    # Extract both direct and indirect services
                    services_data = self._extract_services_from_response(sent_exposure_data)
                    
                    # Process direct exposure
                    for service in services_data.get('direct', []):
                        if self._is_exchange_service(service):
                            exchange_exposure['direct'].append({
                                'name': service.get('name', 'Unknown'),
                                'category': service.get('category', 'Unknown'),
                                'value': service.get('value', service.get('amount', service.get('sentAmount', 0))),
                                'percentage': service.get('percentage', 0),
                                'direction': 'SENDING',
                                'type': 'direct'
                            })
                    
                    # Process indirect exposure
                    for service in services_data.get('indirect', []):
                        if self._is_exchange_service(service):
                            exchange_exposure['indirect'].append({
                                'name': service.get('name', 'Unknown'),
                                'category': service.get('category', 'Unknown'),
                                'value': service.get('value', service.get('amount', service.get('sentAmount', 0))),
                                'percentage': service.get('percentage', 0),
                                'direction': 'SENDING',
                                'type': 'indirect'
                            })
                    
                    if exchange_exposure['direct'] or exchange_exposure['indirect']:
                        exposure_direction = 'SENDING'
                        self.logger.debug(f"  Found {len(exchange_exposure['direct'])} direct and {len(exchange_exposure['indirect'])} indirect exchange exposures (SENDING)")
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    error_str = str(e)
                    status_code = self._extract_status_code(error_str)
                    api_stats['status_codes'][status_code] += 1
                    api_stats['error_types'][f'exposure_sent_{status_code}'] += 1
                    self.logger.warning(f"✗ Exposure API (SENDING): FAILED ({status_code}) - {response_time:.2f}s")
                    self.logger.warning(f"  Error: {error_str}")
                
                # Check RECEIVING direction if no SENDING exposure found
                if not (exchange_exposure['direct'] or exchange_exposure['indirect']):
                    start_time = time.time()
                    try:
                        self.logger.debug(f"Calling get_exposure_by_service (RECEIVING) for {addr.address[:20]}...")
                        
                        received_exposure_data = self.gui.api_service.get_exposure_by_service(
                            addr.address, 
                            api_symbol, 
                            'RECEIVING',
                            self.gui.api_currency_var.get()
                        )
                        
                        response_time = time.time() - start_time
                        api_stats['response_times'].append(response_time)
                        api_stats['status_codes'][200] += 1
                        
                        self.logger.info(f"✓ Exposure API (RECEIVING): SUCCESS (200) - {response_time:.2f}s")
                        self.logger.debug(f"  Full RECEIVING exposure response: {received_exposure_data}")
                        
                        # Extract both direct and indirect services
                        services_data = self._extract_services_from_response(received_exposure_data)
                        
                        # Process direct exposure for RECEIVING
                        for service in services_data.get('direct', []):
                            if self._is_exchange_service(service):
                                exchange_exposure['direct'].append({
                                    'name': service.get('name', 'Unknown'),
                                    'category': service.get('category', 'Unknown'),
                                    'value': service.get('value', service.get('amount', service.get('receivedAmount', 0))),
                                    'percentage': service.get('percentage', 0),
                                    'direction': 'RECEIVING',
                                    'type': 'direct'
                                })
                        
                        # Process indirect exposure for RECEIVING
                        for service in services_data.get('indirect', []):
                            if self._is_exchange_service(service):
                                exchange_exposure['indirect'].append({
                                    'name': service.get('name', 'Unknown'),
                                    'category': service.get('category', 'Unknown'),
                                    'value': service.get('value', service.get('amount', service.get('receivedAmount', 0))),
                                    'percentage': service.get('percentage', 0),
                                    'direction': 'RECEIVING',
                                    'type': 'indirect'
                                })
                        
                        if exchange_exposure['direct'] or exchange_exposure['indirect']:
                            exposure_direction = 'RECEIVING'
                            self.logger.debug(f"  Found {len(exchange_exposure['direct'])} direct and {len(exchange_exposure['indirect'])} indirect exchange exposures (RECEIVING)")
                        
                    except Exception as e:
                        response_time = time.time() - start_time
                        error_str = str(e)
                        status_code = self._extract_status_code(error_str)
                        api_stats['status_codes'][status_code] += 1
                        api_stats['error_types'][f'exposure_received_{status_code}'] += 1
                        self.logger.warning(f"✗ Exposure API (RECEIVING): FAILED ({status_code}) - {response_time:.2f}s")
                        self.logger.warning(f"  Error: {error_str}")
                
                # Store enhanced results
                api_data['exchange_exposure'] = exchange_exposure
                api_data['has_direct_exposure'] = len(exchange_exposure.get('direct', [])) > 0
                api_data['has_indirect_exposure'] = len(exchange_exposure.get('indirect', [])) > 0
                if exposure_direction:
                    api_data['exposure_direction'] = exposure_direction
                
                # Set the enhanced attributes on the address object
                if exchange_exposure['direct'] or exchange_exposure['indirect']:
                    # Set separated direct and indirect exposure
                    setattr(addr, 'api_direct_exposure', exchange_exposure.get('direct', []))
                    setattr(addr, 'api_indirect_exposure', exchange_exposure.get('indirect', []))
                    
                    # Also set combined exposure for backward compatibility
                    all_exposures = exchange_exposure.get('direct', []) + exchange_exposure.get('indirect', [])
                    setattr(addr, 'api_exchange_exposure', all_exposures)
                    
                    # Log summary
                    total_direct = len(exchange_exposure.get('direct', []))
                    total_indirect = len(exchange_exposure.get('indirect', []))
                    self.logger.info(f"  Found {total_direct} direct and {total_indirect} indirect exchange exposures")
                else:
                    # Set empty lists if no exposure data
                    setattr(addr, 'api_direct_exposure', [])
                    setattr(addr, 'api_indirect_exposure', [])
                    setattr(addr, 'api_exchange_exposure', [])
                    self.logger.debug("  No exchange exposure found in either direction")
            
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
                        api_data['cluster_root_address'] = cluster_info.get('rootAddress', addr.address)
                        self.logger.debug(f"  Cluster: {api_data['cluster_name']} ({api_data['cluster_category']})")
                    else:
                        self.logger.debug("  No cluster information found in response")
                        api_data['cluster_name'] = 'Unknown'
                        api_data['cluster_category'] = 'Unknown'
                        api_data['cluster_root_address'] = addr.address
                        
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

    def _is_exchange_service(self, service):
        """
        Determine if a service represents an exchange.
        Enhanced to handle None values properly to prevent 'NoneType' has no attribute 'lower' errors.
        
        Args:
            service: Service dictionary from API response
            
        Returns:
            bool: True if service is an exchange, False otherwise
        """
        if not isinstance(service, dict):
            return False
        
        # Get category and name safely
        category = service.get('category', '')
        name = service.get('name', '')
        
        # Ensure we have strings before calling .lower()
        if not isinstance(category, str):
            category = str(category) if category is not None else ''
        if not isinstance(name, str):
            name = str(name) if name is not None else ''
        
        category_lower = category.lower()
        name_lower = name.lower()
        
        # Check if it's an exchange based on category
        exchange_categories = ['exchange', 'centralized exchange', 'dex', 'decentralized exchange']
        for exc_cat in exchange_categories:
            if exc_cat in category_lower:
                return True
        
        # Check known exchange names
        known_exchanges = [
            'binance', 'coinbase', 'kraken', 'bitfinex', 'huobi', 'okex', 'ftx',
            'kucoin', 'gate.io', 'bybit', 'bitstamp', 'gemini', 'bittrex', 'poloniex',
            'bitmart', 'crypto.com', 'mexc', 'lbank', 'hotbit', 'ascendex'
        ]
        
        for exchange in known_exchanges:
            if exchange in name_lower:
                return True
        
        return False
    
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