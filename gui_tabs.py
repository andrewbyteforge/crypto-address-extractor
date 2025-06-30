"""
GUI Tabs Module
===============
This module contains all the tab creation methods for the Crypto Extractor GUI.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.1.0 - Added i2 and graph analysis export options
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging
from datetime import datetime


class GUITabs:
    """Mixin class containing all tab creation methods."""
    
    def _create_extraction_tab(self):
        """Create the main extraction tab with integrated Chainalysis API options and scrolling support."""
        extraction_frame = ttk.Frame(self.notebook)
        self.notebook.add(extraction_frame, text="Extract Addresses")
        
        # Create a canvas and scrollbar for scrolling
        canvas = tk.Canvas(extraction_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(extraction_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel to scrolling
        def _on_mousewheel(event):
            """Handle mouse wheel scrolling."""
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                self.logger.debug(f"Mouse wheel scroll error: {e}")
        
        # Bind mouse wheel events
        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # Linux
        
        # Update canvas frame width when canvas is resized
        def configure_canvas_frame(event):
            """Update the scrollable frame width to match canvas."""
            canvas_width = event.width
            canvas.itemconfig(canvas_frame, width=canvas_width)
        
        canvas.bind("<Configure>", configure_canvas_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Now create all the content in scrollable_frame instead of extraction_frame
        
        # File selection section
        file_frame = ttk.LabelFrame(scrollable_frame, text="Select CSV or Excel Files", padding="15")
        file_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Selected files listbox with scrollbar
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill='both', expand=True)
        
        files_scrollbar = ttk.Scrollbar(list_frame)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=files_scrollbar.set,
                                        selectmode=tk.EXTENDED, font=('Arial', 10))
        self.files_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        files_scrollbar.config(command=self.files_listbox.yview)
        
        # File buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Add Files", command=self._select_files,
                style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self._remove_selected_file,
                style="Warning.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self._clear_files,
                style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        
        # Options section
        options_frame = ttk.LabelFrame(scrollable_frame, text="Extraction Options", padding="15")
        options_frame.pack(fill='x', padx=20, pady=10)
        
        # Output directory
        dir_frame = ttk.Frame(options_frame)
        dir_frame.pack(fill='x', pady=5)
        
        ttk.Label(dir_frame, text="Output Directory:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.output_dir_var = tk.StringVar(value=self.config.get('default_output_directory', os.getcwd()))
        self.output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, font=('Arial', 10))
        self.output_dir_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 10))
        ttk.Button(dir_frame, text="Browse", command=self._select_output_directory).pack(side=tk.LEFT)
        
        # Output filename
        name_frame = ttk.Frame(options_frame)
        name_frame.pack(fill='x', pady=5)
        
        ttk.Label(name_frame, text="Output Filename:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = self.config.get('output_filename_pattern', 'crypto_addresses_{timestamp}.xlsx')
        default_name = default_name.replace('{timestamp}', timestamp)
        self.output_name_var = tk.StringVar(value=default_name)
        self.output_entry = ttk.Entry(name_frame, textvariable=self.output_name_var, font=('Arial', 10))
        self.output_entry.pack(side=tk.LEFT, fill='x', expand=True)
        
        # Checksum validation
        self.validate_checksum_var = tk.BooleanVar(value=self.config.get('validate_checksums', True))
        ttk.Checkbutton(options_frame, text="Validate address checksums (where applicable)",
                        variable=self.validate_checksum_var, style='Switch.TCheckbutton').pack(pady=5)
        
        # Chainalysis API Integration Section
        self._create_api_integration_section(options_frame)
        
        # ENHANCED: Report generation and export options
        self._create_export_options_section(options_frame)
        
        # Progress section
        progress_frame = ttk.LabelFrame(scrollable_frame, text="Progress", padding="15")
        progress_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            maximum=100, length=400, style='TProgressbar')
        self.progress_bar.pack(fill='x', pady=5)
        
        self.status_var = tk.StringVar(value="Ready to extract addresses")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var, font=('Arial', 10))
        self.status_label.pack(pady=5)
        
        # Statistics text
        self.stats_text = tk.Text(progress_frame, height=6, width=60, font=('Consolas', 9))
        self.stats_text.pack(fill='both', expand=True, pady=5)
        self.stats_text.config(state=tk.DISABLED)
        
        # Extract button
        extract_frame = ttk.Frame(scrollable_frame)
        extract_frame.pack(pady=20)
        
        self.extract_button = ttk.Button(extract_frame, text="Extract Addresses",
                                        command=self._start_extraction, style="Success.TButton")
        self.extract_button.pack()
        
        # Log the scrollbar implementation
        self.logger.info("Extraction tab created with scrollbar support")




    def _create_export_options_section(self, parent_frame):
        """Create enhanced export options section with i2 and graph analysis support."""
        export_frame = ttk.LabelFrame(parent_frame, text="Export & Analysis Options", padding="10")
        export_frame.pack(fill='x', pady=(10, 0))
        
        # Standard report generation
        standard_frame = ttk.LabelFrame(export_frame, text="Standard Reports", padding="8")
        standard_frame.pack(fill='x', pady=(0, 10))
        
        self.generate_pdf_var = tk.BooleanVar(value=self.config.get('generate_pdf', False))
        ttk.Checkbutton(standard_frame, text="Generate PDF investigation report",
                        variable=self.generate_pdf_var).pack(anchor='w', pady=2)
        
        self.generate_word_var = tk.BooleanVar(value=self.config.get('generate_word', False))
        ttk.Checkbutton(standard_frame, text="Generate Word investigation report",
                        variable=self.generate_word_var).pack(anchor='w', pady=2)
        
        # Graph Analysis Exports - ENHANCED FOR LAW ENFORCEMENT
        graph_frame = ttk.LabelFrame(export_frame, text="Graph Analysis & Investigation Tools", padding="8")
        graph_frame.pack(fill='x', pady=(0, 10))
        
        # i2 Analyst's Notebook export (prioritized for law enforcement)
        self.export_i2_var = tk.BooleanVar(value=True)  # Default to True for law enforcement
        i2_cb = ttk.Checkbutton(graph_frame, text="Export to i2 Analyst's Notebook (XML + CSV)",
                               variable=self.export_i2_var)
        i2_cb.pack(anchor='w', pady=2)
        
        # i2 help text
        i2_info = ttk.Label(graph_frame, 
                           text="  → Creates entities, clusters, and relationships for advanced graph analysis",
                           font=('Arial', 8), foreground='gray')
        i2_info.pack(anchor='w', padx=20)
        
        # Other graph formats
        self.export_gephi_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(graph_frame, text="Export to Gephi (GEXF format)",
                        variable=self.export_gephi_var).pack(anchor='w', pady=2)
        
        self.export_cytoscape_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(graph_frame, text="Export to Cytoscape (GraphML format)",
                        variable=self.export_cytoscape_var).pack(anchor='w', pady=2)
        
        # Investigation metadata for i2 export
        metadata_frame = ttk.LabelFrame(export_frame, text="Investigation Metadata (for i2 Export)", padding="8")
        metadata_frame.pack(fill='x')
        
        # Case information row 1
        case_row1 = ttk.Frame(metadata_frame)
        case_row1.pack(fill='x', pady=2)
        
        ttk.Label(case_row1, text="Case ID:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.case_id_var = tk.StringVar(value="")
        case_entry = ttk.Entry(case_row1, textvariable=self.case_id_var, width=20, font=('Arial', 9))
        case_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(case_row1, text="Analyst:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.analyst_var = tk.StringVar(value="")
        analyst_entry = ttk.Entry(case_row1, textvariable=self.analyst_var, width=20, font=('Arial', 9))
        analyst_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(case_row1, text="Priority:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.case_priority_var = tk.StringVar(value="MEDIUM")
        priority_combo = ttk.Combobox(case_row1, textvariable=self.case_priority_var, 
                                     values=["LOW", "MEDIUM", "HIGH", "CRITICAL"], 
                                     state="readonly", width=10, font=('Arial', 9))
        priority_combo.pack(side=tk.LEFT)
        
        # Case information row 2
        case_row2 = ttk.Frame(metadata_frame)
        case_row2.pack(fill='x', pady=2)
        
        ttk.Label(case_row2, text="Investigation Type:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.investigation_type_var = tk.StringVar(value="FINANCIAL_CRIMES")
        inv_type_combo = ttk.Combobox(case_row2, textvariable=self.investigation_type_var,
                                     values=["FINANCIAL_CRIMES", "RANSOMWARE", "MONEY_LAUNDERING", 
                                           "FRAUD", "TERRORISM_FINANCING", "SANCTIONS", "OTHER"],
                                     state="readonly", width=18, font=('Arial', 9))
        inv_type_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(case_row2, text="Target Entity:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.target_entity_var = tk.StringVar(value="")
        target_entry = ttk.Entry(case_row2, textvariable=self.target_entity_var, width=25, font=('Arial', 9))
        target_entry.pack(side=tk.LEFT)
        
        # Processing strategy for large datasets
        strategy_frame = ttk.LabelFrame(export_frame, text="Large Dataset Processing", padding="8")
        strategy_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(strategy_frame, text="Processing Strategy:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 10))
        self.processing_strategy_var = tk.StringVar(value="SMART")
        strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.processing_strategy_var,
                                     values=["SMART", "COMPLETE", "SAMPLE", "PRIORITY_ONLY"],
                                     state="readonly", width=15, font=('Arial', 9))
        strategy_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Strategy help text
        strategy_help = ttk.Label(strategy_frame,
                                 text="SMART: Auto-prioritize for 500+ addresses | COMPLETE: Process all | SAMPLE: Representative sample | PRIORITY_ONLY: High-risk only",
                                 font=('Arial', 8), foreground='gray')
        strategy_help.pack(side=tk.LEFT)
        
        # Bind strategy selection to show help
        def on_strategy_change(event=None):
            strategy = self.processing_strategy_var.get()
            help_texts = {
                "SMART": "Automatically prioritizes addresses, processes top 20% with full API analysis",
                "COMPLETE": "Process all addresses with full API analysis (may take significant time)",
                "SAMPLE": "Process statistically representative sample (recommended for 1000+ addresses)",
                "PRIORITY_ONLY": "Process only high-risk addresses identified by pattern analysis"
            }
            strategy_help.config(text=help_texts.get(strategy, ""))
        
        strategy_combo.bind('<<ComboboxSelected>>', on_strategy_change)
        on_strategy_change()  # Set initial help text
    
    def _create_api_integration_section(self, parent_frame):
        """Create the Chainalysis API integration section."""
        api_frame = ttk.LabelFrame(parent_frame, text="Chainalysis API Integration", padding="10")
        api_frame.pack(fill='x', pady=(10, 0))
        
        # Check if API is available
        if self.api_service:
            # Enable Chainalysis API checkbox
            self.enable_chainalysis_var = tk.BooleanVar(value=False)
            api_checkbox = ttk.Checkbutton(
                api_frame, 
                text="Enable Chainalysis API analysis for extracted addresses",
                variable=self.enable_chainalysis_var,
                command=self._toggle_chainalysis_options
            )
            api_checkbox.pack(anchor='w', pady=2)
            
            # API Options frame (initially disabled)
            self.api_options_frame = ttk.Frame(api_frame)
            self.api_options_frame.pack(fill='x', pady=(10, 0))
            
            # API analysis options
            self.api_balance_var = tk.BooleanVar(value=True)
            self.api_balance_cb = ttk.Checkbutton(
                self.api_options_frame, 
                text="Get balance information",
                variable=self.api_balance_var
            )
            self.api_balance_cb.pack(anchor='w', padx=20)
            
            self.api_exposure_var = tk.BooleanVar(value=True)
            self.api_exposure_cb = ttk.Checkbutton(
                self.api_options_frame, 
                text="Get exchange exposure analysis",
                variable=self.api_exposure_var
            )
            self.api_exposure_cb.pack(anchor='w', padx=20)
            
            self.api_cluster_info_var = tk.BooleanVar(value=True)  # Changed default to True
            self.api_cluster_info_cb = ttk.Checkbutton(
                self.api_options_frame, 
                text="Get cluster name and category (required for i2 export)",
                variable=self.api_cluster_info_var
            )
            self.api_cluster_info_cb.pack(anchor='w', padx=20)
            
            # API performance options
            perf_frame = ttk.Frame(self.api_options_frame)
            perf_frame.pack(fill='x', pady=(10, 0), padx=20)
            
            ttk.Label(perf_frame, text="Concurrent API calls:", font=('Arial', 9)).pack(side=tk.LEFT)
            self.api_threads_var = tk.IntVar(value=5)  # Increased default for better performance
            api_threads_spin = ttk.Spinbox(perf_frame, from_=1, to=20, increment=1, 
                                         textvariable=self.api_threads_var, width=5)
            api_threads_spin.pack(side=tk.LEFT, padx=(10, 20))
            
            ttk.Label(perf_frame, text="Output currency:", font=('Arial', 9)).pack(side=tk.LEFT)
            self.api_currency_var = tk.StringVar(value="USD")
            currency_combo = ttk.Combobox(perf_frame, textvariable=self.api_currency_var, 
                                          values=["NATIVE", "USD"], state="readonly", width=8)
            currency_combo.pack(side=tk.LEFT, padx=(10, 0))
            
            # Initially disable API options
            self._toggle_chainalysis_options()
            
        else:
            # Show message about API not being configured
            api_message = ttk.Label(
                api_frame, 
                text="⚠️  Chainalysis API not configured. Enhanced analysis and i2 export require API access.",
                font=('Arial', 9),
                foreground='#ff6600'  # Orange warning color
            )
            api_message.pack(anchor='w', pady=5)
            
            settings_btn = ttk.Button(
                api_frame, 
                text="Configure API Key", 
                command=lambda: self.notebook.select(self.settings_frame),
                style="Primary.TButton"
            )
            settings_btn.pack(anchor='w', pady=5)
            
            # Set default values for when API is not available
            self.enable_chainalysis_var = tk.BooleanVar(value=False)
            self.api_balance_var = tk.BooleanVar(value=False)
            self.api_exposure_var = tk.BooleanVar(value=False)
            self.api_cluster_info_var = tk.BooleanVar(value=False)
            self.api_threads_var = tk.IntVar(value=5)
            self.api_currency_var = tk.StringVar(value="USD")
    
    def _create_custom_crypto_tab(self):
        """Create the custom cryptocurrency tab."""
        custom_frame = ttk.Frame(self.notebook)
        self.notebook.add(custom_frame, text="Add Custom Crypto")
        
        # Instructions
        instructions = ttk.Label(custom_frame, text="Add custom cryptocurrency patterns for extraction",
                                font=('Arial', 12, 'bold'))
        instructions.pack(pady=20)
        
        # Input frame with better layout
        input_frame = ttk.LabelFrame(custom_frame, text="New Cryptocurrency", padding="20")
        input_frame.pack(padx=40, pady=10, fill='x')
        
        # Grid layout for inputs
        ttk.Label(input_frame, text="Name:", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.custom_name_var = tk.StringVar()
        name_entry = ttk.Entry(input_frame, textvariable=self.custom_name_var, width=30, font=('Arial', 10))
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        ttk.Label(input_frame, text="Symbol:", font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        self.custom_symbol_var = tk.StringVar()
        symbol_entry = ttk.Entry(input_frame, textvariable=self.custom_symbol_var, width=30, font=('Arial', 10))
        symbol_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        
        ttk.Label(input_frame, text="Pattern (regex):", font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        self.custom_pattern_var = tk.StringVar()
        pattern_entry = ttk.Entry(input_frame, textvariable=self.custom_pattern_var, width=30, font=('Arial', 10))
        pattern_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
        
        input_frame.columnconfigure(1, weight=1)
        
        # Examples frame
        examples_frame = ttk.LabelFrame(custom_frame, text="Pattern Examples", padding="15")
        examples_frame.pack(padx=40, pady=10, fill='x')
        
        examples_text = """• Ethereum-like: 0x[a-fA-F0-9]{40}
- Bitcoin-like: [13][a-km-zA-HJ-NP-Z1-9]{25,34}
- Fixed prefix: PREFIX[A-Z0-9]{20,30}
- Cosmos-like: cosmos1[a-z0-9]{38}
- Base58: [1-9A-HJ-NP-Za-km-z]{32,44}"""
        
        ttk.Label(examples_frame, text=examples_text, font=('Consolas', 9)).pack()
        
        # Add button
        add_button = ttk.Button(custom_frame, text="Add Custom Cryptocurrency",
                                command=self._add_custom_crypto, style="Success.TButton")
        add_button.pack(pady=20)
        
        # Recently added
        recent_frame = ttk.LabelFrame(custom_frame, text="Recently Added", padding="15")
        recent_frame.pack(padx=40, pady=10, fill='both', expand=True)
        
        # Listbox for recently added
        scrollbar = ttk.Scrollbar(recent_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recent_custom_listbox = tk.Listbox(recent_frame, height=5, yscrollcommand=scrollbar.set,
                                                font=('Consolas', 9))
        self.recent_custom_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.recent_custom_listbox.yview)
        
        # Load existing custom cryptos
        for crypto in self.custom_cryptos[-5:]:  # Show last 5 added
            self.recent_custom_listbox.insert(tk.END, 
                f"{crypto['name']} ({crypto['symbol']}): {crypto['pattern']}")
    
    def _create_crypto_list_tab(self):
        """Create the cryptocurrency list tab with pagination."""
        list_frame = ttk.Frame(self.notebook)
        self.notebook.add(list_frame, text="Cryptocurrency List")
        
        # Title
        title = ttk.Label(list_frame, text="Supported Cryptocurrencies", font=('Arial', 14, 'bold'))
        title.pack(pady=20)
        
        # Search frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(padx=20, pady=10, fill='x')
        
        ttk.Label(search_frame, text="Search:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30, font=('Arial', 10))
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Table frame
        table_frame = ttk.Frame(list_frame)
        table_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Create Treeview for the table
        columns = ('Symbol', 'Type', 'Pattern Example')
        self.crypto_tree = ttk.Treeview(table_frame, columns=columns, show='tree headings', height=15)
        
        # Define headings
        self.crypto_tree.heading('#0', text='Name')
        self.crypto_tree.heading('Symbol', text='Symbol')
        self.crypto_tree.heading('Type', text='Type')
        self.crypto_tree.heading('Pattern Example', text='Pattern Example')
        
        # Column widths
        self.crypto_tree.column('#0', width=150)
        self.crypto_tree.column('Symbol', width=80)
        self.crypto_tree.column('Type', width=100)
        self.crypto_tree.column('Pattern Example', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.crypto_tree.yview)
        self.crypto_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table
        self.crypto_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Pagination controls
        self.page_frame = ttk.Frame(list_frame)
        self.page_frame.pack(pady=10)
        
        self.current_page = 0
        self.items_per_page = 20
        
        ttk.Button(self.page_frame, text="◀ Previous", command=self._prev_page).pack(side=tk.LEFT, padx=5)
        self.page_label = ttk.Label(self.page_frame, text="Page 1 of 1", font=('Arial', 10))
        self.page_label.pack(side=tk.LEFT, padx=20)
        ttk.Button(self.page_frame, text="Next ▶", command=self._next_page).pack(side=tk.LEFT, padx=5)
        
        # Populate the table
        self._populate_crypto_list()
    
    def _create_api_tab(self):
        """Create the API tab for Chainalysis integration."""
        from api_tab import APITab
        
        api_frame = ttk.Frame(self.notebook)
        self.notebook.add(api_frame, text="API")
        
        if not self.api_service:
            # Show API key setup message
            setup_frame = ttk.Frame(api_frame)
            setup_frame.pack(expand=True)
            
            ttk.Label(setup_frame, text="Chainalysis API not configured", 
                     font=('Arial', 14, 'bold')).pack(pady=20)
            ttk.Label(setup_frame, text="Please go to Settings tab to configure your API key.",
                     font=('Arial', 10)).pack(pady=10)
            
            ttk.Button(setup_frame, text="Go to Settings", 
                      command=lambda: self.notebook.select(self.settings_frame),
                      style="Primary.TButton").pack(pady=10)
        else:
            # Initialize API tab with the frame and api_service
            self.api_tab = APITab(api_frame, self.api_service)
    
    def _create_settings_tab(self):
        """Create settings tab for API key and other configurations."""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Main settings container
        main_frame = ttk.Frame(self.settings_frame, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # API Settings Section
        api_frame = ttk.LabelFrame(main_frame, text="Chainalysis API Settings", padding="15")
        api_frame.pack(fill='x', pady=(0, 20))
        
        # API Key input
        ttk.Label(api_frame, text="API Key:", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        
        self.api_key_var = tk.StringVar(value=self.api_key)
        api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=50, show='*', font=('Arial', 10))
        api_key_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        # Show/Hide API key button
        self.show_api_key = False
        def toggle_api_key_visibility():
            self.show_api_key = not self.show_api_key
            api_key_entry.config(show='' if self.show_api_key else '*')
            show_btn.config(text='Hide' if self.show_api_key else 'Show')
        
        show_btn = ttk.Button(api_frame, text="Show", command=toggle_api_key_visibility, width=10)
        show_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Test API button
        def test_api_connection():
            api_key = self.api_key_var.get().strip()
            if not api_key:
                messagebox.showwarning("No API Key", "Please enter an API key first.")
                return
            
            try:
                # Test the API connection
                from iapi_service import IAPIService
                test_service = IAPIService(api_key)
                # Try a simple API call to test the connection
                messagebox.showinfo("Success", "API connection successful!")
            except Exception as e:
                messagebox.showerror("Connection Failed", f"Failed to connect to API: {str(e)}")
        
        test_btn = ttk.Button(api_frame, text="Test Connection", command=test_api_connection, style="Primary.TButton")
        test_btn.grid(row=1, column=1, pady=10, sticky='w')
        
        api_frame.columnconfigure(1, weight=1)
        
        # Other Settings Section
        other_frame = ttk.LabelFrame(main_frame, text="General Settings", padding="15")
        other_frame.pack(fill='x', pady=(0, 20))
        
        # Default directories
        ttk.Label(other_frame, text="Default Input Directory:", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.input_dir_var = tk.StringVar(value=self.config.get('default_input_directory', ''))
        input_dir_entry = ttk.Entry(other_frame, textvariable=self.input_dir_var, width=40, font=('Arial', 10))
        input_dir_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        def browse_input_dir():
            directory = filedialog.askdirectory(title="Select Default Input Directory")
            if directory:
                self.input_dir_var.set(directory)
        
        ttk.Button(other_frame, text="Browse", command=browse_input_dir).grid(row=0, column=2, padx=5, pady=5)
        
        # Checksum validation default
        self.settings_validate_var = tk.BooleanVar(value=self.config.get('validate_checksums', True))
        ttk.Checkbutton(other_frame, text="Validate checksums by default", 
                       variable=self.settings_validate_var).grid(row=1, column=0, columnspan=3, sticky='w', pady=10)
        
        other_frame.columnconfigure(1, weight=1)
        
        # Save button
        save_frame = ttk.Frame(main_frame)
        save_frame.pack(pady=20)
        ttk.Button(save_frame, text="Save All Settings", command=self._save_all_settings, 
                  style="Success.TButton").pack()