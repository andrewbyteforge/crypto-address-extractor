import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import threading
import queue
import time
from datetime import datetime
import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

class APITab:
    def __init__(self, parent, api_service=None):
        self.parent = parent
        self.api_service = api_service
        self.addresses_df = None
        self.results_queue = queue.Queue()
        self.is_processing = False
        self.current_thread = None
        self.results = []
        self.logger = logging.getLogger(__name__)
        
        # Set up more detailed logging
        self.logger.setLevel(logging.DEBUG)
        
        # Add console handler if not already present
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        self.logger.info("Initializing API Tab")
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Results section
        main_frame.columnconfigure(1, weight=1)
        
        # File Upload Section
        upload_frame = ttk.LabelFrame(main_frame, text="File Upload", padding="10")
        upload_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(upload_frame, text="Select CSV/Excel file:").grid(row=0, column=0, sticky=tk.W)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(upload_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=0, column=1, padx=(10, 10), sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(upload_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2, sticky=tk.W)
        
        load_btn = ttk.Button(upload_frame, text="Load File", command=self.load_file)
        load_btn.grid(row=0, column=3, padx=(10, 0), sticky=tk.W)
        
        # File info
        self.file_info_label = ttk.Label(upload_frame, text="No file loaded")
        self.file_info_label.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky=tk.W)
        
        upload_frame.columnconfigure(1, weight=1)
        
        # API Endpoints Selection
        endpoints_frame = ttk.LabelFrame(main_frame, text="Select API Endpoints", padding="10")
        endpoints_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Checkboxes for endpoints
        self.endpoint_vars = {}
        endpoints = [
            ("Cluster Name and Category", "cluster_info"),
            ("Cluster Balance", "cluster_balance"),
            ("Cluster Addresses", "cluster_addresses"),
            ("Cluster Transactions", "cluster_transactions"),
            ("Cluster Counterparties", "cluster_counterparties"),
            ("Transaction Details", "transaction_details"),
            ("Exposure by Category", "exposure_category"),
            ("Exposure by Service", "exposure_service")
        ]
        
        for i, (name, key) in enumerate(endpoints):
            var = tk.BooleanVar()
            self.endpoint_vars[key] = var
            cb = ttk.Checkbutton(endpoints_frame, text=name, variable=var)
            cb.grid(row=i // 2, column=i % 2, sticky=tk.W, padx=(0, 20), pady=2)
        
        # Options Section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Output currency option
        ttk.Label(options_frame, text="Output Currency:").grid(row=0, column=0, sticky=tk.W)
        self.output_currency_var = tk.StringVar(value="NATIVE")
        currency_combo = ttk.Combobox(options_frame, textvariable=self.output_currency_var, 
                                      values=["NATIVE", "USD"], state="readonly", width=10)
        currency_combo.grid(row=0, column=1, padx=(10, 20), sticky=tk.W)
        
        # Concurrent threads (replacing batch size)
        ttk.Label(options_frame, text="Concurrent Threads:").grid(row=0, column=2, sticky=tk.W)
        self.max_workers_var = tk.IntVar(value=3)  # Reduced from 10 to 3
        workers_spin = ttk.Spinbox(options_frame, from_=1, to=50, increment=1, 
                                 textvariable=self.max_workers_var, width=10)
        workers_spin.grid(row=0, column=3, padx=(10, 20), sticky=tk.W)
        
        # Performance mode
        ttk.Label(options_frame, text="Mode:").grid(row=0, column=4, sticky=tk.W)
        self.fast_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Fast Mode (Concurrent)", 
                       variable=self.fast_mode_var).grid(row=0, column=5, padx=(10, 0), sticky=tk.W)
        
        # Control Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        self.process_btn = ttk.Button(control_frame, text="Process Addresses", 
                                     command=self.start_processing, state=tk.DISABLED)
        self.process_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_processing, 
                                  state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.export_btn = ttk.Button(control_frame, text="Export Results", 
                                    command=self.export_results, state=tk.DISABLED)
        self.export_btn.grid(row=0, column=2)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.progress_label = ttk.Label(main_frame, text="Ready")
        self.progress_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Results Section with Filtering
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.rowconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        # Filter controls
        filter_frame = ttk.Frame(results_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by Asset:").pack(side=tk.LEFT, padx=(0, 10))
        self.asset_filter_var = tk.StringVar(value="All")
        self.asset_filter_combo = ttk.Combobox(filter_frame, textvariable=self.asset_filter_var, 
                                               values=["All"], state="readonly", width=15)
        self.asset_filter_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.asset_filter_combo.bind("<<ComboboxSelected>>", self.apply_asset_filter)
        
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.apply_search_filter)
        
        # Clear filters button
        ttk.Button(filter_frame, text="Clear Filters", command=self.clear_filters).pack(side=tk.LEFT)
        
        # Results table with scrollbars
        table_frame = ttk.Frame(results_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Create Treeview for results
        columns = ('Asset', 'Balance', 'Received', 'Sent', 'Transfers', 'Status', 'Details')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='tree headings', height=15)
        
        # Define column headings and widths
        self.results_tree.heading('#0', text='Address')
        self.results_tree.heading('Asset', text='Asset')
        self.results_tree.heading('Balance', text='Balance')
        self.results_tree.heading('Received', text='Total Received')
        self.results_tree.heading('Sent', text='Total Sent')
        self.results_tree.heading('Transfers', text='Transfers')
        self.results_tree.heading('Status', text='Status')
        self.results_tree.heading('Details', text='Details')
        
        # Column widths
        self.results_tree.column('#0', width=300)
        self.results_tree.column('Asset', width=60)
        self.results_tree.column('Balance', width=120)
        self.results_tree.column('Received', width=120)
        self.results_tree.column('Sent', width=120)
        self.results_tree.column('Transfers', width=80)
        self.results_tree.column('Status', width=80)
        self.results_tree.column('Details', width=200)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack table and scrollbars
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure tags for styling
        self.results_tree.tag_configure('success', background='#e8f5e9')
        self.results_tree.tag_configure('error', background='#ffebee')
        self.results_tree.tag_configure('hover', background='#e3f2fd')
        
        # Bind hover events
        self.results_tree.bind('<Motion>', self.on_hover)
        self.results_tree.bind('<Leave>', self.on_leave)
        self.results_tree.bind('<Double-Button-1>', self.on_row_double_click)
        
        # Store the last hovered item
        self.last_hovered = None
        
        # Summary label
        self.summary_label = ttk.Label(results_frame, text="No results yet", font=('Arial', 10, 'italic'))
        self.summary_label.grid(row=2, column=0, pady=(10, 0), sticky=tk.W)
        
        # Configure main_frame grid weights
        main_frame.rowconfigure(6, weight=1)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select file",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file_path_var.set(filename)
            
    def load_file(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("No File", "Please select a file first.")
            return
        
        self.logger.info(f"Starting to load file: {file_path}")
        
        try:
            # Load file based on extension
            if file_path.lower().endswith('.csv'):
                self.logger.debug("Loading CSV file")
                self.addresses_df = pd.read_csv(file_path)
            else:
                self.logger.debug("Loading Excel file")
                self.addresses_df = pd.read_excel(file_path)
            
            self.logger.info(f"Raw data loaded: {len(self.addresses_df)} rows")
            
            # Clean the data
            self.addresses_df = self.addresses_df.dropna(how='all')  # Remove blank rows
            self.logger.debug(f"After removing blank rows: {len(self.addresses_df)} rows")
            
            # Check for required columns
            if len(self.addresses_df.columns) < 2:
                self.logger.error("File has less than 2 columns")
                messagebox.showerror("Invalid File", 
                    "File must have at least 2 columns (address and asset type)")
                return
            
            # Assume first column is address, second is asset
            self.addresses_df.columns = ['address', 'asset'] + list(self.addresses_df.columns[2:])
            self.logger.debug(f"Columns renamed. First 5 rows:\n{self.addresses_df.head()}")
            
            # Remove rows with missing address or asset
            initial_count = len(self.addresses_df)
            self.addresses_df = self.addresses_df.dropna(subset=['address', 'asset'])
            self.logger.info(f"Removed {initial_count - len(self.addresses_df)} rows with missing address/asset")
            
            # Clean address and asset columns
            self.addresses_df['address'] = self.addresses_df['address'].astype(str).str.strip()
            self.addresses_df['asset'] = self.addresses_df['asset'].astype(str).str.strip().str.upper()
            
            # Remove empty addresses
            before_empty = len(self.addresses_df)
            self.addresses_df = self.addresses_df[self.addresses_df['address'] != '']
            self.logger.debug(f"Removed {before_empty - len(self.addresses_df)} empty addresses")
            
            # Validate asset types (based on API documentation)
            valid_assets = ['BTC', 'ETH', 'BCH', 'LTC', 'DOGE', 'DASH', 'XRP', 'ZEC', 'EOS', 'BSV', 
                          'ALGO', 'SOL', 'TRX', 'ETC', 'USDT', 'USDC', 'DAI', 'WBTC', 'LINK', 
                          'UNI', 'AAVE', 'COMP', 'MKR', 'SNX', 'YFI', 'SUSHI', 'BAT', 'ZRX']
            
            # Check for invalid assets
            invalid_assets = self.addresses_df[~self.addresses_df['asset'].isin(valid_assets)]
            if len(invalid_assets) > 0:
                self.logger.warning(f"Found {len(invalid_assets)} rows with unsupported assets")
                self.logger.debug(f"Invalid assets: {invalid_assets['asset'].unique()}")
                
                invalid_list = invalid_assets['asset'].unique()[:10]  # Show first 10
                warning_msg = f"Warning: Found {len(invalid_assets)} rows with unsupported assets:\n"
                warning_msg += ", ".join(invalid_list)
                if len(invalid_assets['asset'].unique()) > 10:
                    warning_msg += f", and {len(invalid_assets['asset'].unique()) - 10} more..."
                warning_msg += "\n\nThese rows will be skipped during processing."
                messagebox.showwarning("Unsupported Assets", warning_msg)
            
            # Filter to only valid assets
            before_filter = len(self.addresses_df)
            self.addresses_df = self.addresses_df[self.addresses_df['asset'].isin(valid_assets)]
            self.logger.info(f"Filtered out {before_filter - len(self.addresses_df)} rows with invalid assets")
            
            final_count = len(self.addresses_df)
            removed_count = initial_count - final_count
            
            # Log final summary
            self.logger.info(f"File loading complete: {final_count} valid addresses loaded")
            self.logger.info(f"Asset distribution: {self.addresses_df['asset'].value_counts().to_dict()}")
            
            # Update UI
            info_text = f"Loaded {final_count} valid addresses"
            if removed_count > 0:
                info_text += f" ({removed_count} invalid/unsupported rows removed)"
            
            self.file_info_label.config(text=info_text)
            self.process_btn.config(state=tk.NORMAL)
            
            # Clear previous results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            self.results = []
            self.summary_label.config(text="Ready to process")
            
            # Show asset distribution
            asset_counts = self.addresses_df['asset'].value_counts()
            info_text += "\n"
            for asset, count in asset_counts.items():
                info_text += f"{asset}: {count} | "
            self.file_info_label.config(text=info_text.rstrip(" | "))
            
        except Exception as e:
            self.logger.error(f"Failed to load file: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            
    def start_processing(self):
        if self.addresses_df is None or len(self.addresses_df) == 0:
            messagebox.showwarning("No Data", "Please load a file with addresses first.")
            return
            
        # Check if at least one endpoint is selected
        selected_endpoints = [key for key, var in self.endpoint_vars.items() if var.get()]
        if not selected_endpoints:
            messagebox.showwarning("No Endpoints", "Please select at least one API endpoint.")
            return
        
        self.logger.info("="*80)
        self.logger.info("STARTING NEW PROCESSING SESSION")
        self.logger.info("="*80)
        self.logger.info(f"Total addresses to process: {len(self.addresses_df)}")
        self.logger.info(f"Selected endpoints: {selected_endpoints}")
        self.logger.info(f"Fast mode: {self.fast_mode_var.get()}")
        self.logger.info(f"Max workers: {self.max_workers_var.get()}")
        self.logger.info(f"Output currency: {self.output_currency_var.get()}")
        
        # Disable buttons
        self.process_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.DISABLED)
        
        # Clear results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.results = []
        
        # Start processing in a separate thread
        self.is_processing = True
        self.current_thread = threading.Thread(target=self.process_addresses)
        self.current_thread.daemon = True
        self.current_thread.start()
        
        self.logger.info("Processing thread started")
        
        # Start monitoring the queue
        self.parent.after(50, self.check_queue)
        
    def stop_processing(self):
        self.is_processing = False
        self.progress_label.config(text="Stopping...")
        
    def process_addresses(self):
        try:
            total_addresses = len(self.addresses_df)
            output_currency = self.output_currency_var.get()
            selected_endpoints = [key for key, var in self.endpoint_vars.items() if var.get()]
            
            # Track start time for performance metrics
            start_time = time.time()
            
            if self.fast_mode_var.get():
                # Use concurrent processing
                self.process_addresses_concurrent(total_addresses, output_currency, selected_endpoints, start_time)
            else:
                # Use sequential processing (legacy mode)
                self.process_addresses_sequential(total_addresses, output_currency, selected_endpoints, start_time)
                
        except Exception as e:
            self.results_queue.put(('error', str(e)))
    
    def process_addresses_concurrent(self, total_addresses, output_currency, selected_endpoints, start_time):
        """Process addresses using concurrent threads for maximum speed."""
        max_workers = self.max_workers_var.get()
        completed_count = 0
        completed_lock = Lock()
        
        # Increase max workers for each endpoint to truly parallelize
        actual_workers = max_workers * len(selected_endpoints) if len(selected_endpoints) > 1 else max_workers
        actual_workers = min(actual_workers, 50)  # Cap at 50 total workers
        
        self.logger.info(f"Concurrent processing started with {actual_workers} workers")
        self.logger.info(f"Processing {total_addresses} addresses with {len(selected_endpoints)} endpoints each")
        self.logger.info(f"Total API calls to make: {total_addresses * len(selected_endpoints)}")
        
        self.results_queue.put(('progress', 0, f"Starting concurrent processing with {actual_workers} threads..."))
        
        def process_single_endpoint(params):
            """Process a single endpoint for a single address."""
            address, asset, endpoint = params
            endpoint_result = {}
            
            self.logger.debug(f"Processing {endpoint} for {address[:20]}... ({asset})")
            api_start_time = time.time()
            
            try:
                if endpoint == 'cluster_info':
                    data = self.api_service.get_cluster_name_and_category(address, asset)
                    if 'items' in data and len(data['items']) > 0:
                        item = data['items'][0]
                        endpoint_result['cluster_name'] = item.get('name', 'N/A')
                        endpoint_result['cluster_category'] = item.get('category', 'N/A')
                        endpoint_result['cluster_root_address'] = item.get('rootAddress', 'N/A')
                        
                elif endpoint == 'cluster_balance':
                    data = self.api_service.get_cluster_balance(address, asset, output_currency)
                    endpoint_result['balance'] = data.get('balance', 0)
                    endpoint_result['total_received'] = data.get('totalReceivedAmount', 0)
                    endpoint_result['total_sent'] = data.get('totalSentAmount', 0)
                    endpoint_result['address_count'] = data.get('addressCount', 0)
                    endpoint_result['transfer_count'] = data.get('transferCount', 0)
                    endpoint_result['deposit_count'] = data.get('depositCount', 0)
                    endpoint_result['withdrawal_count'] = data.get('withdrawalCount', 0)
                    endpoint_result['total_fees'] = data.get('totalFeesAmount', 0)
                    endpoint_result['root_address'] = data.get('rootAddress', 'N/A')
                    
                elif endpoint == 'cluster_addresses':
                    data = self.api_service.get_cluster_addresses(address, asset, {'limit': 10})
                    if 'items' in data:
                        endpoint_result['cluster_addresses'] = [addr['address'] for addr in data['items'][:5]]
                        
                elif endpoint == 'cluster_transactions':
                    data = self.api_service.get_cluster_transactions(address, asset, {'limit': 10})
                    if 'items' in data:
                        endpoint_result['recent_transactions'] = [tx['transactionHash'] for tx in data['items'][:5]]
                        
                elif endpoint == 'cluster_counterparties':
                    data = self.api_service.get_cluster_counterparties(address, asset, output_currency, {'limit': 10})
                    if 'items' in data:
                        endpoint_result['counterparties'] = []
                        for cp in data['items'][:5]:
                            endpoint_result['counterparties'].append({
                                'name': cp.get('name', 'Unknown'),
                                'category': cp.get('category', 'N/A'),
                                'sent': cp.get('sentAmount', 0),
                                'received': cp.get('receivedAmount', 0)
                            })
                        
                elif endpoint == 'exposure_category':
                    data = self.api_service.get_exposure_by_category(address, asset, 'sent', output_currency)
                    if 'directExposure' in data:
                        endpoint_result['exposure_categories'] = data['directExposure'].get('categories', [])
                        
                elif endpoint == 'exposure_service':
                    data = self.api_service.get_exposure_by_service(address, asset, 'sent', output_currency)
                    if 'directExposure' in data:
                        endpoint_result['exposure_services'] = data['directExposure'].get('services', [])
                
                api_time = time.time() - api_start_time
                self.logger.debug(f"✓ {endpoint} for {address[:20]}... completed in {api_time:.2f}s")
                
            except Exception as e:
                error_msg = str(e)
                self.logger.warning(f"✗ {endpoint} for {address[:20]}... failed: {error_msg}")
                
                if '503' in error_msg:
                    endpoint_result[f'{endpoint}_error'] = 'Service temporarily unavailable'
                elif '404' in error_msg:
                    endpoint_result[f'{endpoint}_error'] = 'Address not found'
                elif '400' in error_msg:
                    endpoint_result[f'{endpoint}_error'] = 'Invalid request'
                elif '403' in error_msg:
                    endpoint_result[f'{endpoint}_error'] = 'Invalid API key'
                else:
                    endpoint_result[f'{endpoint}_error'] = error_msg[:50]
            
            return address, endpoint, endpoint_result
        
        # Create all tasks (address + endpoint combinations)
        all_tasks = []
        for idx, row in self.addresses_df.iterrows():
            address = row['address']
            asset = row['asset']
            for endpoint in selected_endpoints:
                all_tasks.append((address, asset, endpoint))
        
        self.logger.info(f"Created {len(all_tasks)} total tasks")
        
        # Process all endpoint calls concurrently
        results_dict = {}  # Store results by address
        total_tasks = len(all_tasks)
        completed_tasks = 0
        
        with ThreadPoolExecutor(max_workers=actual_workers) as executor:
            self.logger.info("ThreadPoolExecutor created, submitting tasks...")
            
            # Submit all tasks
            futures = {executor.submit(process_single_endpoint, task): task for task in all_tasks}
            self.logger.info(f"All {len(futures)} tasks submitted")
            
            # Collect results as they complete
            for future in as_completed(futures):
                if not self.is_processing:
                    self.logger.info("Processing stopped by user")
                    executor.shutdown(wait=False)
                    break
                    
                try:
                    address, endpoint, endpoint_result = future.result()
                    
                    # Aggregate results by address
                    if address not in results_dict:
                        results_dict[address] = {
                            'address': address,
                            'asset': futures[future][1],  # Get asset from original task
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                    
                    results_dict[address].update(endpoint_result)
                    
                    # Update progress
                    completed_tasks += 1
                    if completed_tasks % 10 == 0:  # Update every 10 tasks to reduce GUI overhead
                        progress = (completed_tasks / total_tasks) * 100
                        self.logger.info(f"Progress: {completed_tasks}/{total_tasks} API calls completed ({progress:.1f}%)")
                        self.results_queue.put(('progress', progress, f"Processed {completed_tasks}/{total_tasks} API calls"))
                    
                    # Send complete address results when all endpoints are done for that address
                    address_tasks = [t for t in all_tasks if t[0] == address]
                    address_completed = sum(1 for t in address_tasks if any(
                        futures[f] == (t[0], t[1], t[2]) and f.done() for f in futures
                    ))
                    
                    if address_completed == len(selected_endpoints):
                        self.results_queue.put(('result', results_dict[address]))
                        with completed_lock:
                            completed_count += 1
                        self.logger.debug(f"Address {address[:20]}... completed ({completed_count}/{total_addresses})")
                        
                except Exception as e:
                    self.logger.error(f"Error processing task: {e}", exc_info=True)
        
        # Calculate and display performance metrics
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            addresses_per_second = total_addresses / elapsed_time
            calls_per_second = total_tasks / elapsed_time
            sequential_estimate = total_tasks * 0.5  # Estimate 0.5s per API call
            speedup = sequential_estimate / elapsed_time
            
            perf_msg = f"Completed {total_addresses} addresses ({total_tasks} API calls) in {elapsed_time:.1f}s\n"
            perf_msg += f"Performance: {addresses_per_second:.1f} addresses/sec, {calls_per_second:.1f} API calls/sec\n"
            perf_msg += f"Estimated {speedup:.1f}x faster than sequential!"
            
            self.logger.info("="*80)
            self.logger.info("PROCESSING COMPLETE - PERFORMANCE METRICS")
            self.logger.info("="*80)
            self.logger.info(f"Total time: {elapsed_time:.1f} seconds")
            self.logger.info(f"Addresses processed: {total_addresses}")
            self.logger.info(f"API calls made: {total_tasks}")
            self.logger.info(f"Addresses per second: {addresses_per_second:.1f}")
            self.logger.info(f"API calls per second: {calls_per_second:.1f}")
            self.logger.info(f"Speedup vs sequential: {speedup:.1f}x")
            self.logger.info("="*80)
            
            self.results_queue.put(('progress', 100, perf_msg))
        
        self.results_queue.put(('complete', None))
    
    def process_addresses_sequential(self, total_addresses, output_currency, selected_endpoints, start_time):
        """Legacy sequential processing mode."""
        for i, row in self.addresses_df.iterrows():
            if not self.is_processing:
                break
                
            address = row['address']
            asset = row['asset']
            
            # Update progress
            progress = (i + 1) / total_addresses * 100
            self.results_queue.put(('progress', progress, f"Processing {i+1}/{total_addresses}: {address[:20]}..."))
            
            result = {
                'address': address,
                'asset': asset,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Process each selected endpoint (same logic as concurrent version)
            for endpoint in selected_endpoints:
                if not self.is_processing:
                    break
                    
                try:
                    if endpoint == 'cluster_info':
                        data = self.api_service.get_cluster_name_and_category(address, asset)
                        if 'items' in data and len(data['items']) > 0:
                            item = data['items'][0]
                            result['cluster_name'] = item.get('name', 'N/A')
                            result['cluster_category'] = item.get('category', 'N/A')
                            result['cluster_root_address'] = item.get('rootAddress', 'N/A')
                            
                    elif endpoint == 'cluster_balance':
                        data = self.api_service.get_cluster_balance(address, asset, output_currency)
                        result['balance'] = data.get('balance', 0)
                        result['total_received'] = data.get('totalReceivedAmount', 0)
                        result['total_sent'] = data.get('totalSentAmount', 0)
                        result['address_count'] = data.get('addressCount', 0)
                        result['transfer_count'] = data.get('transferCount', 0)
                        result['deposit_count'] = data.get('depositCount', 0)
                        result['withdrawal_count'] = data.get('withdrawalCount', 0)
                        result['total_fees'] = data.get('totalFeesAmount', 0)
                        result['root_address'] = data.get('rootAddress', 'N/A')
                        
                    # ... (other endpoints same as concurrent version)
                        
                except Exception as e:
                    error_msg = str(e)
                    result[f'{endpoint}_error'] = error_msg[:50]
            
            # Add result to queue
            self.results_queue.put(('result', result))
            
            # Small delay to prevent overwhelming the API
            if i < total_addresses - 1:
                time.sleep(0.1)
        
        # Show completion time
        elapsed_time = time.time() - start_time
        self.results_queue.put(('progress', 100, f"Completed in {elapsed_time:.1f}s (sequential mode)"))
        self.results_queue.put(('complete', None))
            
    def check_queue(self):
        try:
            while True:
                msg_type, data, *extra = self.results_queue.get_nowait()
                
                if msg_type == 'progress':
                    self.progress_var.set(data)
                    self.progress_label.config(text=extra[0] if extra else "")
                    
                elif msg_type == 'result':
                    self.results.append(data)
                    self.add_result_to_table(data)
                    
                    # Update asset filter options
                    current_assets = list(self.asset_filter_combo['values'])
                    if data['asset'] not in current_assets and data['asset'] != 'All':
                        current_assets.append(data['asset'])
                        self.asset_filter_combo['values'] = sorted(current_assets)
                    
                elif msg_type == 'complete':
                    self.processing_complete()
                    return
                    
                elif msg_type == 'error':
                    messagebox.showerror("Processing Error", f"An error occurred: {data}")
                    self.processing_complete()
                    return
                    
        except queue.Empty:
            pass
            
        if self.is_processing:
            self.parent.after(50, self.check_queue)  # Reduced from 100ms to 50ms
    
    def add_result_to_table(self, result):
        """Add a result to the table."""
        # Determine if this is a success or error
        has_error = any(key.endswith('_error') for key in result)
        status = "Error" if has_error else "Success"
        tags = ('error',) if has_error else ('success',)
        
        # Extract key values
        balance = result.get('balance', 0)
        received = result.get('total_received', 0)
        sent = result.get('total_sent', 0)
        transfers = result.get('transfer_count', 0)
        
        # Format details
        details = []
        if has_error:
            for key, value in result.items():
                if key.endswith('_error'):
                    details.append(f"{key}: {value[:50]}...")
        else:
            if 'cluster_name' in result and result['cluster_name']:
                details.append(f"Cluster: {result['cluster_name']}")
            if 'cluster_category' in result and result['cluster_category']:
                details.append(f"Category: {result['cluster_category']}")
        
        details_str = "; ".join(details) if details else "Click for details"
        
        # Format numbers
        balance_str = f"{balance:,.8f}" if isinstance(balance, (int, float)) else str(balance)
        received_str = f"{received:,.8f}" if isinstance(received, (int, float)) else str(received)
        sent_str = f"{sent:,.8f}" if isinstance(sent, (int, float)) else str(sent)
        transfers_str = f"{transfers:,}" if isinstance(transfers, (int, float)) else str(transfers)
        
        # Add to tree
        self.results_tree.insert('', 'end', 
                                text=result['address'],
                                values=(result['asset'], balance_str, received_str, 
                                       sent_str, transfers_str, status, details_str),
                                tags=tags)
    
    def update_summary(self, displayed_count=None):
        """Update the summary label."""
        if displayed_count is None:
            displayed_count = len(self.results_tree.get_children())
        
        total_count = len(self.results)
        
        # Calculate totals
        total_balance = 0
        success_count = 0
        error_count = 0
        
        for result in self.results:
            has_error = any(key.endswith('_error') for key in result)
            if has_error:
                error_count += 1
            else:
                success_count += 1
                if 'balance' in result and isinstance(result['balance'], (int, float)):
                    total_balance += result['balance']
        
        summary = f"Showing {displayed_count} of {total_count} results | "
        summary += f"Success: {success_count} | Errors: {error_count}"
        if total_balance > 0:
            summary += f" | Total Balance: {total_balance:,.8f}"
        
        self.summary_label.config(text=summary)
            
    def processing_complete(self):
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.NORMAL if self.results else tk.DISABLED)
        
        # Don't overwrite performance message
        if "faster than sequential" not in self.progress_label.cget("text"):
            self.progress_label.config(text="Processing complete!")
        self.progress_var.set(100)
        
        # Update final summary
        self.update_summary()
        
        # Show completion message
        if self.results:
            success_count = sum(1 for r in self.results if not any(k.endswith('_error') for k in r))
            error_count = len(self.results) - success_count
            
            msg = f"Processing complete!\n\n"
            msg += f"Total processed: {len(self.results)}\n"
            msg += f"Successful: {success_count}\n"
            msg += f"Errors: {error_count}\n\n"
            
            # Add performance note if in fast mode
            if self.fast_mode_var.get():
                msg += f"Used {self.max_workers_var.get()} concurrent threads for faster processing.\n\n"
            
            msg += "Double-click any row to see detailed information."
            
            messagebox.showinfo("Processing Complete", msg)
            
    def export_results(self):
        if not self.results:
            messagebox.showwarning("No Results", "No results to export.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json")
            ]
        )
        
        if filename:
            try:
                if filename.endswith('.xlsx'):
                    df = pd.DataFrame(self.results)
                    df.to_excel(filename, index=False)
                elif filename.endswith('.csv'):
                    df = pd.DataFrame(self.results)
                    df.to_csv(filename, index=False)
                elif filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.results, f, indent=2)
                        
                messagebox.showinfo("Export Complete", f"Results exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def on_hover(self, event):
        """Handle mouse hover over tree items."""
        item = self.results_tree.identify('item', event.x, event.y)
        if item and item != self.last_hovered:
            # Remove hover from last item
            if self.last_hovered:
                tags = list(self.results_tree.item(self.last_hovered, 'tags'))
                if 'hover' in tags:
                    tags.remove('hover')
                    self.results_tree.item(self.last_hovered, tags=tags)
            
            # Add hover to current item
            tags = list(self.results_tree.item(item, 'tags'))
            if 'hover' not in tags:
                tags.append('hover')
                self.results_tree.item(item, tags=tags)
            
            self.last_hovered = item
    
    def on_leave(self, event):
        """Handle mouse leaving the tree widget."""
        if self.last_hovered:
            tags = list(self.results_tree.item(self.last_hovered, 'tags'))
            if 'hover' in tags:
                tags.remove('hover')
                self.results_tree.item(self.last_hovered, tags=tags)
            self.last_hovered = None
    
    def on_row_double_click(self, event):
        """Handle double-click on a row to show detailed information."""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            address = self.results_tree.item(item, 'text')
            
            # Find the full result data
            for result in self.results:
                if result['address'] == address:
                    self.show_detailed_info(result)
                    break
    
    def show_detailed_info(self, result):
        """Show detailed information in a popup window."""
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Details for {result['address']}")
        detail_window.geometry("600x400")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(detail_window, padding="10")
        text_frame.pack(fill='both', expand=True)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=70, height=20)
        text_widget.pack(fill='both', expand=True)
        
        # Format and display all data
        text_widget.insert(tk.END, f"Address: {result['address']}\n")
        text_widget.insert(tk.END, f"Asset: {result['asset']}\n")
        text_widget.insert(tk.END, f"Timestamp: {result['timestamp']}\n")
        text_widget.insert(tk.END, "-" * 50 + "\n\n")
        
        for key, value in sorted(result.items()):
            if key not in ['address', 'asset', 'timestamp']:
                if isinstance(value, list):
                    text_widget.insert(tk.END, f"{key}:\n")
                    for item in value:
                        text_widget.insert(tk.END, f"  - {item}\n")
                else:
                    text_widget.insert(tk.END, f"{key}: {value}\n")
        
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(detail_window, text="Close", command=detail_window.destroy).pack(pady=10)
    
    def apply_asset_filter(self, event=None):
        """Apply asset filter to the results table."""
        self.filter_results()
    
    def apply_search_filter(self, event=None):
        """Apply search filter to the results table."""
        self.filter_results()
    
    def clear_filters(self):
        """Clear all filters."""
        self.asset_filter_var.set("All")
        self.search_var.set("")
        self.filter_results()
    
    def filter_results(self):
        """Filter results based on current filter settings."""
        # Clear current display
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        asset_filter = self.asset_filter_var.get()
        search_term = self.search_var.get().lower()
        
        # Apply filters and re-display
        displayed_count = 0
        for result in self.results:
            # Check asset filter
            if asset_filter != "All" and result.get('asset', '') != asset_filter:
                continue
            
            # Check search filter
            if search_term:
                found = False
                for key, value in result.items():
                    if search_term in str(value).lower():
                        found = True
                        break
                if not found:
                    continue
            
            # Add to table
            self.add_result_to_table(result)
            displayed_count += 1
        
        # Update summary
        self.update_summary(displayed_count)